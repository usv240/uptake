# Upgrade receipt: org.yaml:snakeyaml 1.33 -> 2.0

**Verdict: ESCALATED**

- Advisories removed by this upgrade: 1 (GHSA-mjmj-j48q-9wg2)
- Before repair: COMPILATION_FAILURE (2 compile errors, 0 failing tests)
- After repair: COMPILATION_FAILURE, 10 tests run (project ran 753 before the upgrade), 0 failing
- Files changed: none (no diff)
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/b1a941400d68:ready` (offline, --network none)
- Patch sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`


## Proposed patch for a human to approve: applies, build TEST_FAILURE

- Touches: compiler/src/test/java/com/fluxtion/compiler/builder/factory/GraphOfInstancesTest.java
- Proposed patch sha256: `852cbcd16ff24157f61221585a461ba7a213dfe4841bb203eaade1c0e75146e6` (`.uptake/proposed.patch`)

## Escalation (the agent stopped and asked for a human decision)

# Escalation: SnakeYAML 1.33 → 2.0

## Failing symbol

`org.yaml.snakeyaml.constructor.Constructor()` — no-argument constructor.

## Evidence

```
compiler/src/test/java/com/fluxtion/compiler/builder/factory/GraphOfInstancesTest.java:[78,39]
  no suitable constructor found for Constructor(no arguments)

compiler/src/test/java/com/fluxtion/compiler/builder/factory/GraphOfInstancesTest.java:[114,39]
  no suitable constructor found for Constructor(no arguments)
```

In SnakeYAML 1.33 `Constructor` had a public no-arg constructor. In 2.0 **all** constructors require
a `LoaderOptions` argument as the last parameter (the no-arg form was already `@Deprecated` in 1.x
with the Javadoc note *"use options"*). The class still exists in 2.0 but every overload now mandates
`LoaderOptions`.

The two call sites are both inside `GraphOfInstancesTest.java`, a **test** file that cannot be
touched under the Uptake contract. The import is `org.yaml.snakeyaml.constructor.Constructor`
directly — there is no production-code shim that could intercept this.

## Decision a human must make

The test file `GraphOfInstancesTest.java` must be updated to pass a `new LoaderOptions()` to the
`Constructor` constructor. Because this is a test file, a human approver must authorise the change.

The proposed patch is in `.uptake/proposed.patch`. It is minimal: only the two `new Constructor()`
calls are modified.

Re-verify from scratch: `python -m uptake verify <this folder>`
