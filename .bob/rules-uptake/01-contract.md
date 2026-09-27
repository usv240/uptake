# The Uptake contract

The upgraded dependency version fixes known vulnerabilities. A repair that makes the build green by
undoing, weakening or hiding the upgrade is worse than no repair, because it ships the vulnerability
behind a passing build.

## You may
- Edit production Java under `src/main/java/`.
- Write `.uptake/rationale.md` (why each change preserves behaviour) and `.uptake/escalation.md`.
- Use the `explore` subagent to find every call site of a removed or changed API in parallel.

## You may not, and the audit will catch it if you try
- Change any test, build file (`pom.xml`), version, exclusion, or plugin configuration.
- Stub behaviour out: `throw new UnsupportedOperationException`, empty catch blocks, returning null or
  a default to make a type check pass.
- Use reflection to reach APIs that were removed.
- Delete or rename public methods of this project.

## Procedure
1. `uptake_status`, then `uptake_build`. Read the `apiEvidence` for every unresolved symbol. If the evidence
   does not make the replacement obvious, or tests fail because behaviour changed, call
   `uptake_release_notes` with the symbols involved and read what the library's maintainers wrote about the
   change. Quote the source URL in `.uptake/rationale.md` for anything you rely on.
2. Group the errors by root cause. For each: find the replacement API in the NEW version
   (`uptake_api_lookup`), then update every call site.
3. `uptake_build` after each group. Stop when status is SUCCESS and the number of tests run is at least
   `testsRunBeforeUpgrade`.
4. Write `.uptake/rationale.md`: one short bullet per change, citing the API evidence
   ("`X` was removed in 1.67; `Y` is its replacement, see deprecation note").

## Reading test failures
`uptake_build` returns `testFailureDetails`: the failing tests' own reports (assertion message, exception,
project stack frames). Read them before opening any file. `ClassNotFoundException` / `NoSuchMethodError` /
`NoClassDefFoundError` at test time usually mean a *companion* artifact (e.g. `log4j-api` next to
`log4j-core`) was left at the old version: that is a build-file problem, not a code problem.

## When to stop and escalate instead of forcing it green
Escalate, do not guess, when:
- the fix needs a build-file change (aligning a companion artifact, a new dependency, a plugin setting);
- the new version removed functionality with no replacement on the build classpath;
- a test fails because the library now *behaves* differently on purpose (a security fix changed a default).

Write `.uptake/escalation.md` with: the failing test or symbol, the evidence (quote the exception), and the
one decision a human must make. If you know the change that would fix it (a pom line, a test's import of a
moved library class), also write it to `.uptake/proposed.patch` as a `git diff`-style unified diff with
`a/` and `b/` paths relative to the project root. Uptake applies that patch in a scratch copy and proves
whether it goes green, so the human only has to approve it. Then stop.
A clear escalation with a proven patch is a correct outcome; editing the file yourself is not.
