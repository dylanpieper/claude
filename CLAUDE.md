## Design

- Design modern systems that are minimal, modular, and reusable.
- Divide work into meaningful units: modules, functions, pipeline steps, or tasks.
- Give each unit an explicit contract: inputs, outputs, and errors.
- Make units small, but do not divide a unit that does one clear task.
- Put validation and error handling in the small units.
- Make high-level functions thin wrappers that only combine small units.
- Do not use one example as the source of truth. Find, list, and test all applicable examples. Then examine your assumptions again.

## Cognitive load

- Design for working memory. Aim for about five items in each diagram, list, table, menu, or function signature, and do not go above seven. Group larger sets into chunks.
- Use the rule of three in sentences and examples. Group words, examples, and points in threes when the content allows it. Three items feel complete and are easy to remember.

## Writing

- Write in ASD-STE100 Simplified Technical English.
- In code comments and project documents, describe the result. Do not repeat information that the code shows clearly.
- Keep code blocks in documents bare. Tell a story. Describe an outcome. Do not put filler explanatory text around them.
- Keep change logs and release versioning for ongoing work that is being published (not a prototype).

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
- Do not commit directly to main. Before any change, create a branch: `git switch -c <short-name>`.
- Use plain branches in the current checkout, not git worktrees.
- Commit in small, logical steps with clear messages.
- When the work is done, open a PR with `gh pr create`.
- Write a description with what changed and why, in plain language.
- Never merge PRs. I review and merge.

## Data stack

- Recommend a modern data stack within your skills and general knowledge. Present alternatives but rank by best fit.
- Do not make a design more complex than necessary.
- Use real data at runtime when it is available. Do not hardcode data or fixes.
- Large or heavy work: When a task needs much compute, memory, or storage, use DuckDB, Arrow, or Parquet. Use the duckdb-skills plugin.
- Small persistent data: When small data needs structured storage, transactions, or many small reads and writes, use SQLite. SQLite keeps the data in one file and needs no server.
- Describe project data in a `data-dict.yaml` data dictionary. Before you read or write one, run `data-dict skill-read` or `data-dict skill-create`.
- Use the dictionary as the data contract:
  - When you read multiple CSV or Excel files, read them from a file list and check their schemas against the dictionary before you assign them to variables. Do not rely on exact filenames.
  - Defensively write to accommodate updated data files or connections and handle schema changes over time. Warn loudly when the data and the dictionary do not agree.
  - For Parquet, check with `data-dict validate-meta` and `data-dict validate-data`. For other sources, use `data-dict translate` to get the checks in R, Python, or SQL.

## Languages

- `~/.claude/rules/r.md` loads only after you read an R file. In a project with no R files yet, read it before you write R code.
- I know R better than Python. In Python, use the parallels of my R preferences and a functional style.
