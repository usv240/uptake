# Upgrade receipt: org.liquibase:liquibase-core 3.4.2 -> 4.8.0

**Verdict: FAILED**

- Advisories removed by this upgrade: 1 (GHSA-jvfv-hrrc-6q72)
- Before repair: COMPILATION_FAILURE (5 compile errors, 0 failing tests)
- After repair: TEST_FAILURE, 4 tests run (project ran 4 before the upgrade), 4 failing
- Files changed: src/java/liquibase/ext/mssql/database/MSSQLDatabase.java, src/java/liquibase/ext/mssql/sqlgenerator/AddPrimaryKeyGeneratorMSSQL.java, src/java/liquibase/ext/mssql/sqlgenerator/CreateIndexGeneratorMSSQL.java (3 files changed, 6 insertions(+), 5 deletions(-))
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/feb582661e77:ready` (offline, --network none)
- Patch sha256: `cec4ccdbbc6a06b4baf973c4f9f8239a27ca03df2dc220c35a8cd2ad4711b4d7`


Re-verify from scratch: `python -m uptake verify <this folder>`
