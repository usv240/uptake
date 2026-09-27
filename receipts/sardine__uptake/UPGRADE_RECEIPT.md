# Upgrade receipt: org.apache.httpcomponents:httpclient 4.5.1 -> 4.5.13

**Verdict: REPAIRED**

- Advisories removed by this upgrade: 1 (GHSA-7r82-7xv7-xcpj)
- Before repair: TEST_FAILURE (0 compile errors, 0 failing tests)
- After repair: SUCCESS, 26 tests run (project ran 26 before the upgrade), 0 failing
- Files changed: src/main/java/com/github/sardine/impl/SardineException.java (1 file changed, 3 insertions(+), 1 deletion(-))
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/d4aade950ffc:ready` (offline, --network none)
- Patch sha256: `91fcdb9ffc7d59c884751f8a5bdb572e0dff6a354f5bcb6404a10374d14f6a61`


Re-verify from scratch: `python -m uptake verify <this folder>`
