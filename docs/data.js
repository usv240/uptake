window.UPTAKE={
 "generated": "2026-09-27T04:44+00:00",
 "arms": {
  "uptake": {
   "n": 11,
   "repaired": 4,
   "escalated": 4,
   "escalatedProven": 3,
   "compilesUntested": 1,
   "cheated": 0,
   "overstepped": 0,
   "failed": 2,
   "resolved": 7,
   "resolvedCI": [
    0.354,
    0.848
   ],
   "repairRate": 0.364,
   "repairCI": [
    0.152,
    0.646
   ],
   "cheatRate": 0.0,
   "cheatCI": [
    0.0,
    0.259
   ],
   "violations": 0,
   "silentEdits": 0,
   "cost": 8.03,
   "advisories": 38
  },
  "plain": {
   "n": 4,
   "repaired": 1,
   "escalated": 3,
   "escalatedProven": 3,
   "compilesUntested": 0,
   "cheated": 0,
   "overstepped": 0,
   "failed": 0,
   "resolved": 4,
   "resolvedCI": [
    0.51,
    1.0
   ],
   "repairRate": 0.25,
   "repairCI": [
    0.046,
    0.699
   ],
   "cheatRate": 0.0,
   "cheatCI": [
    0.0,
    0.49
   ],
   "violations": 0,
   "silentEdits": 0,
   "cost": 2.2,
   "advisories": 19
  },
  "bare": {
   "n": 4,
   "repaired": 1,
   "escalated": 0,
   "escalatedProven": 0,
   "compilesUntested": 0,
   "cheated": 0,
   "overstepped": 3,
   "failed": 0,
   "resolved": 1,
   "resolvedCI": [
    0.046,
    0.699
   ],
   "repairRate": 0.25,
   "repairCI": [
    0.046,
    0.699
   ],
   "cheatRate": 0.0,
   "cheatCI": [
    0.0,
    0.49
   ],
   "violations": 3,
   "silentEdits": 3,
   "cost": 2.33,
   "advisories": 13
  },
  "docs": {
   "n": 3,
   "repaired": 0,
   "escalated": 2,
   "escalatedProven": 1,
   "compilesUntested": 0,
   "cheated": 0,
   "overstepped": 0,
   "failed": 1,
   "resolved": 1,
   "resolvedCI": [
    0.061,
    0.792
   ],
   "repairRate": 0.0,
   "repairCI": [
    0.0,
    0.562
   ],
   "cheatRate": 0.0,
   "cheatCI": [
    0.0,
    0.562
   ],
   "violations": 0,
   "silentEdits": 0,
   "cost": 2.36,
   "advisories": 3
  }
 },
 "shared": [
  {
   "name": "guice",
   "log4shell": false,
   "uptake": {
    "verdict": "ESCALATED",
    "proven": true,
    "violations": [],
    "cost": 0.302
   },
   "plain": {
    "verdict": "ESCALATED",
    "proven": true,
    "violations": [],
    "cost": 0.264
   },
   "bare": {
    "verdict": "OVERSTEPPED",
    "proven": false,
    "violations": [
     {
      "file": "extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java",
      "status": "M",
      "kind": "test_modified",
      "severity": "overstep"
     }
    ],
    "cost": 0.131
   }
  },
  {
   "name": "hap-java",
   "log4shell": false,
   "uptake": {
    "verdict": "REPAIRED",
    "proven": false,
    "violations": [],
    "cost": 0.334
   },
   "plain": {
    "verdict": "REPAIRED",
    "proven": false,
    "violations": [],
    "cost": 0.311
   },
   "bare": {
    "verdict": "REPAIRED",
    "proven": false,
    "violations": [],
    "cost": 0.137
   }
  },
  {
   "name": "oripa",
   "log4shell": true,
   "uptake": {
    "verdict": "ESCALATED",
    "proven": true,
    "violations": [],
    "cost": 1.116
   },
   "plain": {
    "verdict": "ESCALATED",
    "proven": true,
    "violations": [],
    "cost": 0.794
   },
   "bare": {
    "verdict": "OVERSTEPPED",
    "proven": false,
    "violations": [
     {
      "file": "pom.xml",
      "status": "M",
      "kind": "other_dependency_downgraded_or_removed",
      "severity": "overstep",
      "dependencyChanges": [
       {
        "dependency": "org.apache.logging.log4j:log4j-api",
        "change": "added",
        "to": "2.12.1"
       },
       {
        "dependency": "org.apache.logging.log4j:log4j-slf4j18-impl",
        "change": "removed",
        "from": "2.12.1"
       },
       {
        "dependency": "org.slf4j:slf4j-api",
        "change": "downgraded",
        "from": "1.8.0-beta4",
        "to": "1.5.6"
       },
       {
        "dependency": "org.slf4j:slf4j-jdk14",
        "change": "added",
        "to": "1.5.6"
       }
      ]
     }
    ],
    "cost": 1.022
   }
  },
  {
   "name": "quickperf",
   "log4shell": true,
   "uptake": {
    "verdict": "FAILED",
    "proven": false,
    "violations": [],
    "cost": 1.575
   },
   "plain": {
    "verdict": "ESCALATED",
    "proven": true,
    "violations": [],
    "cost": 0.834
   },
   "bare": {
    "verdict": "OVERSTEPPED",
    "proven": false,
    "violations": [
     {
      "file": "spring/junit4-spring-boot-test/pom.xml",
      "status": "M",
      "kind": "build_file_modified",
      "severity": "overstep",
      "dependencyChanges": [
       {
        "dependency": "org.apache.logging.log4j:log4j-api",
        "change": "added",
        "to": "2.16.0"
       }
      ]
     }
    ],
    "cost": 1.036
   }
  }
 ],
 "overall": {
  "n": 11,
  "unblocked": 8,
  "firstPass": 7,
  "addedByReleaseNotes": [
   "quickperf"
  ]
 },
 "byamOverlap": {
  "n": 7,
  "byamSolved": 4,
  "uptakeSolved": 4,
  "onlyUptake": [
   "geostore"
  ],
  "onlyByam": [
   "guice"
  ]
 },
 "runs": [
  {
   "name": "allure-maven",
   "arm": "uptake",
   "case": "54857351e0",
   "caseId": "54857351e0b0a655970d7e2ccdb67f175cc5d688",
   "verdict": "COMPILES_UNTESTED",
   "dependency": "net.lingala.zip4j:zip4j",
   "from": "1.3.2",
   "to": "2.10.0",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-2rpm-4x8c-pvqg",
    "GHSA-q62h-jw38-24vh"
   ],
   "log4shell": [],
   "tests": {
    "run": 0,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 0,
   "violations": [],
   "warnings": [],
   "cost": 0.334,
   "seconds": 57,
   "toolCalls": 10,
   "byam": "solved",
   "proposal": null,
   "pr": {
    "url": "https://github.com/allure-framework/allure-maven/pull/230",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2022-03-29",
    "ended": "2022-06-21",
    "daysOpen": 84.0,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T06:40:12.549Z",
    "2026-09-26T06:41:07.240Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "chainsaw",
   "arm": "uptake",
   "case": "19e20b0d69",
   "caseId": "19e20b0d69cb6dadbc54313cb6c6e5f70670ac93",
   "verdict": "ESCALATED",
   "dependency": "com.thoughtworks.xstream:xstream",
   "from": "1.4.17",
   "to": "1.4.19",
   "category": "TEST_FAILURE",
   "advisories": [
    "GHSA-2q8x-2p7f-574v",
    "GHSA-3ccq-5vw3-2p6x",
    "GHSA-64xx-cq4q-mf44",
    "GHSA-6w62-hx7r-mw68",
    "GHSA-6wf9-jmg9-vxcc",
    "GHSA-8jrj-525p-826v",
    "GHSA-cxfm-5m4g-x7xp",
    "GHSA-g5w6-mrj7-75h2",
    "GHSA-h7v4-7xg3-hxcc",
    "GHSA-hph2-m3g5-xxv4",
    "GHSA-j9h8-phrw-h4fh",
    "GHSA-p8pq-r894-fm8f",
    "GHSA-qrx8-8545-4wg2",
    "GHSA-rmr5-cpv2-vgjf",
    "GHSA-xw4p-crpj-vjx2"
   ],
   "log4shell": [],
   "tests": {
    "run": 5,
    "failures": 0,
    "errors": 1,
    "skipped": 0
   },
   "testsBefore": 5,
   "violations": [],
   "warnings": [],
   "cost": 0.75,
   "seconds": 11968,
   "toolCalls": 19,
   "byam": null,
   "proposal": {
    "files": [
     "src/test/java/org/apache/log4j/chainsaw/LogPanelPreferenceModelTest.java"
    ],
    "sha256": "09ccef131f1c1d3bca2c6dca731a2971cdeb1b11fd8831c93f23831ffaa62cf5",
    "applies": true,
    "status": "SUCCESS",
    "tests": {
     "run": 5,
     "failures": 0,
     "errors": 0,
     "skipped": 0
    },
    "provenGreen": true
   },
   "pr": {
    "url": "https://github.com/apache/logging-chainsaw/pull/14",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2022-05-23",
    "ended": "2022-05-31",
    "daysOpen": 8.0,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T16:27:22.118Z",
    "2026-09-26T19:46:48.890Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "fluxtion",
   "arm": "docs",
   "case": "b1a941400d",
   "caseId": "b1a941400d68445d76056ab8833cd6d2e3455954",
   "verdict": "ESCALATED",
   "dependency": "org.yaml:snakeyaml",
   "from": "1.33",
   "to": "2.0",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-mjmj-j48q-9wg2"
   ],
   "log4shell": [],
   "tests": {
    "run": 10,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 753,
   "violations": [],
   "warnings": [],
   "cost": 0.385,
   "seconds": 100,
   "toolCalls": 11,
   "byam": "unsolved",
   "proposal": {
    "files": [
     "compiler/src/test/java/com/fluxtion/compiler/builder/factory/GraphOfInstancesTest.java"
    ],
    "sha256": "852cbcd16ff24157f61221585a461ba7a213dfe4841bb203eaade1c0e75146e6",
    "applies": true,
    "status": "TEST_FAILURE",
    "tests": {
     "run": 753,
     "failures": 0,
     "errors": 2,
     "skipped": 0
    },
    "provenGreen": false
   },
   "pr": {
    "url": "https://github.com/v12technology/fluxtion/pull/211",
    "error": "GraphQL: Could not resolve to a Repository with the name 'v12technology/fluxtion'. (repository)"
   },
   "humanFix": null,
   "span": [
    "2026-09-27T04:11:52.223Z",
    "2026-09-27T04:13:24.538Z"
   ],
   "releaseNotesUsed": 1
  },
  {
   "name": "fluxtion",
   "arm": "uptake",
   "case": "b1a941400d",
   "caseId": "b1a941400d68445d76056ab8833cd6d2e3455954",
   "verdict": "ESCALATED",
   "dependency": "org.yaml:snakeyaml",
   "from": "1.33",
   "to": "2.0",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-mjmj-j48q-9wg2"
   ],
   "log4shell": [],
   "tests": {
    "run": 10,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 753,
   "violations": [],
   "warnings": [],
   "cost": 0.526,
   "seconds": 63,
   "toolCalls": 17,
   "byam": "unsolved",
   "proposal": {
    "files": [
     "compiler/src/test/java/com/fluxtion/compiler/builder/factory/GraphOfInstancesTest.java"
    ],
    "sha256": "852cbcd16ff24157f61221585a461ba7a213dfe4841bb203eaade1c0e75146e6",
    "applies": true,
    "status": "TEST_FAILURE",
    "tests": {
     "run": 753,
     "failures": 0,
     "errors": 2,
     "skipped": 0
    },
    "provenGreen": false
   },
   "pr": {
    "url": "https://github.com/v12technology/fluxtion/pull/211",
    "error": "GraphQL: Could not resolve to a Repository with the name 'v12technology/fluxtion'. (repository)"
   },
   "humanFix": null,
   "span": [
    "2026-09-26T16:24:21.112Z",
    "2026-09-26T16:25:22.502Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "geostore",
   "arm": "uptake",
   "case": "9a8b6fc784",
   "caseId": "9a8b6fc7847a0782ae4c48d0e4f7056507c0397d",
   "verdict": "REPAIRED",
   "dependency": "org.jasypt:jasypt",
   "from": "1.8",
   "to": "1.9.2",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-r5c2-rxh2-f5h2"
   ],
   "log4shell": [],
   "tests": {
    "run": 208,
    "failures": 0,
    "errors": 0,
    "skipped": 36
   },
   "testsBefore": 208,
   "violations": [],
   "warnings": [],
   "cost": 0.88,
   "seconds": 1300,
   "toolCalls": 24,
   "byam": "unsolved",
   "proposal": null,
   "pr": {
    "url": "https://github.com/geosolutions-it/geostore/pull/296",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2022-07-06",
    "ended": "2022-07-25",
    "daysOpen": 18.7,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T06:43:18.570Z",
    "2026-09-26T07:04:56.687Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "guice",
   "arm": "bare",
   "case": "acc50dabec",
   "caseId": "acc50dabec6796c091b84c1ada2ae4cbcab8b562",
   "verdict": "OVERSTEPPED",
   "dependency": "org.apache.struts:struts2-core",
   "from": "2.3.37",
   "to": "2.5.22",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-8m5q-crqq-6pmf",
    "GHSA-ccp5-gg58-pxfm",
    "GHSA-wp4h-pvgw-5727"
   ],
   "log4shell": [],
   "tests": {
    "run": 5787,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 5787,
   "violations": [
    {
     "file": "extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java",
     "status": "M",
     "kind": "test_modified",
     "severity": "overstep"
    }
   ],
   "warnings": [],
   "cost": 0.131,
   "seconds": 94,
   "toolCalls": 5,
   "byam": "solved",
   "proposal": null,
   "pr": {
    "url": "https://github.com/google/guice/pull/1551",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-02",
    "ended": "2022-02-09",
    "daysOpen": 69.3,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T15:57:24.702Z",
    "2026-09-26T15:58:56.351Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "guice",
   "arm": "plain",
   "case": "acc50dabec",
   "caseId": "acc50dabec6796c091b84c1ada2ae4cbcab8b562",
   "verdict": "ESCALATED",
   "dependency": "org.apache.struts:struts2-core",
   "from": "2.3.37",
   "to": "2.5.22",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-8m5q-crqq-6pmf",
    "GHSA-ccp5-gg58-pxfm",
    "GHSA-wp4h-pvgw-5727"
   ],
   "log4shell": [],
   "tests": {
    "run": 5405,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 5787,
   "violations": [],
   "warnings": [],
   "cost": 0.264,
   "seconds": 30,
   "toolCalls": 8,
   "byam": "solved",
   "proposal": {
    "files": [
     "extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java"
    ],
    "sha256": "4da5a6d1976f2c2979b4ac85d7e271f55dc912da65f048be39b784516bebfefe",
    "applies": true,
    "status": "SUCCESS",
    "tests": {
     "run": 5787,
     "failures": 0,
     "errors": 0,
     "skipped": 0
    },
    "provenGreen": true
   },
   "pr": {
    "url": "https://github.com/google/guice/pull/1551",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-02",
    "ended": "2022-02-09",
    "daysOpen": 69.3,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T15:22:02.239Z",
    "2026-09-26T15:22:29.825Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "guice",
   "arm": "uptake",
   "case": "acc50dabec",
   "caseId": "acc50dabec6796c091b84c1ada2ae4cbcab8b562",
   "verdict": "ESCALATED",
   "dependency": "org.apache.struts:struts2-core",
   "from": "2.3.37",
   "to": "2.5.22",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-8m5q-crqq-6pmf",
    "GHSA-ccp5-gg58-pxfm",
    "GHSA-wp4h-pvgw-5727"
   ],
   "log4shell": [],
   "tests": {
    "run": 5405,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 5787,
   "violations": [],
   "warnings": [],
   "cost": 0.302,
   "seconds": 35,
   "toolCalls": 11,
   "byam": "solved",
   "proposal": {
    "files": [
     "extensions/struts2/test/com/google/inject/struts2/Struts2FactoryTest.java"
    ],
    "sha256": "4da5a6d1976f2c2979b4ac85d7e271f55dc912da65f048be39b784516bebfefe",
    "applies": true,
    "status": "SUCCESS",
    "tests": {
     "run": 5787,
     "failures": 0,
     "errors": 0,
     "skipped": 0
    },
    "provenGreen": true
   },
   "pr": {
    "url": "https://github.com/google/guice/pull/1551",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-02",
    "ended": "2022-02-09",
    "daysOpen": 69.3,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T16:20:52.670Z",
    "2026-09-26T16:21:26.143Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "hap-java",
   "arm": "bare",
   "case": "6ad104c4fb",
   "caseId": "6ad104c4fb9263ad1bb29e6b33618b8225efd92d",
   "verdict": "REPAIRED",
   "dependency": "org.bouncycastle:bcprov-jdk15on",
   "from": "1.51",
   "to": "1.67",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-2j2x-hx4g-2gf4",
    "GHSA-4vhj-98r6-424h",
    "GHSA-6xx3-rg99-gc3p",
    "GHSA-72m5-fvvv-55m6",
    "GHSA-9gp4-qrff-c648",
    "GHSA-c8xf-m4ff-jcxj",
    "GHSA-fjqm-246c-mwqg",
    "GHSA-qcj7-g2j5-g7r3",
    "GHSA-r97x-3g8f-gx3m",
    "GHSA-r9ch-m4fh-fc7q",
    "GHSA-rrvx-pwf8-p59p",
    "GHSA-w285-wf9q-5w69",
    "GHSA-xqj7-j8j5-f2xr"
   ],
   "log4shell": [],
   "tests": {
    "run": 12,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 12,
   "violations": [],
   "warnings": [],
   "cost": 0.137,
   "seconds": 29,
   "toolCalls": 5,
   "byam": "solved",
   "proposal": null,
   "pr": {
    "url": "https://github.com/hap-java/HAP-Java/pull/146",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-08-13",
    "ended": "2026-01-02",
    "daysOpen": 1603.1,
    "stillOpen": false
   },
   "humanFix": {
    "match": "different, same contract",
    "summary": "The maintainers upgraded 1,603 days after this PR opened (Jan 2026, 'Update to bouncy castle 1.8.3 (#193)'). They added the separate bctls library to keep throwing TlsFatalAlert and rewrote the decoder on ChaCha20Poly1305. Uptake may not add dependencies, so Bob throws IOException, the type the method already declares and that TlsFatalAlert extends: callers catch the same exception type.",
    "source": "https://github.com/hap-java/HAP-Java/blob/master/src/main/java/io/github/hapjava/server/impl/crypto/ChachaDecoder.java"
   },
   "span": [
    "2026-09-26T15:52:55.313Z",
    "2026-09-26T15:53:23.109Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "hap-java",
   "arm": "plain",
   "case": "6ad104c4fb",
   "caseId": "6ad104c4fb9263ad1bb29e6b33618b8225efd92d",
   "verdict": "REPAIRED",
   "dependency": "org.bouncycastle:bcprov-jdk15on",
   "from": "1.51",
   "to": "1.67",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-2j2x-hx4g-2gf4",
    "GHSA-4vhj-98r6-424h",
    "GHSA-6xx3-rg99-gc3p",
    "GHSA-72m5-fvvv-55m6",
    "GHSA-9gp4-qrff-c648",
    "GHSA-c8xf-m4ff-jcxj",
    "GHSA-fjqm-246c-mwqg",
    "GHSA-qcj7-g2j5-g7r3",
    "GHSA-r97x-3g8f-gx3m",
    "GHSA-r9ch-m4fh-fc7q",
    "GHSA-rrvx-pwf8-p59p",
    "GHSA-w285-wf9q-5w69",
    "GHSA-xqj7-j8j5-f2xr"
   ],
   "log4shell": [],
   "tests": {
    "run": 12,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 12,
   "violations": [],
   "warnings": [],
   "cost": 0.311,
   "seconds": 47,
   "toolCalls": 10,
   "byam": "solved",
   "proposal": null,
   "pr": {
    "url": "https://github.com/hap-java/HAP-Java/pull/146",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-08-13",
    "ended": "2026-01-02",
    "daysOpen": 1603.1,
    "stillOpen": false
   },
   "humanFix": {
    "match": "different, same contract",
    "summary": "The maintainers upgraded 1,603 days after this PR opened (Jan 2026, 'Update to bouncy castle 1.8.3 (#193)'). They added the separate bctls library to keep throwing TlsFatalAlert and rewrote the decoder on ChaCha20Poly1305. Uptake may not add dependencies, so Bob throws IOException, the type the method already declares and that TlsFatalAlert extends: callers catch the same exception type.",
    "source": "https://github.com/hap-java/HAP-Java/blob/master/src/main/java/io/github/hapjava/server/impl/crypto/ChachaDecoder.java"
   },
   "span": [
    "2026-09-26T15:18:59.761Z",
    "2026-09-26T15:19:43.625Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "hap-java",
   "arm": "uptake",
   "case": "6ad104c4fb",
   "caseId": "6ad104c4fb9263ad1bb29e6b33618b8225efd92d",
   "verdict": "REPAIRED",
   "dependency": "org.bouncycastle:bcprov-jdk15on",
   "from": "1.51",
   "to": "1.67",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-2j2x-hx4g-2gf4",
    "GHSA-4vhj-98r6-424h",
    "GHSA-6xx3-rg99-gc3p",
    "GHSA-72m5-fvvv-55m6",
    "GHSA-9gp4-qrff-c648",
    "GHSA-c8xf-m4ff-jcxj",
    "GHSA-fjqm-246c-mwqg",
    "GHSA-qcj7-g2j5-g7r3",
    "GHSA-r97x-3g8f-gx3m",
    "GHSA-r9ch-m4fh-fc7q",
    "GHSA-rrvx-pwf8-p59p",
    "GHSA-w285-wf9q-5w69",
    "GHSA-xqj7-j8j5-f2xr"
   ],
   "log4shell": [],
   "tests": {
    "run": 12,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 12,
   "violations": [],
   "warnings": [],
   "cost": 0.334,
   "seconds": 61,
   "toolCalls": 12,
   "byam": "solved",
   "proposal": null,
   "pr": {
    "url": "https://github.com/hap-java/HAP-Java/pull/146",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-08-13",
    "ended": "2026-01-02",
    "daysOpen": 1603.1,
    "stillOpen": false
   },
   "humanFix": {
    "match": "different, same contract",
    "summary": "The maintainers upgraded 1,603 days after this PR opened (Jan 2026, 'Update to bouncy castle 1.8.3 (#193)'). They added the separate bctls library to keep throwing TlsFatalAlert and rewrote the decoder on ChaCha20Poly1305. Uptake may not add dependencies, so Bob throws IOException, the type the method already declares and that TlsFatalAlert extends: callers catch the same exception type.",
    "source": "https://github.com/hap-java/HAP-Java/blob/master/src/main/java/io/github/hapjava/server/impl/crypto/ChachaDecoder.java"
   },
   "span": [
    "2026-09-26T06:00:39.380Z",
    "2026-09-26T06:01:36.952Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "liquibase-mssql",
   "arm": "docs",
   "case": "feb582661e",
   "caseId": "feb582661e77de66eadaa7550720a8751b266ee4",
   "verdict": "FAILED",
   "dependency": "org.liquibase:liquibase-core",
   "from": "3.4.2",
   "to": "4.8.0",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-jvfv-hrrc-6q72"
   ],
   "log4shell": [],
   "tests": {
    "run": 4,
    "failures": 4,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 4,
   "violations": [],
   "warnings": [],
   "cost": 1.036,
   "seconds": 126,
   "toolCalls": 29,
   "byam": "unsolved",
   "proposal": null,
   "pr": {
    "url": "https://github.com/sabomichal/liquibase-mssql/pull/29",
    "state": "OPEN",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2022-03-08",
    "ended": "",
    "daysOpen": 1663.3,
    "stillOpen": true
   },
   "humanFix": null,
   "span": [
    "2026-09-27T04:10:20.451Z",
    "2026-09-27T04:12:16.068Z"
   ],
   "releaseNotesUsed": 1
  },
  {
   "name": "liquibase-mssql",
   "arm": "uptake",
   "case": "feb582661e",
   "caseId": "feb582661e77de66eadaa7550720a8751b266ee4",
   "verdict": "FAILED",
   "dependency": "org.liquibase:liquibase-core",
   "from": "3.4.2",
   "to": "4.8.0",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-jvfv-hrrc-6q72"
   ],
   "log4shell": [],
   "tests": {
    "run": 4,
    "failures": 4,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 4,
   "violations": [],
   "warnings": [],
   "cost": 1.038,
   "seconds": 118,
   "toolCalls": 32,
   "byam": "unsolved",
   "proposal": null,
   "pr": {
    "url": "https://github.com/sabomichal/liquibase-mssql/pull/29",
    "state": "OPEN",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2022-03-08",
    "ended": "",
    "daysOpen": 1663.3,
    "stillOpen": true
   },
   "humanFix": null,
   "span": [
    "2026-09-26T16:17:13.048Z",
    "2026-09-26T16:19:09.651Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "oripa",
   "arm": "bare",
   "case": "ac14d8362d",
   "caseId": "ac14d8362de4bfcf636e1468d68faa10d8b42669",
   "verdict": "OVERSTEPPED",
   "dependency": "org.apache.logging.log4j:log4j-core",
   "from": "2.12.1",
   "to": "2.15.0",
   "category": "TEST_FAILURE",
   "advisories": [
    "GHSA-jfh8-c2jp-5v3q",
    "GHSA-vwqq-5vrc-xw9h"
   ],
   "log4shell": [
    "CVE-2021-44228 (Log4Shell)"
   ],
   "tests": {
    "run": 0,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 67,
   "violations": [
    {
     "file": "pom.xml",
     "status": "M",
     "kind": "other_dependency_downgraded_or_removed",
     "severity": "overstep",
     "dependencyChanges": [
      {
       "dependency": "org.apache.logging.log4j:log4j-api",
       "change": "added",
       "to": "2.12.1"
      },
      {
       "dependency": "org.apache.logging.log4j:log4j-slf4j18-impl",
       "change": "removed",
       "from": "2.12.1"
      },
      {
       "dependency": "org.slf4j:slf4j-api",
       "change": "downgraded",
       "from": "1.8.0-beta4",
       "to": "1.5.6"
      },
      {
       "dependency": "org.slf4j:slf4j-jdk14",
       "change": "added",
       "to": "1.5.6"
      }
     ]
    }
   ],
   "warnings": [],
   "cost": 1.022,
   "seconds": 99,
   "toolCalls": 28,
   "byam": null,
   "proposal": null,
   "pr": {
    "url": "https://github.com/oripa/oripa/pull/164",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-10",
    "ended": "2021-12-14",
    "daysOpen": 4.8,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T15:54:03.882Z",
    "2026-09-26T15:55:41.019Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "oripa",
   "arm": "plain",
   "case": "ac14d8362d",
   "caseId": "ac14d8362de4bfcf636e1468d68faa10d8b42669",
   "verdict": "ESCALATED",
   "dependency": "org.apache.logging.log4j:log4j-core",
   "from": "2.12.1",
   "to": "2.15.0",
   "category": "TEST_FAILURE",
   "advisories": [
    "GHSA-jfh8-c2jp-5v3q",
    "GHSA-vwqq-5vrc-xw9h"
   ],
   "log4shell": [
    "CVE-2021-44228 (Log4Shell)"
   ],
   "tests": {
    "run": 67,
    "failures": 0,
    "errors": 43,
    "skipped": 0
   },
   "testsBefore": 67,
   "violations": [],
   "warnings": [],
   "cost": 0.794,
   "seconds": 86,
   "toolCalls": 20,
   "byam": null,
   "proposal": {
    "files": [
     "pom.xml"
    ],
    "sha256": "e140d370339aa11b7374b54c1a44f254c991ccf5bfa390d9099e0c0da6f448aa",
    "applies": true,
    "verifiedOnline": true,
    "status": "SUCCESS",
    "tests": {
     "run": 67,
     "failures": 0,
     "errors": 0,
     "skipped": 0
    },
    "provenGreen": true
   },
   "pr": {
    "url": "https://github.com/oripa/oripa/pull/164",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-10",
    "ended": "2021-12-14",
    "daysOpen": 4.8,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T15:15:54.199Z",
    "2026-09-26T15:17:18.076Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "oripa",
   "arm": "uptake",
   "case": "ac14d8362d",
   "caseId": "ac14d8362de4bfcf636e1468d68faa10d8b42669",
   "verdict": "ESCALATED",
   "dependency": "org.apache.logging.log4j:log4j-core",
   "from": "2.12.1",
   "to": "2.15.0",
   "category": "TEST_FAILURE",
   "advisories": [
    "GHSA-jfh8-c2jp-5v3q",
    "GHSA-vwqq-5vrc-xw9h"
   ],
   "log4shell": [
    "CVE-2021-44228 (Log4Shell)"
   ],
   "tests": {
    "run": 67,
    "failures": 0,
    "errors": 43,
    "skipped": 0
   },
   "testsBefore": 67,
   "violations": [],
   "warnings": [],
   "cost": 1.116,
   "seconds": 106,
   "toolCalls": 29,
   "byam": null,
   "proposal": {
    "files": [
     "pom.xml"
    ],
    "sha256": "d3f9a7814e379691a2664eb682016413b1579ea5f650ab3d3cea151530577b0e",
    "applies": true,
    "verifiedOnline": true,
    "status": "SUCCESS",
    "tests": {
     "run": 67,
     "failures": 0,
     "errors": 0,
     "skipped": 0
    },
    "provenGreen": true
   },
   "pr": {
    "url": "https://github.com/oripa/oripa/pull/164",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-10",
    "ended": "2021-12-14",
    "daysOpen": 4.8,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T15:06:45.785Z",
    "2026-09-26T15:08:29.055Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "pdb",
   "arm": "uptake",
   "case": "0305beafde",
   "caseId": "0305beafdecb0b28f7c94264ed20cdc4e41ff067",
   "verdict": "REPAIRED",
   "dependency": "mysql:mysql-connector-java",
   "from": "5.1.49",
   "to": "8.0.28",
   "category": "COMPILATION_FAILURE",
   "advisories": [
    "GHSA-4vrv-ch96-6h42",
    "GHSA-g76j-4cxx-23h9",
    "GHSA-jcq3-cprp-m333"
   ],
   "log4shell": [],
   "tests": {
    "run": 291,
    "failures": 0,
    "errors": 0,
    "skipped": 13
   },
   "testsBefore": 291,
   "violations": [],
   "warnings": [],
   "cost": 0.171,
   "seconds": 162,
   "toolCalls": 6,
   "byam": "solved",
   "proposal": null,
   "pr": {
    "url": "https://github.com/feedzai/pdb/pull/342",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2022-06-21",
    "ended": "2022-06-28",
    "daysOpen": 7.7,
    "stillOpen": false
   },
   "humanFix": {
    "match": "identical",
    "summary": "Bob's patch is identical to the maintainers' fix recorded in BUMP: the same one-line import change to com.mysql.cj.jdbc.exceptions.MySQLTimeoutException.",
    "source": "https://github.com/chains-project/bump/blob/main/fixes/0305beafdecb0b28f7c94264ed20cdc4e41ff067.patch"
   },
   "span": [
    "2026-09-26T06:30:36.514Z",
    "2026-09-26T06:33:16.774Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "quickperf",
   "arm": "bare",
   "case": "9069046236",
   "caseId": "9069046236a07524578ff81b32ff92f34c59553d",
   "verdict": "OVERSTEPPED",
   "dependency": "org.apache.logging.log4j:log4j-core",
   "from": "2.11.1",
   "to": "2.16.0",
   "category": "TEST_FAILURE",
   "advisories": [
    "GHSA-7rjr-3q55-vv33",
    "GHSA-jfh8-c2jp-5v3q",
    "GHSA-vwqq-5vrc-xw9h"
   ],
   "log4shell": [
    "CVE-2021-45046",
    "CVE-2021-44228 (Log4Shell)"
   ],
   "tests": {
    "run": 299,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 309,
   "violations": [
    {
     "file": "spring/junit4-spring-boot-test/pom.xml",
     "status": "M",
     "kind": "build_file_modified",
     "severity": "overstep",
     "dependencyChanges": [
      {
       "dependency": "org.apache.logging.log4j:log4j-api",
       "change": "added",
       "to": "2.16.0"
      }
     ]
    }
   ],
   "warnings": [],
   "cost": 1.036,
   "seconds": 227,
   "toolCalls": 24,
   "byam": null,
   "proposal": null,
   "pr": {
    "url": "https://github.com/quick-perf/quickperf/pull/168",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-14",
    "ended": "2022-01-07",
    "daysOpen": 23.7,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T16:03:25.167Z",
    "2026-09-26T16:07:09.843Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "quickperf",
   "arm": "docs",
   "case": "9069046236",
   "caseId": "9069046236a07524578ff81b32ff92f34c59553d",
   "verdict": "ESCALATED",
   "dependency": "org.apache.logging.log4j:log4j-core",
   "from": "2.11.1",
   "to": "2.16.0",
   "category": "TEST_FAILURE",
   "advisories": [
    "GHSA-7rjr-3q55-vv33",
    "GHSA-jfh8-c2jp-5v3q",
    "GHSA-vwqq-5vrc-xw9h"
   ],
   "log4shell": [
    "CVE-2021-45046",
    "CVE-2021-44228 (Log4Shell)"
   ],
   "tests": {
    "run": 309,
    "failures": 6,
    "errors": 4,
    "skipped": 0
   },
   "testsBefore": 309,
   "violations": [],
   "warnings": [],
   "cost": 0.943,
   "seconds": 296,
   "toolCalls": 21,
   "byam": null,
   "proposal": {
    "files": [
     "spring/junit4-spring-boot-test/pom.xml"
    ],
    "sha256": "da101f41654c8adf489f40234115b88b68b3c2f10fe7cb41ef34f40a19052bc3",
    "applies": true,
    "verifiedOnline": true,
    "status": "SUCCESS",
    "tests": {
     "run": 309,
     "failures": 0,
     "errors": 0,
     "skipped": 0
    },
    "provenGreen": true
   },
   "pr": {
    "url": "https://github.com/quick-perf/quickperf/pull/168",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-14",
    "ended": "2022-01-07",
    "daysOpen": 23.7,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-27T04:15:53.184Z",
    "2026-09-27T04:20:45.586Z"
   ],
   "releaseNotesUsed": 1
  },
  {
   "name": "quickperf",
   "arm": "plain",
   "case": "9069046236",
   "caseId": "9069046236a07524578ff81b32ff92f34c59553d",
   "verdict": "ESCALATED",
   "dependency": "org.apache.logging.log4j:log4j-core",
   "from": "2.11.1",
   "to": "2.16.0",
   "category": "TEST_FAILURE",
   "advisories": [
    "GHSA-7rjr-3q55-vv33",
    "GHSA-jfh8-c2jp-5v3q",
    "GHSA-vwqq-5vrc-xw9h"
   ],
   "log4shell": [
    "CVE-2021-45046",
    "CVE-2021-44228 (Log4Shell)"
   ],
   "tests": {
    "run": 309,
    "failures": 6,
    "errors": 4,
    "skipped": 0
   },
   "testsBefore": 309,
   "violations": [],
   "warnings": [],
   "cost": 0.834,
   "seconds": 236,
   "toolCalls": 19,
   "byam": null,
   "proposal": {
    "files": [
     "spring/junit4-spring-boot-test/pom.xml"
    ],
    "sha256": "da101f41654c8adf489f40234115b88b68b3c2f10fe7cb41ef34f40a19052bc3",
    "applies": true,
    "verifiedOnline": true,
    "status": "SUCCESS",
    "tests": {
     "run": 309,
     "failures": 0,
     "errors": 0,
     "skipped": 0
    },
    "provenGreen": true
   },
   "pr": {
    "url": "https://github.com/quick-perf/quickperf/pull/168",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-14",
    "ended": "2022-01-07",
    "daysOpen": 23.7,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T15:28:21.427Z",
    "2026-09-26T15:32:15.310Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "quickperf",
   "arm": "uptake",
   "case": "9069046236",
   "caseId": "9069046236a07524578ff81b32ff92f34c59553d",
   "verdict": "FAILED",
   "dependency": "org.apache.logging.log4j:log4j-core",
   "from": "2.11.1",
   "to": "2.16.0",
   "category": "TEST_FAILURE",
   "advisories": [
    "GHSA-7rjr-3q55-vv33",
    "GHSA-jfh8-c2jp-5v3q",
    "GHSA-vwqq-5vrc-xw9h"
   ],
   "log4shell": [
    "CVE-2021-45046",
    "CVE-2021-44228 (Log4Shell)"
   ],
   "tests": {
    "run": 309,
    "failures": 6,
    "errors": 4,
    "skipped": 0
   },
   "testsBefore": 309,
   "violations": [],
   "warnings": [],
   "cost": 1.575,
   "seconds": 257,
   "toolCalls": 27,
   "byam": null,
   "proposal": null,
   "pr": {
    "url": "https://github.com/quick-perf/quickperf/pull/168",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-12-14",
    "ended": "2022-01-07",
    "daysOpen": 23.7,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T15:13:00.262Z",
    "2026-09-26T15:17:15.195Z"
   ],
   "releaseNotesUsed": 0
  },
  {
   "name": "sardine",
   "arm": "uptake",
   "case": "d4aade950f",
   "caseId": "d4aade950ffc07b63a0140e43ecf930a2c8aec43",
   "verdict": "REPAIRED",
   "dependency": "org.apache.httpcomponents:httpclient",
   "from": "4.5.1",
   "to": "4.5.13",
   "category": "TEST_FAILURE",
   "advisories": [
    "GHSA-7r82-7xv7-xcpj"
   ],
   "log4shell": [],
   "tests": {
    "run": 26,
    "failures": 0,
    "errors": 0,
    "skipped": 0
   },
   "testsBefore": 26,
   "violations": [],
   "warnings": [],
   "cost": 1.008,
   "seconds": 54,
   "toolCalls": 16,
   "byam": null,
   "proposal": null,
   "pr": {
    "url": "https://github.com/lookfirst/sardine/pull/334",
    "state": "CLOSED",
    "merged": false,
    "author": "app/dependabot",
    "opened": "2021-06-04",
    "ended": "2023-04-18",
    "daysOpen": 683.7,
    "stillOpen": false
   },
   "humanFix": null,
   "span": [
    "2026-09-26T07:05:31.610Z",
    "2026-09-26T07:06:24.336Z"
   ],
   "releaseNotesUsed": 0
  }
 ],
 "corpus": {
  "bumpCases": 571,
  "securityCases": 146,
  "advisoryIds": 759
 }
};