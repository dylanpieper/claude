"""End-to-end: Claude Code calls the hook and the hook stops a real commit.

Runs `claude -p` with only the hook loaded (no user settings or plugins).
It calls the model, so it runs only when CLAUDE_E2E=1.
"""

import json
import os
import shlex
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "block_main_commit.py"
DENY_REASON = "is blocked. Create a branch first"
# Keep the user's global git config (signing, hooksPath) out of the test.
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
PROMPT = "Run this exact Bash command once and do nothing else: git commit --allow-empty -m e2e-probe"

pytestmark = pytest.mark.skipif(os.environ.get("CLAUDE_E2E") != "1", reason="set CLAUDE_E2E=1 to call Claude Code")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, env=GIT_ENV).stdout.strip()


def make_repo(path: Path, branch: str) -> Path:
    subprocess.run(["git", "init", "-q", "-b", branch, str(path)], check=True, env=GIT_ENV)
    git(path, "config", "user.email", "e2e@example.com")
    git(path, "config", "user.name", "e2e")
    git(path, "commit", "-q", "--allow-empty", "-m", "init")
    return path


def run_claude(repo: Path, settings: Path) -> str:
    """Return the stream-json transcript, which includes each tool result."""
    out = subprocess.run(
        [
            "claude", "-p", PROMPT,
            "--setting-sources", "project",
            "--settings", str(settings),
            "--allowedTools", "Bash(git commit:*)",
            "--model", "haiku",
            "--output-format", "stream-json", "--verbose",
            "--no-session-persistence",
        ],
        cwd=repo, capture_output=True, text=True, timeout=300, env=GIT_ENV,
    )
    assert out.returncode == 0, out.stderr
    return out.stdout


@pytest.fixture
def settings(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": f"python3 {shlex.quote(str(HOOK))}"}]}]}
    }))
    return path


@pytest.mark.parametrize(("branch", "commits_added", "denied"), [("feature", 1, False), ("main", 0, True)])
def test_claude_code_runs_hook(tmp_path, settings, branch, commits_added, denied):
    """On main, the transcript must show the hook's deny reason, so a model that skips the commit cannot pass."""
    repo = make_repo(tmp_path / branch, branch)
    before = int(git(repo, "rev-list", "--count", "HEAD"))
    transcript = run_claude(repo, settings)
    after = int(git(repo, "rev-list", "--count", "HEAD"))
    assert after - before == commits_added, transcript[-2000:]
    assert (DENY_REASON in transcript) == denied, transcript[-2000:]
