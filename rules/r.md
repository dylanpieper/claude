---
paths:
  - "**/*.{R,r,Rmd,qmd}"
  - "**/DESCRIPTION"
---

# R

The r-skills plugin covers general style, tidyverse, rlang, and package development. These rules add to it or override it.

- Do not use `return()` at the end of a function, even a long one. Use `return()` only for an early exit.
- Use four dashes for section headings: `# Load data ----`.
- Do not use partial argument matching.
- Use `cli` for console output (for example, `cli::cli_alert_success()`). Do not use `cat()`, `message()`, or `print()`.
- A function with side effects returns its first argument invisibly.
- For data that is not clean, use `janitor::clean_names()`.
- In scripts, call functions from loaded packages directly. Use `pkg::fn()` only for one or two calls, for a name conflict, or in package code.
- For complex projects, these packages can help: renv, config, here, pins, box, targets, logger, and profvis.
- `box::use()` keeps a module in cache until the R session stops. After you change a module file, restart R or call `box::reload()`. Then do the tests.

## Packages

- Keep the error context: use `withCallingHandlers()` with `parent = e`, or `rlang::try_fetch()`. Do not throw an error again inside `tryCatch()`.
- Use `rlang::check_installed()` for suggested dependencies.
- Use `@importFrom` only for operators (for example, `%||%`), frequent calls, and tight loops. Use `@import` only when necessary.
- Use `pkgdown` with `light-switch` set to `true`.

## Figures and tables

- For distributions, use `ggdist` (raincloud plots and intervals), `ggbeeswarm`, `ggforce` (sina plots), or `ggridges`.
- For model coefficients, Likert data, and proportions, use `ggstats`.
- For tables, use `gt`.
