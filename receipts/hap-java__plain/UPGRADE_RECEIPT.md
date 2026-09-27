# Upgrade receipt: org.bouncycastle:bcprov-jdk15on 1.51 -> 1.67

**Verdict: REPAIRED**

- Advisories removed by this upgrade: 13 (GHSA-2j2x-hx4g-2gf4, GHSA-4vhj-98r6-424h, GHSA-6xx3-rg99-gc3p, GHSA-72m5-fvvv-55m6, GHSA-9gp4-qrff-c648, GHSA-c8xf-m4ff-jcxj, GHSA-fjqm-246c-mwqg, GHSA-qcj7-g2j5-g7r3, GHSA-r97x-3g8f-gx3m, GHSA-r9ch-m4fh-fc7q, GHSA-rrvx-pwf8-p59p, GHSA-w285-wf9q-5w69 ...)
- Before repair: COMPILATION_FAILURE (4 compile errors, 0 failing tests)
- After repair: SUCCESS, 12 tests run (project ran 12 before the upgrade), 0 failing
- Files changed: src/main/java/io/github/hapjava/server/impl/crypto/ChachaDecoder.java (1 file changed, 1 insertion(+), 3 deletions(-))
- Integrity violations: 0
- Behaviour-review warnings: 0
- Verified in: `uptake-local/6ad104c4fb92:ready` (offline, --network none)
- Patch sha256: `380c10136fc7ca12eea8d50c26a2153118609ed44234bcccf5acf965aec4e974`


## Why the code changed (agent's rationale)

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

Re-verify from scratch: `python -m uptake verify <this folder>`
