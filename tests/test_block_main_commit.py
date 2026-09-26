import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "block_main_commit.py"
sys.path.insert(0, str(HOOK.parent))
import block_main_commit as hook  # noqa: E402


def make_repo(path: Path, branch: str) -> Path:
    subprocess.run(["git", "init", "-q", "-b", branch, str(path)], check=True)
    return path


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    make_repo(tmp_path / "on_main", "main")
    make_repo(tmp_path / "on_feature", "feature")
    return tmp_path


def run_hook(command: str, cwd: Path) -> bool:
    """Run the hook as Claude Code does. Return True when it denies the call."""
    event = json.dumps({"cwd": str(cwd), "tool_input": {"command": command}})
    out = subprocess.run([sys.executable, str(HOOK)], input=event, capture_output=True, text=True, check=True).stdout
    return '"deny"' in out


BLOCKED = [
    ("git commit -m m", "on_main"),
    ("git -C {home}/on_main commit -m m", "."),
    ("git -C on_main commit -m m", "."),
    ("git -C ~/on_main commit -m m", "."),
    ("git -c user.name=x commit -m m", "on_main"),
    ("git --git-dir {home}/on_main/.git --work-tree {home}/on_main commit -m m", "."),
    ("cd {home}/on_main && git commit -m m", "."),
    ("cd on_main && git commit -m m", "."),
    ("/usr/bin/git commit -m m", "on_main"),
    ("git add .;git commit -m m", "on_main"),
    ("git add . && git commit -m 'a b'", "on_main"),
    ("GIT_AUTHOR_NAME=x git commit -m m", "on_main"),
    ("git status || git commit -m m", "on_main"),
]

ALLOWED = [
    ("git commit -m m", "on_feature"),
    ("git -C ~/on_feature commit -m m", "."),
    ("cd on_feature && git commit -m m", "."),
    ("cd on_main && cd ../on_feature && git commit -m m", "."),
    ("git status", "on_main"),
    ("git log -m commit", "on_main"),
    ("echo git commit", "on_main"),
    ("git commit -m m", "."),
    ("git commit -m 'unclosed", "on_main"),
]


@pytest.mark.parametrize(("command", "cwd"), BLOCKED)
def test_blocks_commit_on_main(home, command, cwd):
    assert run_hook(command.format(home=home), home / cwd)


@pytest.mark.parametrize(("command", "cwd"), ALLOWED)
def test_allows_other_calls(home, command, cwd):
    assert not run_hook(command.format(home=home), home / cwd)


def test_segments_split_at_operators():
    assert hook.segments("a b;c && d | e") == [["a", "b"], ["c"], ["d"], ["e"]]
