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
- **[research-writing](skills/research-writing/SKILL.md)**: APA 7, open-science, and figure rules.

## Installed tools

- **[Clanker Constitution](https://github.com/kenn-io/constitution)**: operating principles for coding agents. © 2026 Kenn Software LLC, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **[roborev](https://github.com/kenn-io/roborev)**: reviews each commit in the background and sends findings back to Claude.
- **[caveman](https://github.com/juliusbrussee/caveman)**: short output, fewer tokens.
- **[r-skills](https://github.com/ab604/claude-code-r-skills)** and **[Posit skills](https://github.com/posit-dev/skills)**: R, packages, Quarto, and Shiny.
- **[python-skills](https://github.com/wdm0006/python-skills)**: Python setup with uv, ruff, and pytest.
- **[duckdb-skills](https://github.com/duckdb/duckdb-skills)**: read and query data files.
- **[data-dict](https://github.com/tidyverse/data-dict)**: data dictionaries that are checked against the data.
- **[slidecrafting](https://github.com/EmilHvitfeldt/slidecrafting-book.com)**: build, theme, and animate Quarto reveal.js slide decks.
- **[Superpowers](https://github.com/obra/superpowers)**: workflow skills for planning, test-driven development, and debugging.

## Requirements

- [Claude Code](https://claude.com/claude-code). Each install step names the other tools it needs. Install only the steps you want.

## Install

### 1. This repo

Needs curl.

```
base=https://raw.githubusercontent.com/dylanpieper/agentsflow/main
mkdir -p ~/.claude/rules ~/.claude/skills/research-writing
curl -fsSL $base/CLAUDE.md -o ~/.claude/CLAUDE.md
curl -fsSL $base/rules/r.md -o ~/.claude/rules/r.md
curl -fsSL $base/rules/roborev.md -o ~/.claude/rules/roborev.md
curl -fsSL $base/skills/research-writing/SKILL.md -o ~/.claude/skills/research-writing/SKILL.md
```

Add the merge block to `~/.claude/settings.json`. Merge it into the file, because roborev also writes there:

```
{
  "permissions": {
    "deny": ["Bash(gh pr merge:*)"]
  }
}
```

### 2. Protect main

Needs the [GitHub CLI](https://cli.github.com). Run this in each repository to block direct pushes to the default branch. Changes then go through a pull request. The ruleset does not block local commits. On the free plan, GitHub does not enforce rulesets on private repositories.

```
gh api repos/{owner}/{repo}/rulesets --method POST --input - <<'EOF'
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    }
  ]
}
EOF
```

### 3. Clanker Constitution

Needs git.

```
git clone https://github.com/kenn-io/constitution ~/src/constitution
mkdir -p ~/.claude/rules
ln -s ~/src/constitution/CONSTITUTION.md ~/.claude/rules/clanker-constitution.md
```

### 4. Plugins

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
claude plugin marketplace add EmilHvitfeldt/slidecrafting-book.com
claude plugin install slidecrafting@slidecrafting
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install superpowers@claude-plugins-official
```

### 5. data-dict

Needs [uv](https://docs.astral.sh/uv/). For other install methods, see the [data-dict install page](https://data-dict.tidyverse.org/install.html).

```
uv tool install data-dict-yaml
```

### 6. roborev

Needs [Homebrew](https://brew.sh).

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
