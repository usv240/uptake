# Upgrade receipt: mysql:mysql-connector-java 5.1.49 -> 8.0.28

**Verdict: REPAIRED**

- Advisories removed by this upgrade: 3 (GHSA-4vrv-ch96-6h42, GHSA-g76j-4cxx-23h9, GHSA-jcq3-cprp-m333)
- Before repair: COMPILATION_FAILURE (2 compile errors, 0 failing tests)
- After repair: SUCCESS, 291 tests run (project ran 291 before the upgrade), 0 failing
- Files changed: src/main/java/com/feedzai/commons/sql/abstraction/engine/impl/mysql/MySqlQueryExceptionHandler.java (1 file changed, 1 insertion(+), 1 deletion(-))
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/0305beafdecb:ready` (offline, --network none)
- Patch sha256: `4e251285fc881b5dd7376f313a40150694374db8f5ca381c19d4d302f212639f`


## Why the code changed (agent's rationale)

# Upgrade rationale: mysql-connector-java 5.1.49 → 8.0.28

## Changes

- **[`MySqlQueryExceptionHandler.java`](../src/main/java/com/feedzai/commons/sql/abstraction/engine/impl/mysql/MySqlQueryExceptionHandler.java:21)**
  Updated import from `com.mysql.jdbc.exceptions.MySQLTimeoutException` to
  `com.mysql.cj.jdbc.exceptions.MySQLTimeoutException`.

  **API evidence:** `com.mysql.jdbc.exceptions.MySQLTimeoutException` existed in 5.1.49 but was
  removed in 8.0.28 as part of the driver's migration to the new `com.mysql.cj` package hierarchy.
  The replacement class `com.mysql.cj.jdbc.exceptions.MySQLTimeoutException` is present in
  `mysql-connector-java-8.0.28.jar` with the same interface. The `instanceof` check and overall
  logic are unchanged; only the import is updated.

Re-verify from scratch: `python -m uptake verify <this folder>`
