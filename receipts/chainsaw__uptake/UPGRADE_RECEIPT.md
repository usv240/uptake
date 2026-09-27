# Upgrade receipt: com.thoughtworks.xstream:xstream 1.4.17 -> 1.4.19

**Verdict: ESCALATED**

- Advisories removed by this upgrade: 15 (GHSA-2q8x-2p7f-574v, GHSA-3ccq-5vw3-2p6x, GHSA-64xx-cq4q-mf44, GHSA-6w62-hx7r-mw68, GHSA-6wf9-jmg9-vxcc, GHSA-8jrj-525p-826v, GHSA-cxfm-5m4g-x7xp, GHSA-g5w6-mrj7-75h2, GHSA-h7v4-7xg3-hxcc, GHSA-hph2-m3g5-xxv4, GHSA-j9h8-phrw-h4fh, GHSA-p8pq-r894-fm8f ...)
- Before repair: TEST_FAILURE (0 compile errors, 1 failing tests)
- After repair: TEST_FAILURE, 5 tests run (project ran 5 before the upgrade), 1 failing
- Files changed: none (no diff)
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/19e20b0d69cb:ready` (offline, --network none)
- Patch sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`


## Proposed patch for a human to approve: proven green: applying it makes the build and all tests pass

- Touches: src/test/java/org/apache/log4j/chainsaw/LogPanelPreferenceModelTest.java
- Proposed patch sha256: `09ccef131f1c1d3bca2c6dca731a2971cdeb1b11fd8831c93f23831ffaa62cf5` (`.uptake/proposed.patch`)

## Escalation (the agent stopped and asked for a human decision)

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

Re-verify from scratch: `python -m uptake verify <this folder>`
