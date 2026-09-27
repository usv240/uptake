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
