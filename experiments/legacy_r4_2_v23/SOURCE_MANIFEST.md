# R4.2 / v23 historical source manifest

> Status: **SUPERSEDED historical implementation evidence.** `FP_THEORY.md` is normative.

- original package SHA-256: `2c3e5091f90a0e5e3bf659dabb04afb0c7cf7b293ea7e7319892a1f8a273ccd4`
- historical release commit: `2f5977d41c78edfebe892af2fe8d789ba9fb8f26`
- historical release tree: `58136ac42efcc50ed27af9e003aaede1ac417458`
- curated source/text files in recovered package: 25

The canonical repository intentionally retains only the small subset of readable source needed to audit the R4.2 failure and implementation shape. The full recovered package is identified by the hashes below; no old `.git`, ZIP bundle, cache, dataset, checkpoint, or raw log is imported.

## Complete recovered package file hashes

| path | bytes | SHA-256 |
|---|---:|---|
| `PACKAGE_VERSION.json` | 828 | `608169404f660c690eb7a04be93bc45612729eb4442069bc698ab0b61a64ef6d` |
| `README.md` | 838 | `1d83ccb4043b5e29cddd36f2361cd2a4d06755c1121d077217317affb93339de` |
| `README_NATIVE_FROM_PRIOR_R4_2_CN.txt` | 4830 | `9490bf8b9570617c6bc0b4fe5ec7a20f52f3aa1faecab6651f19130a4807fb43` |
| `REAL_3090_R4_1_POSTMORTEM_AND_R4_2_CHANGES.md` | 8874 | `8a5b4c363c40d72e9f21116d7ae607688d018ddaab1aa487691d2cad731f3596` |
| `RUN_FP_NATIVE_PRIOR_R4_2.bat` | 2928 | `3d3658e221b89ba91ff439c257e49e527c6db80060f2337d851efee0e8dbf668` |
| `VERIFIED_IMPLEMENTATION_R4_2_V23.md` | 12061 | `1f6eef1cb8c37acb104d92327a8ca4aea73fc613140656b4401f9a9c2ac55530` |
| `cpp/fp_native_cpu.cpp` | 14369 | `398c746a756555908caf3b5649ef830f73351cb7962807c5109a84517161f33f` |
| `fpnp/__init__.py` | 43 | `e3e3f2f7ccd10b446afb677b1e967c760f8430fac1e7e1ffc79160233ebf7391` |
| `fpnp/async_compile.py` | 15956 | `90d61ca147f73f9cababc40d957321be2164048f69e4d4b5cbdb8fbbd72b3ecf` |
| `fpnp/compiler_v23.py` | 22373 | `f6448637081dae6856445d252d3cd17575542d69a18b927c1b4544df2ff791a2` |
| `fpnp/config.py` | 2775 | `5376453310a31e38d5394b9f2d81e9d003edd93a2019c35ae4110b99be096605` |
| `fpnp/data.py` | 1958 | `b05e60acdd8ac89500ccbc8a60ccb3dd9786b61decc0dbc165de7b18fdd651dd` |
| `fpnp/gpu_runtime.py` | 9100 | `4d042cd53efd1b5811cc10a9fe461699fb588a6f8b35c165acfcff1b8e854855` |
| `fpnp/measure.py` | 13140 | `e000439db732e1f7df2eb3ffa7cbc01733567b477e727075c2f84661d92aa204` |
| `fpnp/native_cpu.py` | 9452 | `1131c88fef0c1bd530d0e0ac15c16cdb64b8fa36796d8b8f4f0a18ed5058b527` |
| `fpnp/native_runner.py` | 29320 | `1f61cf87e992f33bad6ac25226dc3f2e431b856bd5e5e52938fced5edd11654e` |
| `fpnp/preflight.py` | 14870 | `4470cb923a37c12da1abb8a56a372f8e532365144276c8eec22863a0d538d612` |
| `fpnp/program.py` | 11940 | `4d6935e2128a165fbb5543cb209d3692d4492e3834f6fd23628b4a4cae1c18cb` |
| `fpnp/readout.py` | 8668 | `dc7e37fb4b178bb4c6c20f6ef65ee5657e3fc7535a120afa7a809db175b8fc0a` |
| `fpnp/result_pack.py` | 2492 | `a0adf48f0783ed656bdd70b97b234049b1ae05558485c663244d21c7a17cc0b7` |
| `fpnp/runlog.py` | 3768 | `4432fcd06dc6a48cd8441c712f539c95ec314472b9517abf1875c344a7fc0856` |
| `fpnp/selftest.py` | 39553 | `60fad91623c7bb1ceec9ea18234dd736f44cb5caca4a482df636d2d8ef5197e6` |
| `fpnp/transaction.py` | 20347 | `87a0869ba959a74e4efe78283e56fa89010262a1ee65d303ea294ad454122f33` |
| `fpnp/validation.py` | 1768 | `0276624800f47f95c500ca3924c1f6244815d922dd2308e311d37e1e5b5ec7c3` |
| `launcher.py` | 10895 | `b53f8e5725a8e6a16e2be767b2d96bff8413ff4f8c022221f0f82d3cd0672114` |

## Files retained as readable historical source in the canonical repository

- `PACKAGE_VERSION.json`
- `REAL_3090_R4_1_POSTMORTEM_AND_R4_2_CHANGES.md`
- `fpnp/program.py`
- `fpnp/gpu_runtime.py`
- `fpnp/readout.py`
- `fpnp/config.py`
- `fpnp/data.py`
- `fpnp/validation.py`

Large superseded files such as `compiler_v23.py`, `transaction.py`, `native_runner.py`, `selftest.py`, `async_compile.py`, `preflight.py`, the C++ backend, and ancillary runner/logging modules are represented by the exact hashes above rather than duplicated as a second maintained implementation.
