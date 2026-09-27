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

# Escalation: snakeyaml 1.33 → 2.0

## Failing symbols

`org.yaml.snakeyaml.constructor.Constructor()` — the no-argument constructor was removed in snakeyaml 2.0.
All remaining constructors now require at least a `LoaderOptions` argument.

## Evidence

```
[ERROR] .../GraphOfInstancesTest.java:[78,39] no suitable constructor found for Constructor(no arguments)
[ERROR]     constructor org.yaml.snakeyaml.constructor.Constructor.Constructor(org.yaml.snakeyaml.LoaderOptions) is not applicable
[ERROR]       (actual and formal argument lists differ in length)
...
[ERROR] .../GraphOfInstancesTest.java:[114,39] no suitable constructor found for Constructor(no arguments)
```

## Root cause

The test file `compiler/src/test/java/com/fluxtion/compiler/builder/factory/GraphOfInstancesTest.java`
directly imports and instantiates `org.yaml.snakeyaml.constructor.Constructor` with no arguments (lines 78
and 114). In snakeyaml 2.0 the zero-argument constructor was removed (it had been deprecated since 1.18
with the note "use options"). The only constructors now available are:

- `Constructor(LoaderOptions)`
- `Constructor(Class<?>, LoaderOptions)`
- `Constructor(TypeDescription, LoaderOptions)`
- `Constructor(TypeDescription, Collection<TypeDescription>, LoaderOptions)`
- `Constructor(String, LoaderOptions)`

## Decision needed

The test source file must be updated to pass `new LoaderOptions()` to each `Constructor` call.
This is a test-file change and cannot be made under the Uptake contract, which restricts edits to
`src/main/java/`.

## Proposed patch

See `.uptake/proposed.patch`.

Re-verify from scratch: `python -m uptake verify <this folder>`
