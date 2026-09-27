# Upgrade receipt: org.apache.logging.log4j:log4j-core 2.12.1 -> 2.15.0

**Verdict: ESCALATED**

- Advisories removed by this upgrade: 2 (GHSA-jfh8-c2jp-5v3q, GHSA-vwqq-5vrc-xw9h)
- Before repair: TEST_FAILURE (0 compile errors, 42 failing tests)
- After repair: TEST_FAILURE, 67 tests run (project ran 67 before the upgrade), 43 failing
- Files changed: none (no diff)
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/ac14d8362de4:ready` (offline, --network none)
- Patch sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`


## Proposed patch for a human to approve: proven green: applying it makes the build and all tests pass (verified online: it needs artifacts the original image never downloaded)

- Touches: pom.xml
- Proposed patch sha256: `e140d370339aa11b7374b54c1a44f254c991ccf5bfa390d9099e0c0da6f448aa` (`.uptake/proposed.patch`)

## Escalation (the agent stopped and asked for a human decision)

# Escalation: log4j-core 2.15.0 — companion artifact version mismatch

## Failing tests (all 43 errors)

Every failing test throws one of:
```
java.lang.NoClassDefFoundError: Could not initialize class org.apache.logging.log4j.core.LoggerContext
```
or a cascading `UnfinishedMockingSessionException` caused by a prior test class failing to initialise.

## Root cause

`log4j-core` was upgraded from 2.12.1 to 2.15.0, but its companion artifact
`log4j-slf4j18-impl` was left at 2.12.1.  
`log4j-slf4j18-impl:2.12.1` depends on (and pins) `log4j-api:2.12.1`.  
`log4j-core:2.15.0`'s `LoggerContext` static initializer calls into `log4j-api` code that was
only added in 2.14/2.15, so the JVM throws `ExceptionInInitializerError` on first use, which
the classloader records as `NoClassDefFoundError: Could not initialize class
org.apache.logging.log4j.core.LoggerContext` on every subsequent attempt.

Evidence from the build classpath (as reported by `uptake_api_lookup`):
- `log4j-api` jar on classpath: `log4j-api-2.12.1.jar`  ← old
- `log4j-core` jar on classpath: `log4j-core-2.15.0.jar` ← new

This is a build-file problem: aligning the companion artifact requires a `pom.xml` change.

## Decision required

Bump `log4j-slf4j18-impl` from `2.12.1` to `2.15.0` in `pom.xml`.  
This will pull in `log4j-api:2.15.0`, matching `log4j-core:2.15.0`.  
`log4j-slf4j18-impl:2.15.0` is the last release of that artifact to support `slf4j-api:1.8.x`
(the version already declared in the pom), so no other dependency changes are needed.

The proposed patch below has been prepared for human review.

Re-verify from scratch: `python -m uptake verify <this folder>`
