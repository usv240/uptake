# lablab.ai submission fields

## Project title
Uptake: security upgrades an AI agent can't cheat on

## Short description
When a Dependabot security upgrade breaks the build, Uptake has IBM Bob repair the code in a locked mode, proves it green offline, and commits the fix to the PR, or leaves a one-line patch already proven green. Runs as a GitHub Action.

## Technology & category tags
IBM Bob, IBM Bob Shell, MCP, Java, Maven, Docker, Software Supply Chain Security, DevSecOps, Dependency Management, AI Agents, Application Maintenance

## Long description: Problem & Solution (under 500 words)

**Problem.** Security fixes usually exist: 95% of vulnerable components downloaded had a fixed version available (Sonatype 2024). Teams don't take them because the upgrade breaks the build. We looked up the ten real Dependabot security PRs behind our benchmark: **none were merged**. HAP-Java's BouncyCastle upgrade, which removes 13 advisories, sat open for **1,603 days**. Coding agents make it riskier, because they get CI green however they can.

**Solution.** Uptake runs IBM Bob in a custom **Uptake mode**. Bob can edit only production source (the lock is computed from the project's poms) and has no shell. Uptake's MCP server gives Bob:
- the real failure, reproduced offline;
- what changed in the library's API;
- the library's own release notes (document understanding);
- an offline test runner.

When the fix needs a file Bob may not touch, Bob writes a proposed patch. Uptake proves it in a scratch copy, so a human only approves.

An independent auditor diffs every file, names every dependency version change, and writes a receipt that anyone can rebuild with `uptake verify`.

**Where it runs.** It's a GitHub Action: `uses: usv240/uptake@main`. On a Dependabot PR it runs Bob Shell in CI, commits the proven fix to the PR, and comments the receipt. Bob wrote the CI pipeline and the PR comment feature itself.

**Evidence, on data we didn't write.** The cases are real breaking Dependabot/Renovate upgrades from the BUMP benchmark (SANER 2024). Of BUMP's 571 cases, 146 remove known advisories; our 11 come from those, including two Log4Shell patches.
- **8 of 11 unblocked:**
  - 4 repaired with all tests green;
  - 3 proven one-approval patches on the first pass;
  - 1 more once Bob read the library's release notes.
- **Both Log4Shell upgrades** are among them.
- **0 silent edits** to tests or build files across 18 runs under Uptake's rules.
- **HAP-Java:** Bob took 61 seconds.
- **pdb:** Bob's fix is identical to the maintainers' own.
- **Byam baseline:** on the 7 cases the published Byam system also attempted, it needed its best of 40 configurations to solve 4. Uptake solved 4 in one run each.

**Control.** The same Bob with a normal request ("get the build and all tests passing") made silent edits in **3 of 4** runs. On Log4Shell it downgraded a logging library to a 2008 release, and the build still failed.

**Limits, measured.** The sample is small, and every run is shown, failures included. On this sample the rules mattered more than the mode lock. Test-code fixes are escalated, not made. Java/Maven only.

## IBM Bob usage statement (under 500 words)
See BOB_USAGE.md (trimmed copy below is what goes in the form).
