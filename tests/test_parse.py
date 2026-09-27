"""Maven log parsing and the evidence extracted from compile errors."""
from uptake import apidiff, container

COMPILE_LOG = """[INFO] Compiling 40 source files
[ERROR] COMPILATION ERROR :
[ERROR] /HAP-Java/src/main/java/io/x/ChachaDecoder.java:[8,35] package org.bouncycastle.crypto.tls does not exist
[ERROR] /HAP-Java/src/main/java/io/x/ChachaDecoder.java:[31,17] cannot find symbol
[ERROR] /HAP-Java/src/main/java/io/x/ChachaDecoder.java:[31,17] cannot find symbol
[ERROR]   symbol:   class TlsFatalAlert
[ERROR]   location: class io.x.ChachaDecoder
[INFO] BUILD FAILURE
"""

TEST_LOG = """[INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 1.2 s - in a.ATest
[ERROR] Tests run: 3, Failures: 1, Errors: 1, Skipped: 0, Time elapsed: 0.1 s <<< FAILURE! - in a.BTest
[INFO] Results:
[ERROR] Failures:
[ERROR]   BTest.should_parse:42 expected:<1> but was:<2>
[ERROR] Errors:
[ERROR]   BTest.should_load:17 » ClassNotFound org.apache.logging.log4j.spi.X
[ERROR] Tests run: 15, Failures: 1, Errors: 1, Skipped: 0
[INFO] BUILD FAILURE
There are test failures.
"""


def test_parse_compile_errors_dedupes_and_merges_detail():
    r = container.parse(COMPILE_LOG, "/HAP-Java")
    assert r["status"] == "COMPILATION_FAILURE"
    assert [(e["line"], e["col"]) for e in r["compileErrors"]] == [(8, 35), (31, 17)]
    assert r["compileErrors"][0]["file"] == "src/main/java/io/x/ChachaDecoder.java"
    assert "symbol: class TlsFatalAlert" in r["compileErrors"][1]["detail"]


def test_parse_test_failures_counts_summary_only():
    r = container.parse(TEST_LOG, "/p")
    assert r["status"] == "TEST_FAILURE"
    assert r["tests"] == {"run": 15, "failures": 1, "errors": 1, "skipped": 0}


def test_parse_success_and_timeout():
    assert container.parse("[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0\n[INFO] BUILD SUCCESS", "/p")["status"] == "SUCCESS"
    assert container.parse("[INFO] Running\n" + container.TIMEOUT_MARK, "/p")["status"] == "TIMEOUT"


def test_symbols_from_errors():
    r = container.parse(COMPILE_LOG, "/HAP-Java")
    syms = apidiff.symbols_from_errors(r["compileErrors"])
    assert ("org.bouncycastle.crypto.tls", None) in syms
    assert ("TlsFatalAlert", None) in syms


def test_condensed_reports_drop_framework_frames():
    text = "java.lang.AssertionError: boom\n\tat org.junit.Assert.fail(Assert.java:1)\n\tat a.BTest.t(BTest.java:9)\n"
    out = container._condense_reports(text)
    assert "AssertionError: boom" in out and "a.BTest.t" in out and "org.junit" not in out
