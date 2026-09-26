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

- **[CLAUDE.md](CLAUDE.md)**: rules for every session.
- **[rules/roborev.md](rules/roborev.md)**: how Claude uses roborev when I ask in plain words for a review or fix.
- **[research-writing](skills/research-writing/SKILL.md)**: APA 7, open-science, and figure rules.
- **[rules/r.md](rules/r.md)**: R preferences that the R plugins miss or contradict. Loads only for R files.

## Installed tools

### Workflow

- **[Clanker Constitution](https://github.com/kenn-io/constitution)**: operating principles for coding agents. © 2026 Kenn Software LLC, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **[Superpowers](https://github.com/obra/superpowers)**: workflow skills for planning, test-driven development, and debugging.
- **[roborev](https://github.com/kenn-io/roborev)**: reviews each commit in the background and sends findings back to Claude.
- **[caveman](https://github.com/juliusbrussee/caveman)**: short output, fewer tokens.

### Data

- **[duckdb-skills](https://github.com/duckdb/duckdb-skills)**: read and query data files.
- **[data-dict](https://github.com/tidyverse/data-dict)**: data dictionaries that are checked against the data.

### R

- **[r-skills](https://github.com/ab604/claude-code-r-skills)** and **[Posit skills](https://github.com/posit-dev/skills)**: R, packages, Quarto, and Shiny.
- **[Air](https://posit-dev.github.io/air/)**: R code formatter.

### Python

- **[python-skills](https://github.com/wdm0006/python-skills)**: Python setup with uv, ruff, and pytest.

### Slides

- **[slidecrafting](https://github.com/EmilHvitfeldt/slidecrafting-book.com)**: build, theme, and animate Quarto reveal.js slide decks.

## Install

### 1. This repo

```
base=https://raw.githubusercontent.com/dylanpieper/agentsflow/main
mkdir -p ~/.claude/rules ~/.claude/skills/research-writing
curl -fsSL $base/CLAUDE.md -o ~/.claude/CLAUDE.md
curl -fsSL $base/rules/r.md -o ~/.claude/rules/r.md
curl -fsSL $base/rules/roborev.md -o ~/.claude/rules/roborev.md
curl -fsSL $base/skills/research-writing/SKILL.md -o ~/.claude/skills/research-writing/SKILL.md
```

Add this rule to `permissions.deny` in `~/.claude/settings.json`:

```
"Bash(gh pr merge:*)"
```

### 2. Protect main

Run in each repository to block direct pushes to the default branch. On the free plan, GitHub does not enforce this on private repositories.

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

```
git clone https://github.com/kenn-io/constitution ~/src/constitution
mkdir -p ~/.claude/rules
ln -s ~/src/constitution/CONSTITUTION.md ~/.claude/rules/clanker-constitution.md
```

### 4. roborev

```
brew install kenn-io/tap/roborev
roborev agent-hook install
roborev skills install
```

Then run `roborev init` in each repository to review.

### 5. Plugins

```
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install superpowers@claude-plugins-official
claude plugin marketplace add JuliusBrussee/caveman
claude plugin install caveman@caveman

claude plugin marketplace add duckdb/duckdb-skills
claude plugin install duckdb-skills@duckdb-skills

claude plugin marketplace add ab604/claude-code-r-skills
claude plugin install r-skills@r-skills
claude plugin marketplace add posit-dev/skills
claude plugin install r-lib@posit-dev-skills
claude plugin install quarto@posit-dev-skills
claude plugin install shiny@posit-dev-skills

claude plugin marketplace add wdm0006/python-skills
claude plugin install python-library-foundations@dev-skills

claude plugin marketplace add EmilHvitfeldt/slidecrafting-book.com
claude plugin install slidecrafting@slidecrafting
```

### 6. data-dict

```
uv tool install data-dict-yaml
```

### 7. Air

```
uv tool install air-formatter
```

## Use

### roborev dashboard

| Command | Result |
|---|---|
| `roborev tui` | Opens the dashboard in the terminal |
| `roborev ui` | Opens the dashboard in the browser |

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
