# How Uptake uses IBM Bob 2.0

IBM Bob is the agent that does the repair, and Bob 2.0's extension points are how Uptake makes that repair trustworthy.

## 1. A custom mode is the lock
Uptake ships a **custom mode** (`.bob/custom_modes.yaml`). In it, Bob:
- **Edits only production source.** The `edit` group has a `fileRegex` that Uptake computes from each project's own poms, so `src/java`, `${project.basedir}/src` and multi-module builds all get the right lock. Tests, `pom.xml`, `.bob/` and `..` escapes are refused before any file is touched.
- **Has no shell.** There's no `execute` group, so `mvn -DskipTests` or `sed` on the pom are impossible.
- **May delegate only to read-only `explore` subagents** (`allowedSubagents: [explore]`) for call-site search. In practice Bob used one in 1 of 19 benchmark runs; most breaks were local enough not to need it.

## 2. A custom MCP server gives Bob evidence
`.bob/mcp.json` connects Bob to Uptake's server:
- **`uptake_status`:** the upgrade, the advisories it removes, and the original failure.
- **`uptake_build`:** compiles and runs every test in the original BUMP container, offline. It returns the compile errors and failing tests' own stack traces, and, for each missing symbol, where it lived in the old library and what exists in the new one.
- **`uptake_api_lookup`:** the same evidence on demand.
- **`uptake_audit`:** the integrity check used for the final verdict.

None of these tools can edit a file.

## 3. Mode rules turn "stuck" into one approval
`.bob/rules-uptake/` tells Bob when to stop. For a companion library left behind, a moved class used in tests, or a deliberate behaviour change, Bob writes `.uptake/escalation.md` and a `.uptake/proposed.patch`. Uptake applies the patch in a scratch copy and proves whether it goes green. On the Log4Shell upgrade, Bob found the mismatched `log4j-slf4j18-impl` and proposed a one-line pom change. Uptake proved it: 67/67 tests.

## 4. Bob Shell ran the benchmark headless
Every case ran with `bob run --mode uptake --max-cost 1.0 --format stream-json`. Bob's reported cost and tool counts feed the results table directly.

We ran the same Bob on the same upgrades three ways:
- **Uptake mode**
- **Agent mode with the rules written down**
- **Agent mode with a normal request** ("get the build and all tests passing")

With Uptake's rules, Bob never made a silent edit to a test or build file. Without them, it made silent edits in 3 of 4 cases. In one it downgraded a logging library to a 2008 release and swapped out the app's log4j binding, and the build still failed.

## 5. Bob IDE is the developer experience
A developer opens the repo, picks **Uptake** from the mode menu and types *"Repair this dependency upgrade."*. The IDE session screenshots are in `bob_sessions/`.

## 6. Who wrote what
Bob wrote every repair and proposed patch in the benchmark, and the `uptake pr` feature (see `bob_sessions/`). The harness, auditor and results site were written with help from another AI coding assistant, and all of it was reviewed by a human.

Every Bob run's full trace, diff, rationale and receipt is on the results site (`docs/`). Each receipt re-verifies with `python -m uptake verify`.
