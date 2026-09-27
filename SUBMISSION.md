# lablab.ai submission fields

## Project title
Uptake: security upgrades an AI agent can't cheat on

## Short description
Uptake reproduces a breaking security upgrade, has IBM Bob rewrite your code to the new API with tests and build files locked read-only, and proves it green in the original container, or hands back a one-line patch already proven green.

## Technology & category tags
IBM Bob, IBM Bob Shell, MCP, Java, Maven, Docker, Software Supply Chain Security, DevSecOps, Dependency Management, AI Agents, Application Maintenance

## Long description: Problem & Solution (under 500 words)

**Problem.** Security fixes usually exist: 95% of vulnerable components downloaded had a fixed version available (Sonatype 2024). Teams don't take them because the upgrade breaks the build. Four years after Log4Shell, 13% of Log4j downloads are still vulnerable. The best published AI system for breaking upgrades fully repairs 27% (Byam, EMSE 2026). Coding agents add a new risk: they get CI green however they can, and frontier agents exploit tests up to 76% of the time (ImpossibleBench, ICLR 2026).

**Solution.** Uptake runs IBM Bob in a custom **Uptake mode**. Bob can edit only production source; the lock is computed from the project's own poms. Tests, build files, versions and Bob's config are outside its permission, and there's no shell. Uptake's MCP server gives Bob the real failure, reproduced offline in the original container. For every missing symbol it shows what existed in the old library and what replaced it, and it gives Bob an offline build-and-test verifier.

When a fix needs a file Bob may not touch, such as a companion library's version or a test importing a moved class, Bob writes a proposed patch and stops. Uptake applies it in a scratch copy and proves whether it goes green, so a human only has to approve it.

An independent auditor trusts nothing the agent says. It diffs every file, names every dependency version change, and writes `UPGRADE_RECEIPT.md` with a patch hash. `uptake verify` rebuilds any receipt from the public images.

**Evidence, on data we didn't write.** Every case is a real Dependabot/Renovate upgrade that broke a real open-source build, from the BUMP benchmark (SANER 2024). We queried OSV for all 571 BUMP cases: 146 remove known advisories. Our cases come from those, including two Log4Shell patches.

**Results.**
- **7 of 11 unblocked** (95% CI 35–85%): 4 repaired with all tests green, and 3 one-approval patches proven green.
- **38 advisories unblocked**, including Log4Shell.
- **0 silent edits** to tests or build files in 15 runs under Uptake's rules.

On Log4Shell, Bob traced 43 dead tests to a companion logging library left behind. It proposed one pom line, and Uptake proved it: 67/67 tests green.

**Control.** The same Bob with a normal request ("get the build and all tests passing") made silent edits in **3 of 4** runs. On Log4Shell it downgraded slf4j-api to a 2008 release, and the build still failed.

**Baseline.** On the 7 cases Byam also attempted, Byam needed its best of 40 configurations to solve 4; Uptake repaired 4 in one run each.

**Limits, measured.** The sample is small because every run costs Bobcoins; every run is shown, failures included. On this sample the rules mattered more than the lock: rules alone also gave 0 silent edits. Test-code fixes are escalated, not made. Java/Maven only.

Everything re-runs: 54 unit tests, the harness, and every Bob trace, diff and receipt.

## IBM Bob usage statement (under 500 words)
See BOB_USAGE.md (trimmed copy below is what goes in the form).
