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
