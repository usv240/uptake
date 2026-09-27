# Upgrade receipt: org.apache.struts:struts2-core 2.3.37 -> 2.5.22

**Verdict: ESCALATED**

- Advisories removed by this upgrade: 3 (GHSA-8m5q-crqq-6pmf, GHSA-ccp5-gg58-pxfm, GHSA-wp4h-pvgw-5727)
- Before repair: COMPILATION_FAILURE (3 compile errors, 0 failing tests)
- After repair: COMPILATION_FAILURE, 5405 tests run (project ran 5787 before the upgrade), 0 failing
- Files changed: none (no diff)
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/acc50dabec67:ready` (offline, --network none)
- Patch sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`


## Proposed patch for a human to approve: proven green: applying it makes the build and all tests pass

- Touches: extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java
- Proposed patch sha256: `4da5a6d1976f2c2979b4ac85d7e271f55dc912da65f048be39b784516bebfefe` (`.uptake/proposed.patch`)

## Escalation (the agent stopped and asked for a human decision)

# Escalation: test file import of removed package

## Failing symbol

`org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter`
in `extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java` line 19.

## Evidence

struts2-core 2.3.37 placed `StrutsPrepareAndExecuteFilter` in the package
`org.apache.struts2.dispatcher.ng.filter`.

struts2-core 2.5.22 removed that entire package (`ng.filter`). The class was
relocated to `org.apache.struts2.dispatcher.filter.StrutsPrepareAndExecuteFilter`
(confirmed by `uptake_api_lookup`; the class is present in
`struts2-core-2.5.22.jar` on the build classpath).

All three compiler errors in `Struts2FactoryTest.java` (lines 19, 55, 57)
are caused by this single stale import.

## Why this requires human approval

The only fix is to update the import in the test file
`extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java`.
The Uptake contract prohibits editing test files without human approval.

## Proposed change

See `.uptake/proposed.patch` — a one-line import replacement that makes the
build green without weakening the security upgrade.

Re-verify from scratch: `python -m uptake verify <this folder>`
