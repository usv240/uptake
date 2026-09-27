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
- Proposed patch sha256: `d3f9a7814e379691a2664eb682016413b1579ea5f650ab3d3cea151530577b0e` (`.uptake/proposed.patch`)

## Escalation (the agent stopped and asked for a human decision)

# Escalation: companion artifact version mismatch

## Failing symptom

All 43 failing tests throw:

```
java.lang.NoClassDefFoundError: Could not initialize class org.apache.logging.log4j.core.LoggerContext
```

The very first test that touches any class with an SLF4J logger field (e.g., `OverlappingLineExtractor`,
`LineAdder`) causes `LoggerContext.<clinit>` to crash. Every subsequent test in the same JVM process that
touches any class relying on SLF4J then fails with `NoClassDefFoundError` for that class, and tests using
Mockito sessions that were opened before this crash surface as `UnfinishedMockingSessionException`
(a cascade).

## Root cause

The `pom.xml` contains two log4j artifacts at **mismatched versions**:

| artifact | version |
|---|---|
| `org.apache.logging.log4j:log4j-core` | **2.15.0** (upgraded) |
| `org.apache.logging.log4j:log4j-slf4j18-impl` | **2.12.1** (unchanged companion) |

`log4j-slf4j18-impl:2.12.1` was compiled against `log4j-core:2.12.1` internal APIs. Between 2.12.1 and
2.15.0 the `StatusLogger.EMPTY` field was removed (or its type changed), causing a
`NoSuchFieldError: EMPTY` inside `LoggerContext`'s static initializer, which then leaves `LoggerContext`
permanently uninitializable for the lifetime of the JVM.

## Evidence

- `target/surefire-reports/oripa.domain.cptool.OverlappingLineExtractorTest.txt`:
  > `java.lang.NoClassDefFoundError: Could not initialize class org.apache.logging.log4j.core.LoggerContext`  
  > `at oripa.domain.cptool.OverlappingLineExtractorTest.testExtract_ofSpecifiedLine(OverlappingLineExtractorTest.java:82)`

- `uptake_build` error log tail: `NoSuchField EMPTY` for `OverlappingLineExtractorTest.testExtract_ofSpecifiedLine`

- `uptake_api_lookup` for `Log4jLoggerFactory` confirms:
  > `log4j-slf4j18-impl:2.12.1` is the only version on the build classpath; no 2.15.0 jar is available.

## Decision required

Bump `log4j-slf4j18-impl` from `2.12.1` to `2.15.0` in `pom.xml`. This is the companion artifact that
must always ship at the same version as `log4j-core`. The proposed patch below makes this change.

All 43 failing tests are caused exclusively by this version mismatch. No production code changes are
needed.

Re-verify from scratch: `python -m uptake verify <this folder>`
