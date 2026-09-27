# Upgrade receipt: org.apache.logging.log4j:log4j-core 2.11.1 -> 2.16.0

**Verdict: ESCALATED**

- Advisories removed by this upgrade: 3 (GHSA-7rjr-3q55-vv33, GHSA-jfh8-c2jp-5v3q, GHSA-vwqq-5vrc-xw9h)
- Before repair: TEST_FAILURE (0 compile errors, 13 failing tests)
- After repair: TEST_FAILURE, 309 tests run (project ran 309 before the upgrade), 10 failing
- Files changed: none (no diff)
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/9069046236a0:ready` (offline, --network none)
- Patch sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`


## Proposed patch for a human to approve: proven green: applying it makes the build and all tests pass (verified online: it needs artifacts the original image never downloaded)

- Touches: spring/junit4-spring-boot-test/pom.xml
- Proposed patch sha256: `da101f41654c8adf489f40234115b88b68b3c2f10fe7cb41ef34f40a19052bc3` (`.uptake/proposed.patch`)

## Escalation (the agent stopped and asked for a human decision)

# Escalation

## Failing tests

All 10 failing tests in `quick-perf-junit4-spring-boot-test`.

Root cause test (direct):
- `QuickPerfSpringRunnerBeforeAfterNewJvmTest.should_find_all_players`
  → `java.lang.ClassNotFoundException: org.apache.logging.log4j.spi.LoggerContextShutdownAware`

All other failures cascade from this:
- `NoClassDefFoundError: Could not initialize class org.quickperf.spring.junit4.SpringRunnerWithQuickPerfFeatures`
- `NoClassDefFoundError: Could not initialize class org.quickperf.spring.junit4.SpringRunnerWithCallableProtectedMethods`
- `NoClassDefFoundError: Could not initialize class org.springframework.test.context.junit4.SpringJUnit4ClassRunner`

## Evidence

```
java.lang.ClassNotFoundException: org.apache.logging.log4j.spi.LoggerContextShutdownAware
```

`LoggerContextShutdownAware` is an interface that lives in `log4j-api` (not `log4j-core`). It was
**introduced in `log4j-api` 2.12.0**. The project's `pom.xml` upgraded `log4j-core` to `2.16.0`, but
`log4j-api` is still managed at `2.11.1` by the `spring-boot-starter-parent 2.1.3.RELEASE` BOM.

`log4j-core` 2.16.0 loads `LoggerContextShutdownAware` from `log4j-api` at class-initialisation time
(used by `AsyncLogger`, which is referenced in `src/test/resources/log4j2.xml`). Because `log4j-api`
is at `2.11.1`, the class does not exist and the JVM throws `ClassNotFoundException`.

## Decision required

Add an explicit `log4j-api` version pin in
`spring/junit4-spring-boot-test/pom.xml` to align it with the upgraded `log4j-core`:

```xml
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>2.16.0</version>
</dependency>
```

This must be placed alongside the existing `log4j-core` 2.16.0 entry.

The proposed patch is in `.uptake/proposed.patch`.

Re-verify from scratch: `python -m uptake verify <this folder>`
