"""PreToolUse hook: deny `git commit` when the target repository is on main.

Fails loudly: when the command looks like a commit but the hook cannot resolve
its branch, or the hook itself errors, it asks the user instead of allowing.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

PROTECTED = {"main", "master"}
SHELLS = {"sh", "bash", "zsh", "dash", "eval"}
DENY_REASON = "Commit on '{branch}' is blocked. Create a branch first: git switch -c <short-name>."
PREFIXES = {"!", "if", "then", "else", "elif", "while", "until", "do", "time", "command", "nohup", "exec", "sudo", "xargs", "env"}
LOOKS_LIKE_COMMIT = re.compile(r"\bgit\b.*\bcommit\b", re.DOTALL)
UNRESOLVED = "?"
VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}


def lex(command: str) -> list[tuple[str, str]]:
    """Split `command` into ("word", text) and ("op", symbol) tokens.

    Quote-aware: `#`, parentheses, and operators count as syntax only when unquoted.
    Comments are dropped before their text is read. Raises ValueError on an unclosed quote.
    """
    tokens: list[tuple[str, str]] = []
    buf, in_word, i, n = [], False, 0, len(command)

    def end_word() -> None:
        nonlocal buf, in_word
        if in_word:
            word = "".join(buf)
            tokens.append(("op", word) if word in ("{", "}") else ("word", word))
        buf, in_word = [], False

    while i < n:
        ch = command[i]
        if ch in " \t\r":
            end_word()
        elif ch == "\n":
            end_word()
            tokens.append(("op", "\n"))
        elif ch == "#" and not in_word:
            while i < n and command[i] != "\n":
                i += 1
            continue
        elif ch == "\\":
            if i + 1 < n and command[i + 1] != "\n":
                buf.append(command[i + 1])
                in_word = True
            i += 2
            continue
        elif ch == "'":
            close = command.find("'", i + 1)
            if close < 0:
                raise ValueError("unclosed single quote")
            buf.append(command[i + 1:close])
            in_word, i = True, close + 1
            continue
        elif ch == '"':
            j = i + 1
            while j < n and command[j] != '"':
                if command[j] == "\\" and j + 1 < n:
                    j += 1
                buf.append(command[j])
                j += 1
            if j >= n:
                raise ValueError("unclosed double quote")
            in_word, i = True, j + 1
            continue
        elif ch == "&" and (command[i - 1:i] in ("<", ">") or command[i + 1:i + 2] == ">"):
            buf.append(ch)
            in_word = True
        elif ch in ";&|()`":
            end_word()
            pair = command[i:i + 2]
            if pair in ("&&", "||", ";;", "|&"):
                tokens.append(("op", pair))
                i += 2
                continue
            tokens.append(("op", ch))
        else:
            buf.append(ch)
            in_word = True
        i += 1
    end_word()
    return tokens


def segments(command: str) -> list[list[str] | str]:
    """Split a shell command into simple commands and scope markers.

    Returns word lists for simple commands, "(" and ")" for subshells, and "|" or "&"
    after a command that runs in its own subshell (a pipeline element or a background job).
    """
    out: list[list[str] | str] = []
    current: list[str] = []
    for kind, text in lex(command):
        if kind == "word":
            current.append(text)
            continue
        if current:
            out.append(current)
            current = []
        if text in ("(", ")", "|", "&"):
            out.append(text)
    if current:
        out.append(current)
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
    """True when `seg` may run a commit that git_call cannot resolve.

    Covers a git token followed later by `commit`, and a shell or eval whose
    argument text contains a git commit, such as `sh -c "git commit"`.
    """
    for i, tok in enumerate(seg):
        if os.path.basename(tok) == "git" and "commit" in seg[i + 1:]:
            return True
    runner = next((t for t in seg if t not in PREFIXES and "=" not in t), "")
    return os.path.basename(runner) in SHELLS and any(LOOKS_LIKE_COMMIT.search(t) for t in seg)


def commit_targets(command: str, cwd: str) -> list[tuple[str, dict[str, str], list[str]]]:
    """Return (working directory, env assignments, git global options) for each `git commit` in `command`.

    Follows `cd`, scoped to subshells, pipelines, and background jobs. A working directory
    of UNRESOLVED means the hook cannot tell where a commit runs.
    """
    try:
        items = segments(command)
    except ValueError:
        return [(UNRESOLVED, {}, [])] if LOOKS_LIKE_COMMIT.search(command) else []
    current: str | None = cwd
    before_cd: str | None = cwd
    last_was_cd = False
    stack: list[str | None] = []
    targets = []
    for item in items:
        if item == "(":
            stack.append(current)
        elif item == ")":
            current = stack.pop() if stack else current
        elif item in ("|", "&"):
            if last_was_cd:
                current = before_cd
        else:
            before_cd = current
            last_was_cd, current = cd_target(item, current)
            if last_was_cd:
                continue
            call = git_call(item)
            if call and call[2] == "commit":
                targets.append((current or UNRESOLVED, call[0], call[1]))
            elif not call and has_git_commit(item):
                targets.append((UNRESOLVED, {}, []))
            continue
        last_was_cd = False
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
            return "deny", DENY_REASON.format(branch=current)
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
