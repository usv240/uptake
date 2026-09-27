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
