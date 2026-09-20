# en_core_web_md 3.8.0 verification

## Artifact provenance

- Upstream repository: `explosion/spacy-models`
- Release: `en_core_web_md-3.8.0`
- Wheel SHA-256: `5e6329fe3fecedb1d1a02c3ea2172ee0fede6cea6e4aefb6a02d832dba78a310`
- Declared vector table: 20,000 rows x 300 dimensions, 684,830 keys.
- Vector mode observed at runtime: `default`.

## Execution evidence

The exact upstream wheel was downloaded and checksum-verified in GitHub Actions, then loaded successfully with:

- Python 3.12.14
- spaCy 3.8.11
- NumPy 1.26.4

A compatibility probe reproduced the same vector behavior under spaCy 3.8.0 + NumPy 1.26.4 and spaCy 3.8.11 + NumPy 2.5.3. This rules out the observed semantic degeneracy as a single-version runtime artifact.

## Observed vector-table structure

On spaCy 3.8.11:

- shape: `(20000, 300)`
- keys: `684830`
- zero rows: `0`
- unique numerical rows: `10112`
- duplicated nonzero rows: `9888`

The duplicate rows are not merely unused/zero slots.

## Semantic behavior

A deterministic 48-word probe generated 1,128 non-identical word pairs.

The exact wheel produced 11 pairs with cosine similarity >= 0.999, including:

- `dog ↔ cat = 1.000000119`
- `computer ↔ software = 1.0`
- `doctor ↔ medicine = 1.0`
- `guitar ↔ piano = 1.0`
- `river ↔ bank = 1.0`
- `teacher ↔ school = 1.0`
- `lawyer ↔ court = 1.0`
- `winter ↔ summer = 0.99999994`

Nearest-neighbor output is also saturated: `computer` returns unrelated/cross-domain terms such as `Paths`, `CONNECTING`, and `CONFIGURATION` at similarity 1.0.

The coarse related-vs-unrelated sanity test still passes, but that is insufficient because exact-vector collisions can satisfy that weak ordering while destroying useful geometry.

## Disposition

**Loadability:** EXPERIMENTALLY_SUPPORTED

**Generic semantic word-similarity behavior:** **CONTRADICTED**

**Root cause:** OPEN

The current evidence shows the problem is reproducible from the exact upstream `en_core_web_md-3.8.0` artifact across multiple compatible spaCy/NumPy runtimes. Do not build a semantic-similarity or vector-retrieval primitive on this artifact.

The next discriminating step is to inspect the larger `en_core_web_lg-3.8.0` artifact from the same release family before abandoning spaCy vectors entirely.
