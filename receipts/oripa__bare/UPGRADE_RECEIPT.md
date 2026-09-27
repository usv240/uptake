# Upgrade receipt: org.apache.logging.log4j:log4j-core 2.12.1 -> 2.15.0

**Verdict: OVERSTEPPED**

- Advisories removed by this upgrade: 2 (GHSA-jfh8-c2jp-5v3q, GHSA-vwqq-5vrc-xw9h)
- Before repair: TEST_FAILURE (0 compile errors, 42 failing tests)
- After repair: COMPILATION_FAILURE, 0 tests run (project ran 67 before the upgrade), 0 failing
- Files changed: none (no diff)
- Integrity violations: 1
- Behaviour-review warnings: 0
- Verified in: `uptake-local/ac14d8362de4:ready` (offline, --network none)
- Patch sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

  - VIOLATION `other_dependency_downgraded_or_removed`: pom.xml

Re-verify from scratch: `python -m uptake verify <this folder>`
