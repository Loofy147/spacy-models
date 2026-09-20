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

The runtime matrix reproduced the same behavior under spaCy 3.8.0 + NumPy 1.26.4, spaCy 3.8.11 + NumPy 1.26.4, and spaCy 3.8.11 + NumPy 2.5.3.

### en_core_web_lg-3.8.0
Status: **ACTIVE CANDIDATE / EXPERIMENTALLY_SUPPORTED**

Exact artifact loads and, in the first probe:
- has 342,918 unique numerical rows
- has zero saturated pairs across 435 selected word pairs
- produces plausible similarities such as `dog↔cat=0.80168539` and `dog↔banana=0.24327642`.

## Next gate

Do not build the application primitive yet.

The next gate is a larger deterministic verification of `en_core_web_lg-3.8.0`:
1. semantic non-degeneracy across a larger probe set;
2. symmetry/identity/OOV behavior;
3. nearest-neighbor inspection;
4. application-specific task performance on the actual intended use case;
5. provenance pinning and reproducible environment lock.

Only after those pass should the vector model become an architectural dependency.
