"""PreToolUse hook: deny `git commit` when the target repository is on main.

Fails loudly: when the command looks like a commit but the hook cannot resolve
its branch, or the hook itself errors, it asks the user instead of allowing.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED = {"main", "master"}
SEPARATORS = set(";&|\n{}")
PREFIXES = {"!", "if", "then", "else", "elif", "while", "until", "do", "time", "command", "nohup", "exec", "sudo", "xargs", "env"}
LOOKS_LIKE_COMMIT = re.compile(r"\bgit\b.*\bcommit\b", re.DOTALL)
UNRESOLVED = "?"
VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}


def segments(command: str) -> list[list[str] | str]:
    """Split a shell command into simple commands.

    Separators are `;`, `&`, `|`, braces, and unquoted newlines. Subshell parentheses
    are kept as "(" and ")" markers so the caller can scope `cd`. Comments are dropped.
    """
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&{}\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    out: list[list[str] | str] = []
    current: list[str] = []
    in_comment = False

    def flush() -> None:
        nonlocal current
        if current:
            out.append(current)
        current = []

    for tok in lexer:
        if in_comment:
            if "\n" in tok:
                in_comment = False
                flush()
            continue
        if tok.startswith("#"):
            in_comment = True
            continue
        if set(tok) <= SEPARATORS | {"(", ")"}:
            for ch in tok:
                flush()
                if ch in "()":
                    out.append(ch)
            continue
        current.append(tok)
    flush()
    return out


def resolve(base: str, path: str) -> str:
    """Resolve `path` against `base`, with `~` expanded."""
    return os.path.normpath(os.path.join(base, os.path.expanduser(path)))


def cd_target(seg: list[str], cwd: str | None) -> tuple[bool, str | None]:
    """Return (is cd, new cwd). A new cwd of None means the target is unknown."""
    if seg[0] != "cd":
        return False, cwd
    args = [a for a in seg[1:] if not (a.startswith("-") and a != "-")]
    if not args:
        return True, os.path.expanduser("~")
    if args[0] == "-":
        return True, None
    target = os.path.expanduser(args[0])
    if os.path.isabs(target):
        return True, os.path.normpath(target)
    return True, resolve(cwd, target) if cwd else None


def git_call(seg: list[str]) -> tuple[dict[str, str], list[str], str] | None:
    """Return (env assignments, global options, subcommand) when `seg` runs git, else None."""
    env, i = {}, 0
    while i < len(seg):
        tok = seg[i]
        if "=" in tok and not tok.startswith("-") and tok.split("=", 1)[0].isidentifier():
            name, value = tok.split("=", 1)
            env[name] = value
        elif tok not in PREFIXES and not (tok.startswith("-") and i > 0 and seg[i - 1] in PREFIXES):
            break
        i += 1
    if i >= len(seg) or os.path.basename(seg[i]) != "git":
        return None
    opts, j = [], i + 1
    while j < len(seg) and seg[j].startswith("-"):
        if seg[j] in VALUE_OPTIONS and j + 1 < len(seg):
            opts += [seg[j], os.path.expanduser(seg[j + 1])]
            j += 2
        else:
            opts.append(seg[j])
            j += 1
    return (env, opts, seg[j]) if j < len(seg) else None


def has_git_commit(seg: list[str]) -> bool:
    """True when `seg` has a git token followed later by `commit`."""
    for i, tok in enumerate(seg):
        if os.path.basename(tok) == "git" and "commit" in seg[i + 1:]:
            return True
    return False


def commit_targets(command: str, cwd: str) -> list[tuple[str, dict[str, str], list[str]]]:
    """Return (working directory, env assignments, git global options) for each `git commit` in `command`.

    Follows `cd`, scoped to subshells. A working directory of UNRESOLVED means the hook
    cannot tell where a commit runs, for example after `cd -` or a segment it cannot parse.
    """
    try:
        items = segments(command)
    except ValueError:
        return [(UNRESOLVED, {}, [])] if LOOKS_LIKE_COMMIT.search(command) else []
    current: str | None = cwd
    stack: list[str | None] = []
    targets = []
    for item in items:
        if item == "(":
            stack.append(current)
            continue
        if item == ")":
            current = stack.pop() if stack else current
            continue
        is_cd, current = cd_target(item, current)
        if is_cd:
            continue
        call = git_call(item)
        if call and call[2] == "commit":
            targets.append((current or UNRESOLVED, call[0], call[1]))
        elif not call and has_git_commit(item):
            targets.append((UNRESOLVED, {}, []))
    return targets


def branch(cwd: str, env: dict[str, str], opts: list[str]) -> str | None:
    """Return the current branch that git sees with `env` and `opts` from `cwd`, or None."""
    try:
        out = subprocess.run(
            ["git", *opts, "branch", "--show-current"],
            cwd=cwd, env={**os.environ, **env}, capture_output=True, text=True,
        )
    except OSError:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def decide(command: str, cwd: str) -> tuple[str, str] | None:
    """Return (decision, reason) for `command`, or None to allow. Deny wins over ask."""
    unsure = None
    for target_cwd, env, opts in commit_targets(command, cwd):
        current = None if target_cwd == UNRESOLVED else branch(target_cwd, env, opts)
        if current in PROTECTED:
            return "deny", f"Commit on '{current}' is blocked. Create a branch first: git switch -c <short-name>."
        if current is None:
            unsure = "The hook could not tell which branch a git commit in this command targets. Check the branch before you allow it."
    return ("ask", unsure) if unsure else None


def respond(decision: str, reason: str) -> None:
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }, sys.stdout)


def main() -> None:
    try:
        event = json.load(sys.stdin)
        result = decide(event.get("tool_input", {}).get("command", ""), event.get("cwd", os.getcwd()))
    except Exception as e:  # noqa: BLE001 - any hook failure must reach the user
        result = ("ask", f"The commit hook failed ({type(e).__name__}: {e}). Check the branch before you allow this command.")
    if result:
        respond(*result)


if __name__ == "__main__":
    main()
