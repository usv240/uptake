# Upgrade rationale: org.jasypt:jasypt 1.8 → 1.9.2

## Changes

### `GeoStoreDigestPasswordEncoder.java`
- **Removed import**: `org.jasypt.spring.security.PasswordEncoder`  
  This class was dropped entirely in jasypt 1.9 — `apiEvidence` verdict: REMOVED, not in new version, nothing on classpath.
- **Added import**: `org.acegisecurity.providers.encoding.PasswordEncoder`  
  The old jasypt `PasswordEncoder` was itself an implementation of the acegi `PasswordEncoder` interface (already used as the return type of `createStringEncoder()` in the abstract base class). Switching the import to the interface directly is correct — no behaviour change.
- **Replaced `createStringEncoder()` body**: The old code instantiated `org.jasypt.spring.security.PasswordEncoder` (a concrete class) and called `setPasswordEncryptor(new StrongPasswordEncryptor())`. The replacement creates an anonymous `org.acegisecurity.providers.encoding.PasswordEncoder` that delegates to `StrongPasswordEncryptor.encryptPassword()` and `StrongPasswordEncryptor.checkPassword()` — the exact same methods the removed class delegated to internally. `StrongPasswordEncryptor` is present unchanged in 1.9.2.

### `GeoStorePBEPasswordEncoder.java`
- **Removed import**: `org.jasypt.spring.security.PBEPasswordEncoder`  
  Dropped in jasypt 1.9 — `apiEvidence` verdict: REMOVED, not in new version, nothing on classpath with that name.
- **Replaced `PBEPasswordEncoder` instantiation** in `createStringEncoder()`: The old `PBEPasswordEncoder.setPbeStringEncryptor(stringEncrypter)` wrapped a `StandardPBEStringEncryptor` and exposed it as an acegi `PasswordEncoder` by calling `encrypt()` / `decrypt()`. The replacement creates an anonymous `org.acegisecurity.providers.encoding.PasswordEncoder` (already imported in this file via the acegi import retained from line 31) that calls `stringEncrypter.encrypt(rawPass)` and `stringEncrypter.decrypt(encPass).equals(rawPass)` directly — identical behaviour. `StandardPBEStringEncryptor` is present unchanged in 1.9.2.
