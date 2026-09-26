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
OPERATORS = {";", "&&", "||", "|", "&", "\n", "(", ")", "{", "}"}
PREFIXES = {"!", "if", "then", "else", "elif", "while", "until", "do", "time", "command", "nohup", "exec", "sudo", "xargs", "env"}
LOOKS_LIKE_COMMIT = re.compile(r"\bgit\b.*\bcommit\b", re.DOTALL)
VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}


def segments(command: str) -> list[list[str]]:
    """Split a shell command into simple commands at operators, braces, parentheses, and unquoted newlines."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&{}\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    out, current = [], []
    for tok in lexer:
        if tok in OPERATORS or set(tok) <= set(";&|\n"):
            out.append(current)
            current = []
        else:
            current.append(tok)
    out.append(current)
    return [seg for seg in out if seg]


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


def commit_targets(command: str, cwd: str) -> list[tuple[str, dict[str, str], list[str]]]:
    """Return (working directory, env assignments, git global options) for each `git commit` in `command`.

    Follows `cd`. When a `cd` target is unknown (for example `cd -`), checks the starting directory.
    """
    try:
        segs = segments(command)
    except ValueError:
        return []
    start, current, targets = cwd, cwd, []
    for seg in segs:
        is_cd, current = cd_target(seg, current)
        if is_cd:
            continue
        call = git_call(seg)
        if call and call[2] == "commit":
            targets.append((current or start, call[0], call[1]))
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
    """Return (decision, reason) for `command`, or None to allow."""
    targets = commit_targets(command, cwd)
    if not targets:
        if LOOKS_LIKE_COMMIT.search(command):
            return "ask", "The command looks like a git commit, but the hook could not parse it. Check the branch before you allow it."
        return None
    unknown = None
    for target_cwd, env, opts in targets:
        current = branch(target_cwd, env, opts)
        if current in PROTECTED:
            return "deny", f"Commit on '{current}' is blocked. Create a branch first: git switch -c <short-name>."
        if current is None:
            unknown = target_cwd
    if unknown:
        return "ask", f"The hook could not read the branch for a commit in {unknown}. Check the branch before you allow it."
    return None


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
