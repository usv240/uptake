# How Uptake uses IBM Bob 2.0

IBM Bob does the repairs, and Bob 2.0's extension points make those repairs safe to trust.

## 1. A custom mode is the lock
In the **Uptake mode** (`.bob/custom_modes.yaml`), Bob:
- **edits only production source.** The `fileRegex` is computed from each project's own poms. Tests, `pom.xml`, `.bob/` and `..` escapes are refused.
- **has no shell.** There's no `execute` group.
- **can delegate only to read-only `explore` subagents** (`allowedSubagents: [explore]`).

## 2. An MCP server gives Bob evidence
`.bob/mcp.json` connects Bob to Uptake's server. None of its tools can edit a file.
- **`uptake_status`:** the upgrade, the advisories it removes, and the original failure.
- **`uptake_build`:** the full test suite in the original container, offline, with the failing tests' stack traces and API evidence for each missing symbol.
- **`uptake_api_lookup`:** that evidence on demand.
- **`uptake_release_notes`** (document understanding): the library's own release notes and changelogs for the versions involved. Bob reads them and cites the source.
- **`uptake_audit`:** the integrity check behind the final verdict.

## 3. Mode rules turn "stuck" into one approval
`.bob/rules-uptake/` tells Bob when to stop. For a companion library left behind, or a moved class used in tests, Bob writes `.uptake/proposed.patch`, and Uptake proves it in a scratch copy. On the Log4Shell upgrade, Bob proposed a one-line pom change, and Uptake proved it: 67/67 tests green.

## 4. Bob Shell runs it headless, in parallel and in CI
- **Benchmark:** every case ran with `bob run --mode uptake --max-cost 1.0 --format stream-json`. Bob's reported costs feed the results. Three cases ran as parallel Bob tasks.
- **In CI:** the GitHub Action (`action.yml`) installs Bob Shell and runs the same mode on a Dependabot PR. Uptake then commits a proven fix to that PR and comments the receipt.

## 5. The controlled comparison
We ran the same Bob on the same upgrades three ways: Uptake mode, rules only, and a normal request. With Uptake's rules, Bob made no silent edits to tests or build files. With a normal request it made them in 3 of 4 runs, including downgrading a logging library to a 2008 release.

## 6. Bob IDE is the developer experience
A developer picks **Uptake** from the mode menu and types *"Repair this dependency upgrade."*. IDE session screenshots are in `bob_sessions/`.

## 7. Who wrote what
**Bob wrote:**
- every repair and proposed patch;
- `uptake pr` (the PR comment) and `uptake ci` (the CI pipeline), with tests.

Their full traces are in `bench/runs/build/`.

The harness, auditor and site were written with another AI coding assistant. A human reviewed everything, and review fixes to Bob's code are listed in the commits.
