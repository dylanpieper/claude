# agentsflow

```
   you ──► request
              │
              ▼
           change ◄───────┐
              │           │
              ▼           │
   you ──► commit         │ fail
              │           │
              ▼           │
           review ────────┘
              │ pass
              ▼
        pull request
              │
              ▼
   you ──► merge
```

## In this repo

My rules override the installed tools when they conflict.

- **[CLAUDE.md](CLAUDE.md)**: rules for every session: design, the shell, git, and the data stack.
- **[rules/r.md](rules/r.md)**: R preferences that the R plugins miss or contradict. Loads only for R files.
- **[rules/roborev.md](rules/roborev.md)**: how Claude uses roborev when I ask in plain words for a review or fix.
- **[research-writing](skills/research-writing/SKILL.md)**: APA 7 and open-science rules.
- **[block_main_commit.py](hooks/block_main_commit.py)**: blocks `git commit` on `main`. Asks when it cannot tell the branch.
- **[tests/](tests/)**: hook tests. Run `uv run --no-project --with pytest pytest tests`. Add `CLAUDE_E2E=1` to also test Claude Code calling the hook.

## Installed tools

- **[Clanker Constitution](https://github.com/kenn-io/constitution)**: operating principles for coding agents. © 2026 Kenn Software LLC, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **[roborev](https://github.com/kenn-io/roborev)**: reviews each commit in the background and sends findings back to Claude.
- **[caveman](https://github.com/juliusbrussee/caveman)**: short output, fewer tokens.
- **[r-skills](https://github.com/ab604/claude-code-r-skills)** and **[Posit skills](https://github.com/posit-dev/skills)**: R, packages, Quarto, and Shiny.
- **[python-skills](https://github.com/wdm0006/python-skills)**: Python setup with uv, ruff, and pytest.
- **[duckdb-skills](https://github.com/duckdb/duckdb-skills)**: read and query data files.
- **[UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)**: interface design guidance.
- **[Superpowers](https://github.com/obra/superpowers)**: workflow skills for planning, test-driven development, and debugging.

## Requirements

- [Claude Code](https://claude.com/claude-code), git, and the [GitHub CLI](https://cli.github.com)
- `python3` for the hook. R or Python with [uv](https://docs.astral.sh/uv/) for language work.

## Install

### 1. This repo

```
base=https://raw.githubusercontent.com/dylanpieper/agentsflow/main
mkdir -p ~/.claude/rules ~/.claude/skills/research-writing ~/.claude/hooks
curl -fsSL $base/CLAUDE.md -o ~/.claude/CLAUDE.md
curl -fsSL $base/rules/r.md -o ~/.claude/rules/r.md
curl -fsSL $base/rules/roborev.md -o ~/.claude/rules/roborev.md
curl -fsSL $base/skills/research-writing/SKILL.md -o ~/.claude/skills/research-writing/SKILL.md
curl -fsSL $base/hooks/block_main_commit.py -o ~/.claude/hooks/block_main_commit.py
```

Add the hook and the merge block to `~/.claude/settings.json`. Merge them into the file, because roborev also writes hooks there:

```
{
  "permissions": {
    "deny": ["Bash(gh pr merge:*)"]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3 ~/.claude/hooks/block_main_commit.py", "timeout": 10 }
        ]
      }
    ]
  }
}
```

### 2. Clanker Constitution

```
git clone https://github.com/kenn-io/constitution ~/src/constitution
mkdir -p ~/.claude/rules
ln -s ~/src/constitution/CONSTITUTION.md ~/.claude/rules/clanker-constitution.md
```

### 3. Plugins

```
claude plugin marketplace add JuliusBrussee/caveman
claude plugin install caveman@caveman
claude plugin marketplace add ab604/claude-code-r-skills
claude plugin install r-skills@r-skills
claude plugin marketplace add posit-dev/skills
claude plugin install r-lib@posit-dev-skills
claude plugin install quarto@posit-dev-skills
claude plugin install shiny@posit-dev-skills
claude plugin marketplace add wdm0006/python-skills
claude plugin install python-library-foundations@dev-skills
claude plugin marketplace add duckdb/duckdb-skills
claude plugin install duckdb-skills@duckdb-skills
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill
claude plugin install superpowers@claude-plugins-official
```

### 4. roborev

```
brew install kenn-io/tap/roborev
roborev agent-hook install
roborev skills install
```

Then run `roborev init` in each repository you want reviewed. For other install methods, see [roborev.io](https://roborev.io).

## Use

### Terminal

```
roborev tui
roborev ui
```

`roborev tui` opens the review dashboard in a second terminal. `roborev ui` opens it in the browser.

### caveman commands

| Command | Result |
|---|---|
| `/caveman` | Turns on caveman mode at level `full` |
| `/caveman lite` · `/caveman ultra` | Makes output less or more terse |
| `/caveman off` or "normal mode" | Turns off caveman mode |
| `/caveman-commit` | Writes a short Conventional Commit message |
| `/caveman-review` | Writes one-line review findings |
| `/caveman:compress <file>` | Compresses a Markdown file and keeps a backup |
| `/caveman-help` | Shows the caveman quick reference |

### roborev commands

| Command | Result |
|---|---|
| `/roborev-review` · `/roborev-review-branch` | Reviews a commit or a branch |
| `/roborev-design-review` · `/roborev-design-review-branch` | Reviews the design of a commit or a branch |
| `/roborev-lookahead-review` · `/roborev-lookahead-review-branch` | Looks ahead for problems in a commit or a branch |
| `/roborev-fix` | Fixes open review findings |
| `/roborev-refine` | Fixes findings and reviews again until they pass |
| `/roborev-respond` | Replies to a review |
| `/roborev-snooze` | Pauses review reminders |
