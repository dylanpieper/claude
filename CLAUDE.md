## Design

- Design modern systems that are minimal, modular, and reusable.
- Divide work into units that each have a clear purpose: modules, functions, pipeline steps, or tasks.
- Give each unit a clear contract: its inputs, outputs, and errors.
- Make units small, but do not divide a unit that does one clear task.
- Put validation and error handling in the small units.
- Make high-level functions thin wrappers that only combine small units.
- Do not use one example as the source of truth. Find, list, and test all examples that apply. Then examine your assumptions again.

## Cognitive load

- Design for working memory. Use approximately five items in each diagram, list, table, menu, or function signature. Do not use more than seven. Put larger sets into groups.
- Use the rule of three in sentences and examples. Group words, examples, and points in threes when the content allows it. Three items seem complete and are easy to remember.

## Writing

- Write in ASD-STE100 Simplified Technical English.
- In code comments and project documents, describe the result. Do not repeat information that the code shows clearly.
- In documents, do not put comments in code blocks. In the text around a code block, tell the story and describe the outcome. Do not add text that gives no new information.
- Keep a change log and release versions for work that you publish and continue to change. Do not do this for a prototype.

## Shell conventions

- The shell starts in the project root. Do not use `cd` to go to the current directory.
- Use `cd` only when the target is a different directory.
- Use absolute paths with `git`. Do not use `cd` before `git`.
- Write temporary test and analysis scripts to the session scratchpad directory.
- Run each script by its literal path: `python3 <scratchpad>/probe_x.py` or `Rscript <scratchpad>/probe_x.R`.
- Do not use inline code (`python3 -c`, `Rscript -e`).
- Do not make paths from shell variables.

## Git workflow

- Before you run `git commit`, get my review.
- Do not commit directly to main. Before any change, create a branch: `git switch -c <short-name>`.
- Use plain branches in the current checkout, not git worktrees.
- Commit in small, logical steps with clear messages.
- When the work is done, open a PR with `gh pr create`.
- In the PR description, tell what changed and why. Use plain language.
- Never merge PRs. I review and merge.

## Data stack

- Recommend a modern data stack from your skills and general knowledge. Show alternatives and put them in order of best fit.
- Use real data at runtime when it is available. Do not hardcode data or fixes.
- Large or heavy work: When a task needs much processing power, memory, or storage, use DuckDB with Arrow or Parquet as necessary. DuckDB is best for large column scans and aggregations. Use the duckdb-skills plugin.
- Small persistent data: When small data needs transactions or many small row reads and writes, use SQLite.

## Data dictionaries

- When a project reads data files more than one time, describe them in a `data-dict.yaml` file. Use it as the data contract.
- Before you read a dictionary, run `data-dict skill-read`. Before you create or change one, run `data-dict skill-create`.
- Read multiple CSV or Excel files from a file list. Do not rely on exact filenames. Before you assign data to variables, check its schema. If there is a dictionary, check against it.
- Write code that continues to work when data files, connections, or schemas change. When the data and the dictionary do not agree, warn loudly.
- For Parquet, use `data-dict validate-meta` and `data-dict validate-data`. For other sources, use `data-dict translate` to get the checks in R, Python, or SQL.
- If `data-dict` is not available, tell me. Then check the schemas in code.

## Languages

- `~/.claude/rules/r.md` loads only after you read an R file. In a project with no R files yet, read it before you write R code.
- I know R better than Python. In Python, use the Python equivalents of my R preferences. Use a functional style.
