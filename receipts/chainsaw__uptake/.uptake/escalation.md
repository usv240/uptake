# Escalation: ForbiddenClassException in LogPanelPreferenceModelTest

## Failing test

`org.apache.log4j.chainsaw.LogPanelPreferenceModelTest#testLogPanelPreferenceModelSerialization`

## Evidence

```
com.thoughtworks.xstream.security.ForbiddenClassException: org.apache.log4j.chainsaw.LogPanelPreferenceModel
    at com.thoughtworks.xstream.security.NoTypePermission.allows(NoTypePermission.java:26)
    at com.thoughtworks.xstream.mapper.SecurityMapper.realClass(SecurityMapper.java:74)
    ...
    at com.thoughtworks.xstream.XStream.fromXML(XStream.java:1275)
    at org.apache.log4j.chainsaw.LogPanelPreferenceModelTest.testLogPanelPreferenceModelSerialization(LogPanelPreferenceModelTest.java:47)
```

## Root cause

XStream 1.4.18 (included in the 1.4.19 upgrade) changed the default security policy
from "allow all" to "deny all" (`NoTypePermission`). Any class not explicitly
whitelisted is now rejected during deserialization.

The test at `LogPanelPreferenceModelTest.java:43` constructs its own `XStream` instance:

```java
XStream stream = new XStream(new DomDriver());          // deny-all after 1.4.18
String xml = stream.toXML(model);                       // serialization works
LogPanelPreferenceModel restored =
    (LogPanelPreferenceModel) stream.fromXML(xml);      // THROWS ForbiddenClassException
```

Because the `XStream` instance is created entirely inside the test, there is no
production-code hook available to add the required type permission. The only correct
fix is to call `stream.allowTypes(...)` (or `stream.allowTypesByWildcard(...)`) on
the test's own instance before `fromXML` is called.

## Decision required

A human must approve adding `allowTypes` to the test. This is the only safe fix;
no production-code-only solution exists.

## Proposed change

See `proposed.patch` — it adds
`stream.allowTypesByWildcard(new String[]{"org.apache.log4j.chainsaw.**"})` to the
test immediately after the `XStream` instance is created, and adds the necessary
import for `com.thoughtworks.xstream.security.AnyTypePermission` (not needed here,
`allowTypesByWildcard` is already available directly on `XStream`). The patch is
self-contained and does not change any assertion or logic.
