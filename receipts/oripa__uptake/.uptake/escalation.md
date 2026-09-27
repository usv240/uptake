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
