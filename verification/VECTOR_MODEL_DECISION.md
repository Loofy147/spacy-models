# Vector model verification decision

## Current candidates

### en_core_web_md-3.8.0
Status: **REJECTED FOR SEMANTIC USE**

Exact artifact loads and has vectors, but its observed geometry is degenerate:
- 20,000 x 300 table
- 684,830 keys
- only 10,112 unique numerical rows
- 9,888 duplicated nonzero rows
- 11 saturated non-identical pairs among 1,128 pairs in the final probe
- `dog ↔ cat = 1.000000119`

The runtime matrix reproduced the same behavior under:
- spaCy 3.8.0 + NumPy 1.26.4
- spaCy 3.8.11 + NumPy 1.26.4
- spaCy 3.8.11 + NumPy 2.5.3

Therefore the observed degeneracy is not explained by one particular runtime combination.

### en_core_web_lg-3.8.0
Status: **EXPERIMENTALLY_SUPPORTED — GENERIC VECTOR GATE PASSED**

Exact artifact verification:
- wheel SHA-256: `293e9547a655b25499198ab15a525b05b9407a75f10255e405e8c3854329ab63`
- Python 3.12.14
- spaCy 3.8.11
- NumPy 1.26.4
- vector shape: 342,918 x 300
- 684,830 keys
- 342,918 unique nonzero rows
- zero duplicate rows
- zero zero-rows

Full semantic verification:
- 50 selected words
- 1,225 non-identical word pairs
- 0 pairs with cosine >= 0.999
- maximum non-identical cosine: 0.82296985
- p50/p90/p99: 0.21589 / 0.38274 / 0.67130
- related-vs-unrelated sanity: 20/20
- mean pairwise margin: 0.52298718
- identity, symmetry, OOV and finite-value checks all pass
- nearest-neighbor results show coherent lexical neighborhoods

Core observed similarities:
- `dog ↔ cat = 0.80168539`
- `dog ↔ banana = 0.24327642`
- `doctor ↔ hospital = 0.62423599`
- `computer ↔ software = 0.67071533`
- `king ↔ queen = 0.72526109`

Verification run:
- GitHub Actions run `35541335964`
- job `106159448472`
- conclusion: **success**

## Decision boundary

The generic vector gate is now passed for `en_core_web_lg-3.8.0`.

This does **not** establish that the model is suitable for the intended application. It establishes only that:

1. the exact artifact loads;
2. the vector table is structurally non-degenerate;
3. similarity has reproducible, non-saturated lexical geometry;
4. basic invariants behave as expected.

## Next gate

Do not build the application architecture yet.

Run an application-specific evaluation against the exact same artifact/runtime and record:
- task definition;
- positive/negative pairs or retrieval queries;
- baseline;
- measurable acceptance threshold;
- failure cases;
- reproducibility environment.

Only that result can promote the model from **generic candidate** to **architectural dependency**.
