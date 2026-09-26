"""PreToolUse hook: deny `git commit` when the target repository is on main."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys

PROTECTED = {"main", "master"}
OPERATORS = {";", "&&", "||", "|", "&"}
VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}


def segments(command: str) -> list[list[str]]:
    """Split a shell command into simple commands at `;`, `&&`, `||`, `|`, and `&`."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    out, current = [], []
    for tok in lexer:
        if tok in OPERATORS:
            out.append(current)
            current = []
        else:
            current.append(tok)
    out.append(current)
    return [seg for seg in out if seg]


def resolve(base: str, path: str) -> str:
    """Resolve `path` against `base`, with `~` expanded."""
    return os.path.normpath(os.path.join(base, os.path.expanduser(path)))


def git_call(seg: list[str]) -> tuple[list[str], str] | None:
    """Return (global options, subcommand) when `seg` runs git, else None."""
    i = 0
    while i < len(seg) and (seg[i] == "env" or ("=" in seg[i] and not seg[i].startswith("-"))):
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
    return (opts, seg[j]) if j < len(seg) else None


def commit_targets(command: str, cwd: str) -> list[tuple[str, list[str]]]:
    """Return (working directory, git global options) for each `git commit` in `command`.

    Follows `cd` so a commit after `cd <dir> &&` resolves against that directory.
    """
    try:
        segs = segments(command)
    except ValueError:
        return []
    targets = []
    for seg in segs:
        if seg[0] == "cd" and len(seg) > 1:
            cwd = resolve(cwd, seg[1])
            continue
        call = git_call(seg)
        if call and call[1] == "commit":
            targets.append((cwd, call[0]))
    return targets


def branch(cwd: str, opts: list[str]) -> str | None:
    """Return the current branch that git sees with `opts` from `cwd`, or None."""
    try:
        out = subprocess.run(
            ["git", *opts, "branch", "--show-current"],
            cwd=cwd, capture_output=True, text=True,
        )
    except OSError:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def main() -> None:
    event = json.load(sys.stdin)
    command = event.get("tool_input", {}).get("command", "")
    for cwd, opts in commit_targets(command, event.get("cwd", os.getcwd())):
        current = branch(cwd, opts)
        if current in PROTECTED:
            json.dump({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Commit on '{current}' is blocked. Create a branch first: git switch -c <short-name>.",
                }
            }, sys.stdout)
            return


if __name__ == "__main__":
    main()
