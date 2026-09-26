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


def run_hook(command: str, cwd: Path) -> str:
    """Run the hook as Claude Code does. Return its decision: deny, ask, or allow."""
    event = json.dumps({"cwd": str(cwd), "tool_input": {"command": command}})
    out = subprocess.run([sys.executable, str(HOOK)], input=event, capture_output=True, text=True, check=True).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else "allow"


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
    ("git add .\ngit commit -m m", "on_main"),
    ("cd on_main\ngit commit -m m", "."),
    ('git commit -m "line one\nline two"', "on_main"),
    ("(git commit -m m)", "on_main"),
    ("(cd on_main && git commit -m m)", "."),
    ("if true; then git commit -m m; fi", "on_main"),
    ("for f in a; do git commit -m m; done", "on_main"),
    ("command git commit -m m", "on_main"),
    ("env -i git commit -m m", "on_main"),
    ("GIT_DIR={home}/on_main/.git GIT_WORK_TREE={home}/on_main git commit -m m", "on_feature"),
    ("cd - && cd {home}/on_main && git commit -m m", "on_feature"),
    ("cd && cd on_main && git commit -m m", "on_feature"),
    ("(cd ../on_feature && true) && git commit -m m", "on_main"),
    ("(cd ../on_feature);git commit -m m", "on_main"),
    ("git commit -m a && cd ../on_main # next\ngit commit -m b", "on_feature"),
    ("git add . # stage\ngit commit -m m", "on_main"),
]

ALLOWED = [
    ("git commit -m m", "on_feature"),
    ("git -C ~/on_feature commit -m m", "."),
    ("cd on_feature && git commit -m m", "."),
    ("cd on_main && cd ../on_feature && git commit -m m", "."),
    ("git status", "on_main"),
    ("git add . && git push", "on_main"),
    ("git log --grep commit", "on_main"),
    ("git log | grep commit", "on_main"),
    ('gh pr create --body "run git commit first"', "on_main"),
    ("git add .\necho commit", "on_main"),
    ("(cd ../on_main && git status) && git commit -m m", "on_feature"),
    ("git status # git commit later", "on_main"),
    ("GIT_DIR={home}/on_feature/.git GIT_WORK_TREE={home}/on_feature git commit -m m", "on_main"),
]

ASKED = [
    ("echo git commit", "on_main"),
    ("cd - && git commit -m m", "on_feature"),
    ("git commit -m 'unclosed", "on_main"),
    ("git commit -m m", "."),
]


@pytest.mark.parametrize(("command", "cwd"), BLOCKED)
def test_denies_commit_on_main(home, command, cwd):
    assert run_hook(command.format(home=home), home / cwd) == "deny"


@pytest.mark.parametrize(("command", "cwd"), ALLOWED)
def test_allows_other_calls(home, command, cwd):
    assert run_hook(command.format(home=home), home / cwd) == "allow"


@pytest.mark.parametrize(("command", "cwd"), ASKED)
def test_asks_when_unsure(home, command, cwd):
    """A commit the hook cannot resolve goes to the user, not through."""
    assert run_hook(command.format(home=home), home / cwd) == "ask"


def test_asks_when_hook_crashes(tmp_path):
    out = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True, check=True).stdout
    assert json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_segments_split_at_operators():
    assert hook.segments("a b;c && d | e\nf") == [["a", "b"], ["c"], ["d"], ["e"], ["f"]]
    assert hook.segments("(cd x);y # z\nw") == ["(", ["cd", "x"], ")", ["y"], ["w"]]
    assert hook.segments('git commit -m "x\ny"') == [["git", "commit", "-m", "x\ny"]]
