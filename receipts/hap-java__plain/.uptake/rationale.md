# Upgrade rationale — bcprov-jdk15on 1.51 → 1.67

## ChachaDecoder.java

- `org.bouncycastle.crypto.tls.AlertDescription` was removed in bcprov-jdk15on 1.67;
  `AlertDescription.bad_record_mac` was only used as a numeric argument to `TlsFatalAlert`.
- `org.bouncycastle.crypto.tls.TlsFatalAlert` was removed in bcprov-jdk15on 1.67
  (the entire `org.bouncycastle.crypto.tls` package was extracted into a separate
  `bcpkix`/`bctls` artifact). `TlsFatalAlert` extended `java.io.IOException`.

**Change:** Both imports were deleted and the `throw new TlsFatalAlert(AlertDescription.bad_record_mac)`
was replaced with `throw new IOException("bad_record_mac")`.

**Behaviour preserved:** The method signature already declares `throws IOException` and callers
catch/handle `IOException`. `TlsFatalAlert` was itself an `IOException` subclass, so throwing a
plain `IOException` with an equivalent message string preserves the observable failure contract
— a MAC mismatch still aborts the decryption with an `IOException`.
