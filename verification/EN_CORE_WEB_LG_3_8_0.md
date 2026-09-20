# en_core_web_lg 3.8.0 verification

## Artifact provenance

- Upstream repository: `explosion/spacy-models`
- Release: `en_core_web_lg-3.8.0`
- Wheel SHA-256: `293e9547a655b25499198ab15a525b05b9407a75f10255e405e8c3854329ab63`
- Release wheel size: 400,658,291 bytes.
- Declared vector table: 342,918 vectors, 300 dimensions, 684,830 keys.

spaCy's current English model documentation lists `en_core_web_lg` 3.8.0 as a 382 MB model with 685k keys and 343k unique 300-dimensional vectors. citeturn428557search0turn428557search1

## Full execution evidence

The exact upstream wheel was downloaded and SHA-256 verified in GitHub Actions, then installed with:

- Python 3.12.14
- spaCy 3.8.11
- NumPy 1.26.4

The full verifier completed with **PASS**.

Observed vector table:

- shape: `(342918, 300)`
- keys: `684830`
- mode: `default`
- nonzero rows: `342918`
- zero rows: `0`
- unique rows: `342918`
- duplicated nonzero rows: `0`

Semantic geometry probe:

- 50 selected words
- 1,225 non-identical word pairs
- saturated pairs (cosine >= 0.999): **0**
- maximum non-identical cosine: **0.82296985**
- similarity quantiles: p50=`0.21589`, p90=`0.38274`, p99=`0.67130`
- related-vs-unrelated sanity accuracy: **100% (20/20)**
- mean pairwise margin: `0.52298718`

Core probes:

- `dog ↔ cat = 0.80168539`
- `dog ↔ banana = 0.24327642`
- `doctor ↔ hospital = 0.62423599`
- `computer ↔ software = 0.67071533`
- `king ↔ queen = 0.72526109`

Runtime invariants:

- identity cosine: `0.99999994`
- symmetry: `dog↔cat == cat↔dog`
- OOV has no vector and zero norm
- every probe word has a nonzero vector
- all vector values are finite

Nearest-neighbor behavior is also qualitatively coherent: for example, `dog` returns DOGS, PUPPY, PET, CAT, CANINE; `computer` returns COMPUTERS, LAPTOP, SOFTWARE, DESKTOP, COMPUTING.

## Disposition

**Loadability:** EXPERIMENTALLY_SUPPORTED

**Vector integrity:** EXPERIMENTALLY_SUPPORTED

**Basic semantic geometry:** EXPERIMENTALLY_SUPPORTED

**Production suitability:** OPEN

The model has passed the generic pre-build vector gate. The remaining gate is application-specific: the intended task must be tested against this exact artifact/runtime before it becomes an architectural dependency.
