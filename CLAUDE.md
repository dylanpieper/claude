# General instructions

- Design modern systems that are minimal, modular, and reusable.
- Divide work into meaningful units: modules, functions, pipeline steps, or tasks.
- Give each unit an explicit contract: inputs, outputs, and errors.
- Make units small, but do not divide a unit that does one clear task.
- Put validation and error handling in the small units.
- Make high-level functions thin wrappers that only combine small units.
- Use real data at runtime when it is available. Do not hardcode data or fixes.
- Do not use one example as the source of truth. Find, list, and test all applicable examples. Then examine your assumptions again.
- In code comments and project documents, describe the result. Do not repeat information that the code shows clearly.
- Keep code blocks in documents bare. Tell a story. Describe an outcome. Do not put filler explanatory text around them.
- Keep change logs and release versioning for ongoing work that is being published (not a prototype).
- Write in ASD-STE100 Simplified Technical English.

## Shell conventions

- The shell starts in the project root. Do not use `cd` to go to the current directory.
- Use `cd` only when the target is a different directory.
- Use absolute paths with `git`. Do not use `cd` before `git`.
- Write temporary test and analysis scripts to the session scratchpad directory.
- Run each script by its literal path: `python3 <scratchpad>/probe_x.py` or `Rscript <scratchpad>/probe_x.R`.
- Do not use inline code (`python3 -c`, `Rscript -e`).
- Do not make paths from shell variables.

## Git workflow

- I review commits before you run `git commit`.
- Do not commit directly to main.
- Before any change, create a branch: `git switch -c <short-name>`.
- Use plain branches in the current checkout, not git worktrees.
- Commit in small, logical steps with clear messages.
- When the work is done, open a PR with `gh pr create`.
- Write a description with what changed and why, in plain language.
- Never merge PRs. I review and merge.

## Data stack

- Recommend a modern data stack within your skills and general knowledge. Present alternatives but rank by best fit.
- Do not make a design more complex than necessary.
- For large tasks with high compute, memory, or storage requirements, use DuckDB, Arrow, and/or Parquet. Use the duckdb-skills plugin.
- For small tasks that need better data management, use SQLite.
- When you read multiple CSV or Excel files, read them from a list and check their schemas before you assign them to variables. Do not rely on an exact filename.
- Defensively write to accommodate updated data files or connections and handle schema changes over time. Warn of changes loudly.

## Languages and writing

- R: follow the r-skills and Posit plugins and `~/.claude/rules/r.md`. The rules file loads when you read an R file. In a project with no R files yet, read it before you write R code.
- Python: follow the python-library-foundations plugin. I know R better than Python, so use the Python parallels of my R preferences and a functional style.
- Research writing: use the `research-writing` skill.
