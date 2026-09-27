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
