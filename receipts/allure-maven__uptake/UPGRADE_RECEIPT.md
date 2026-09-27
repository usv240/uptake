# Upgrade receipt: net.lingala.zip4j:zip4j 1.3.2 -> 2.10.0

**Verdict: COMPILES_UNTESTED**

> This project had no tests before the upgrade, so this proves it compiles, not that it behaves.

- Advisories removed by this upgrade: 2 (GHSA-2rpm-4x8c-pvqg, GHSA-q62h-jw38-24vh)
- Before repair: COMPILATION_FAILURE (1 compile errors, 0 failing tests)
- After repair: SUCCESS, 0 tests run (project ran 0 before the upgrade), 0 failing
- Files changed: src/main/java/io/qameta/allure/maven/AllureCommandline.java (1 file changed, 1 insertion(+), 1 deletion(-))
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/54857351e0b0:ready` (offline, --network none)
- Patch sha256: `c7951952123cc0c6d505f49bda9a948e7edd58e14b4ed09b6e95f02ca6b29469`


## Why the code changed (agent's rationale)

# Upgrade rationale: net.lingala.zip4j 1.3.2 → 2.10.0

- **`net.lingala.zip4j.core.ZipFile` import updated to `net.lingala.zip4j.ZipFile`**
  In zip4j 2.x the entire `net.lingala.zip4j.core` package was removed; `ZipFile` was promoted
  to the root package `net.lingala.zip4j`. The `extractAll(String)` method signature is
  identical in both versions, so no call-site changes were required (API evidence confirmed via
  `uptake_api_lookup`). Changed in
  `src/main/java/io/qameta/allure/maven/AllureCommandline.java` line 18.

Re-verify from scratch: `python -m uptake verify <this folder>`
