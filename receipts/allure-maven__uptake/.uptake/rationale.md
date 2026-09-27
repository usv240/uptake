# Upgrade rationale: net.lingala.zip4j 1.3.2 → 2.10.0

- **`net.lingala.zip4j.core.ZipFile` import updated to `net.lingala.zip4j.ZipFile`**
  In zip4j 2.x the entire `net.lingala.zip4j.core` package was removed; `ZipFile` was promoted
  to the root package `net.lingala.zip4j`. The `extractAll(String)` method signature is
  identical in both versions, so no call-site changes were required (API evidence confirmed via
  `uptake_api_lookup`). Changed in
  `src/main/java/io/qameta/allure/maven/AllureCommandline.java` line 18.
