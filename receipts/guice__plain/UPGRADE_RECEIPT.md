# Upgrade receipt: org.apache.struts:struts2-core 2.3.37 -> 2.5.22

**Verdict: ESCALATED**

- Advisories removed by this upgrade: 3 (GHSA-8m5q-crqq-6pmf, GHSA-ccp5-gg58-pxfm, GHSA-wp4h-pvgw-5727)
- Before repair: COMPILATION_FAILURE (3 compile errors, 0 failing tests)
- After repair: COMPILATION_FAILURE, 5405 tests run (project ran 5787 before the upgrade), 0 failing
- Files changed: none (no diff)
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/acc50dabec67:ready` (offline, --network none)
- Patch sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`


## Proposed patch for a human to approve: proven green: applying it makes the build and all tests pass

- Touches: extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java
- Proposed patch sha256: `4da5a6d1976f2c2979b4ac85d7e271f55dc912da65f048be39b784516bebfefe` (`.uptake/proposed.patch`)

## Escalation (the agent stopped and asked for a human decision)

# Escalation

## Failing symbol

`org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter`  
in `extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java`, line 19.

## Evidence

```
error: package org.apache.struts2.dispatcher.ng.filter does not exist
```

API lookup confirms:

- **Old version (2.3.37):** `org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter`
- **New version (2.5.22):** `org.apache.struts2.dispatcher.filter.StrutsPrepareAndExecuteFilter`
  (present on the build classpath in `struts2-core-2.5.22.jar`)

The `ng.filter` subpackage was removed entirely in Struts 2.5; all its filter classes were
promoted to `org.apache.struts2.dispatcher.filter`.

## Why this cannot be fixed in production code

The only broken file is the **test** file `Struts2FactoryTest.java`. The production source
(`Struts2Factory.java`, `Struts2GuicePluginModule.java`, etc.) does not reference the old package.
The contract forbids editing test files, so this repair requires a human to approve the patch below.

## Decision needed

Update the import in the test file from the removed `ng.filter` package to the new
`dispatcher.filter` package. See `proposed.patch`.

Re-verify from scratch: `python -m uptake verify <this folder>`
