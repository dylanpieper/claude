# agentsflow

```
              YOU               │               CLAUDE
────────────────────────────────┼─────────────────────────────────
                                │          ┌──────────────┐
    request ────────────────────┼─────────►│  CLAUDE.md   │
                                │          │ Constitution │
                                │          │   caveman    │
                                │          └──────┬───────┘
                                │                 ▼
                                │             new branch
                                │                 │
                                │                 ▼
                                │               change ◄──────┐
                                │                 │           │
    approve ◄───────────────────┼─────────────────┘           │
       │                        │                             │
       └────────────────────────┼─────────────► commit        │
                                │                 │           │
                                │                 ▼           │
                                │          automated review   │
                                │                 │           │
    dashboard ◄─────────────────┼─────────────────┘           │
       │                        │                             │
       ▼                        │                             │
    outcome ─► fail ────────────┼──────────────► fix ─────────┘
       │                        │
       └─► pass ────────────────┼──────────► pull request
                                │                 │
    merge ✦ ◄───────────────────┼─────────────────┘
```

This repository holds my global Claude Code configuration. My own additions are small. Installed tools do the rest.

## In this repo

My rules override the installed tools when they conflict.

- **[CLAUDE.md](CLAUDE.md)**: rules for every session: design, the shell, git, and the data stack.
- **[rules/r.md](rules/r.md)**: my R preferences that the R plugins miss or contradict. It loads only when Claude reads an R file.
- **[research-writing](skills/research-writing/SKILL.md)**: a skill with APA 7 and open-science rules for manuscripts, reports, and statistical results.
- **[block_main_commit.py](hooks/block_main_commit.py)**: a hook that blocks `git commit` on `main`.

## Installed tools

- **[Clanker Constitution](https://github.com/kenn-io/constitution)**: default operating principles for coding agents. The agent honors the request, acts with judgment, finishes the job, protects existing work, verifies reality, and communicates for humans.
- **[roborev](https://github.com/kenn-io/roborev)**: continuous code review. It reviews each commit in the background, tells the agent about the findings, and shows the reviews in a terminal UI.
- **[caveman](https://github.com/juliusbrussee/caveman)**: makes Claude write short output. It keeps all technical content and uses fewer tokens.
- **[r-skills](https://github.com/ab604/claude-code-r-skills)**: R style, tidyverse, rlang, package development, and testing.
- **[Posit skills](https://github.com/posit-dev/skills)**: `r-lib` for cli, testthat, lifecycle, CRAN checks, and mirai. `quarto` for Quarto documents. `shiny` for Shiny apps with bslib.
- **[python-skills](https://github.com/wdm0006/python-skills)**: `python-library-foundations` for project setup with uv, ruff, and pytest.
- **[duckdb-skills](https://github.com/duckdb/duckdb-skills)**: reads, attaches, and queries data files.
- **[UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)**: design systems, palettes, and UX rules for interfaces.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- git and the [GitHub CLI](https://cli.github.com) (`gh`)
- R for R work. Python with [uv](https://docs.astral.sh/uv/) for Python work. `python3` for the commit hook.

## Workflow

Each request starts with the same rules. Claude reads my instructions and the constitution, then works on a new branch. The main branch stays clean, and all work stays in the current checkout.

Claude makes each change in small, logical steps. I approve each commit before it lands. An automated review then checks the commit in the background, and the review dashboard shows the result live. If the review fails, Claude fixes the findings, and the loop starts again.

When the review passes, Claude opens a pull request that tells what changed and why. I review it and merge it. Claude never merges.

## Install

### 1. This repo

Download the files into `~/.claude`. Edit them for your own languages and preferences.

```
base=https://raw.githubusercontent.com/dylanpieper/agentsflow/main
mkdir -p ~/.claude/rules ~/.claude/skills/research-writing ~/.claude/hooks
curl -fsSL $base/CLAUDE.md -o ~/.claude/CLAUDE.md
curl -fsSL $base/rules/r.md -o ~/.claude/rules/r.md
curl -fsSL $base/skills/research-writing/SKILL.md -o ~/.claude/skills/research-writing/SKILL.md
curl -fsSL $base/hooks/block_main_commit.py -o ~/.claude/hooks/block_main_commit.py
```

Add the hook and the merge block to `~/.claude/settings.json`:

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

Clone the constitution and link it as a global rule. Claude Code loads each file in `~/.claude/rules/`.

```
git clone https://github.com/kenn-io/constitution ~/src/constitution
mkdir -p ~/.claude/rules
ln -s ~/src/constitution/CONSTITUTION.md ~/.claude/rules/clanker-constitution.md
```

To use it in one repository only, copy `CONSTITUTION.md` to the repository root and add `@CONSTITUTION.md` to that repository's `CLAUDE.md`. Pin a reviewed release tag, and update it through a pull request.

### 3. Skill plugins

```
claude plugin marketplace add ab604/claude-code-r-skills
claude plugin install r-skills@r-skills
claude plugin marketplace add wdm0006/python-skills
claude plugin install python-library-foundations@dev-skills
claude plugin marketplace add posit-dev/skills
claude plugin install r-lib@posit-dev-skills
claude plugin install quarto@posit-dev-skills
claude plugin install shiny@posit-dev-skills
claude plugin marketplace add duckdb/duckdb-skills
claude plugin install duckdb-skills@duckdb-skills
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

`python-library-foundations` is the small Python bundle: project setup, code quality, and testing. For all Python skills, install `python-library-complete@dev-skills`. The Posit `github` and `posit-dev` plugins are left out because roborev and my git rules already cover pull requests and review.

### 4. caveman

```
claude plugin marketplace add JuliusBrussee/caveman
claude plugin install caveman@caveman
```

A session-start hook turns on caveman mode (level `full`) in each session.

### 5. roborev

Install the CLI with Homebrew:

```
brew install kenn-io/tap/roborev
```

Or with the install script or Go:

```
curl -fsSL https://roborev.io/install.sh | bash
go install go.kenn.io/roborev/cmd/roborev@latest
```

Install the Claude Code agent hook and the roborev skills:

```
roborev agent-hook install
roborev skills install
```

The agent hook adds `PreToolUse`, `PostToolUse`, and `Stop` hooks to `~/.claude/settings.json`. The skills go to `~/.claude/skills/`.

In each repository you want reviewed, install the post-commit hook:

```
roborev init
```

## Use

### Terminal

Open the review dashboard in a second terminal:

```
roborev tui
```

Or open the browser UI:

```
roborev ui
```

### Claude Code commands

| Command | Result |
|---|---|
| `/caveman` | Turns on caveman mode at level `full` |
| `/caveman lite` · `/caveman ultra` | Makes output less or more terse |
| `/caveman off` or "normal mode" | Turns off caveman mode |
| `/caveman-commit` | Writes a short Conventional Commit message |
| `/caveman-review` | Writes one-line review findings |
| `/caveman:compress <file>` | Compresses a Markdown file and keeps a backup |
| `/caveman-help` | Shows the caveman quick reference |
| `/roborev-review` · `/roborev-review-branch` | Reviews a commit or a branch |
| `/roborev-design-review` · `/roborev-design-review-branch` | Reviews the design of a commit or a branch |
| `/roborev-lookahead-review` · `/roborev-lookahead-review-branch` | Looks ahead for problems in a commit or a branch |
| `/roborev-fix` | Fixes open review findings |
| `/roborev-refine` | Fixes findings and reviews again until they pass |
| `/roborev-respond` | Replies to a review |
| `/roborev-snooze` | Snoozes a review |

## Credits

- [Clanker Constitution](https://github.com/kenn-io/constitution) © 2026 Kenn Software LLC, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- [caveman](https://github.com/juliusbrussee/caveman) by Julius Brussee
- [roborev](https://github.com/kenn-io/roborev) by Kenn Software LLC
