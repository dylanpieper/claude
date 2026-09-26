"""PreToolUse hook: deny `git commit` when the target repository is on main."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys

PROTECTED = {"main", "master"}


def commit_repo(command: str, cwd: str) -> str | None:
    """Return the repository path of a `git commit` call, or None if the command does not commit."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    for i, tok in enumerate(tokens):
        if tok != "git":
            continue
        repo, j = cwd, i + 1
        while j < len(tokens) and tokens[j].startswith("-"):
            if tokens[j] == "-C" and j + 1 < len(tokens):
                repo, j = tokens[j + 1], j + 2
            else:
                j += 1
        if j < len(tokens) and tokens[j] == "commit":
            return repo
    return None


def branch(repo: str) -> str | None:
    """Return the current branch of `repo`, or None outside a repository."""
    out = subprocess.run(
        ["git", "-C", repo, "branch", "--show-current"],
        capture_output=True, text=True,
    )
    return out.stdout.strip() if out.returncode == 0 else None


def main() -> None:
    event = json.load(sys.stdin)
    repo = commit_repo(event.get("tool_input", {}).get("command", ""), event.get("cwd", "."))
    current = branch(repo) if repo else None
    if current in PROTECTED:
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Commit on '{current}' is blocked. Create a branch first: git switch -c <short-name>.",
            }
        }, sys.stdout)


if __name__ == "__main__":
    main()
