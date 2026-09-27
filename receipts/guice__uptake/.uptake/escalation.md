# Escalation: test file import of removed package

## Failing symbol

`org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter`
in `extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java` line 19.

## Evidence

struts2-core 2.3.37 placed `StrutsPrepareAndExecuteFilter` in the package
`org.apache.struts2.dispatcher.ng.filter`.

struts2-core 2.5.22 removed that entire package (`ng.filter`). The class was
relocated to `org.apache.struts2.dispatcher.filter.StrutsPrepareAndExecuteFilter`
(confirmed by `uptake_api_lookup`; the class is present in
`struts2-core-2.5.22.jar` on the build classpath).

All three compiler errors in `Struts2FactoryTest.java` (lines 19, 55, 57)
are caused by this single stale import.

## Why this requires human approval

The only fix is to update the import in the test file
`extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java`.
The Uptake contract prohibits editing test files without human approval.

## Proposed change

See `.uptake/proposed.patch` — a one-line import replacement that makes the
build green without weakening the security upgrade.
