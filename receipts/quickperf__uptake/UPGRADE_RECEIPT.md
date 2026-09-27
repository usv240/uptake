# Upgrade receipt: org.apache.logging.log4j:log4j-core 2.11.1 -> 2.16.0

**Verdict: FAILED**

- Advisories removed by this upgrade: 3 (GHSA-7rjr-3q55-vv33, GHSA-jfh8-c2jp-5v3q, GHSA-vwqq-5vrc-xw9h)
- Before repair: TEST_FAILURE (0 compile errors, 13 failing tests)
- After repair: TEST_FAILURE, 309 tests run (project ran 309 before the upgrade), 10 failing
- Files changed: none (no diff)
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/9069046236a0:ready` (offline, --network none)
- Patch sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`


Re-verify from scratch: `python -m uptake verify <this folder>`
