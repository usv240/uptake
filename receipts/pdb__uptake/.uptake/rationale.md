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
