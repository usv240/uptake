# Upgrade rationale: bcprov-jdk15on 1.51 → 1.67

## ChachaDecoder.java

- **Removed imports** `org.bouncycastle.crypto.tls.AlertDescription` and
  `org.bouncycastle.crypto.tls.TlsFatalAlert`: the entire `org.bouncycastle.crypto.tls`
  package was removed in 1.67 (confirmed via `uptake_api_lookup` — neither class exists
  in the new version or anywhere on the build classpath).

- **Replacement at line 28** (`throw new TlsFatalAlert(AlertDescription.bad_record_mac)`):
  `TlsFatalAlert` was a subclass of `java.io.IOException` whose sole purpose here was to
  signal MAC verification failure. The method already declares `throws IOException`.
  Replacing the throw with `new IOException("bad_record_mac")` preserves identical
  observable behaviour: the caller receives an `IOException` when the MAC does not match,
  with no change to the authentication check itself (the `Arrays.constantTimeAreEqual`
  guard is untouched).
