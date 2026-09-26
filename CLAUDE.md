# General

- Design systems that are minimal, modular, and reusable.
- Divide work into meaningful units: modules, functions, pipeline steps, or tasks.
- Give each unit an explicit contract: inputs, outputs, and errors.
- Make units small, but do not divide a unit that does one clear task.
- Put validation and error handling in the small units.
- Make high-level functions thin wrappers that only combine small units.
- Use real data at runtime when it is available. Do not hardcode data or fixes.
- Do not use one example as the source of truth. Find, list, and test all applicable examples. Then examine your assumptions again.
- In code comments and project documents, describe the result. Do not repeat information that the code shows clearly.
- Keep code blocks in documents bare. Do not put explanatory text around them.
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
- Before any change, create a branch: `git switch -c <short-descriptive-name>`.
- Use plain branches in the current checkout, not git worktrees.
- Commit in small, logical steps with clear messages.
- When the work is done, open a PR with `gh pr create`. 
- Write a description with what changed and why, in plain language.
- Never merge PRs. I review and merge.

## Modern data stack

- Design for a modern data stack.
- Do not make a design more complex than necessary.
- For large tasks with high compute, memory, or storage requirements, use DuckDB, Arrow, and Parquet.
- For small tasks that need better data management, use SQLite.

## R style

- Use the tidyverse style guide.
- Use `snake_case`.
- Use short names that have a clear meaning. Use standard abbreviations (`df`, `n`, `sd`).
- Use `<-`, `TRUE`/`FALSE`, `|>`, and double quotes.
- Do not use partial argument matching.
- Use four dashes for section headings: `# Load data ----`.
- Do not use `return()` at the end of a function. Use `return()` only for an early exit.
- For complex projects, these R packages can help: usethis, renv, config, here, pins, box, targets, testthat, logger, and profvis.
- `box::use()` keeps a module in cache until the R session stops. After you change a file in the modules directory (for example, `R/`), restart R or call `box::reload()`. Then do the tests.

### Tidyverse

- Use tibbles and readr.
- For data that is not clean, use `janitor::clean_names()`.
- For a single grouped operation, use `.by` or `by`. Do not use `group_by() |> ... |> ungroup()`.
- Use `filter_out()`, `when_any()`, and `when_all()`. These functions are new.
- Use `list_rbind()` and `list_cbind()`. Do not use `do.call(rbind, ...)`.
- A function with side effects must return its first argument invisibly.
- Use purrr instead of loops when possible.
- Use `\(x)` for short inline functions.
- Use `function()` for a function that has a name, that you use again, or that has more than one line.
- Use `cli` for console messages and errors (for example, `cli::cli_alert_success()`). Do not use `cat()`, `message()`, or `print()`.

### Namespacing in scripts

- Call functions from loaded packages directly.
- Use `pkg::fn()` only in these conditions:
  - The script calls the function one or two times.
  - Two packages have a function with the same name (for example, `dplyr::filter()`).
  - The code is part of a package.

## R package development

- Use `usethis` and `devtools` to setup and execute your workflows
- Use `pkg::fn()` for external dependencies.
- Use `@importFrom` for operators (for example, `%||%`), for functions that you call often, and in tight loops.
- Use `@import` only when necessary.
- Define exported functions with `function()`. Do not use `\()`.
- Use `cli::cli_abort()`, `cli::cli_warn()`, and `cli::cli_inform()`. Do not use the base R equivalents.
- To keep the error context, use `withCallingHandlers()` with `parent = e`, or use `rlang::try_fetch()`.
- Do not throw an error again inside `tryCatch()`. This removes the backtrace.
- Use `rlang::check_installed()` for suggested dependencies.
- Use `devtools::check()` for full tests and validation.
- Update `NEWS.md` when noteworthy changes are made that affect users
- Use `pkgdown` with `light-switch` set to `true`

## Python style

I have more experience with R, so I do not have strong Python style preferences. Please find the parallels to my R preferences and use modern pythonic patterns. Consider norms and new developments within the broader functional programming landscape.

## Research writing

- Use APA 7 headings, in-text citations, and references.
- For short documents, use a simple structure with APA conventions.
- Use the active voice.
- Write short sentences. Remove words that add no information.
- Do not add unnecessary qualifiers.
- Use the past tense for procedures and results.
- Use the present tense for known facts and implications.
- Write numbers below 10 as words. Exceptions: numbers with units, numbers in tables, and statistical results.

### Open science

- Report effect sizes, confidence intervals, and exact p-values.
- Round coefficients and test statistics to two decimal places.
- Round p-values to three decimal places.
- Use "statistically significant" carefully.
- Do not make decisions only on a binary threshold.
- Keep confirmatory analyses separate from exploratory analyses.
- Report all analytic decisions clearly.
- Report null and unexpected results honestly.
- Use bootstrapping and simulation when they are applicable.
- Use power analyses or sensitivity analyses when they are applicable.