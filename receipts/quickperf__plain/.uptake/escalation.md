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
