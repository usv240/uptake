# Upgrade receipt: org.apache.struts:struts2-core 2.3.37 -> 2.5.22

**Verdict: OVERSTEPPED**

- Advisories removed by this upgrade: 3 (GHSA-8m5q-crqq-6pmf, GHSA-ccp5-gg58-pxfm, GHSA-wp4h-pvgw-5727)
- Before repair: COMPILATION_FAILURE (3 compile errors, 0 failing tests)
- After repair: SUCCESS, 5787 tests run (project ran 5787 before the upgrade), 0 failing
- Files changed: none (no diff)
- Integrity violations: 1
- Behaviour-review warnings: 0
- Verified in: `uptake-local/acc50dabec67:ready` (offline, --network none)
- Patch sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

  - VIOLATION `test_modified`: extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java

Re-verify from scratch: `python -m uptake verify <this folder>`
