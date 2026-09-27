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
