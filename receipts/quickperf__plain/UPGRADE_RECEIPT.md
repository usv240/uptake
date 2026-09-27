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

# Escalation: log4j-api companion artifact must be aligned to 2.16.0

## Failing test / symbol

```
java.lang.ClassNotFoundException: org.apache.logging.log4j.spi.LoggerContextShutdownAware
```

Observed in: `QuickPerfSpringRunnerBeforeAfterNewJvmTest.should_find_all_players`  
Cascade failures (NoClassDefFoundError) in all other tests in the `quick-perf-junit4-spring-boot-test` module.

## Evidence

`uptake_api_lookup` for `LoggerContextShutdownAware` returned:

> REMOVED: not in the new version and nothing with this name is on the build classpath.

The build classpath has `log4j-api-2.11.2.jar` (brought in transitively by `spring-boot-starter-log4j2` whose
version is governed by the Spring Boot 2.1.3 BOM). The interface `LoggerContextShutdownAware` was introduced
in `log4j-api` 2.12. With `log4j-core` upgraded to 2.16.0, the companion `log4j-api` artifact must be
upgraded to the same version. The project's production Java source **does not reference** this interface at all
— the class-load failure occurs inside Spring Test's `SpringJUnit4ClassRunner` which loads the interface at
init time via the log4j2 integration in `spring-test`.

## What a human must decide

Add an explicit `log4j-api` dependency at **2.16.0** to
`spring/junit4-spring-boot-test/pom.xml`, directly below the existing `log4j-core` override. This is a
build-file change and is therefore out of scope for automated repair.

## Proposed patch (proven equivalent)

See `proposed.patch`.

Re-verify from scratch: `python -m uptake verify <this folder>`
