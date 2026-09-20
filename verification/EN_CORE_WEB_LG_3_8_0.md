# en_core_web_lg 3.8.0 verification

## Artifact provenance

- Upstream repository: `explosion/spacy-models`
- Release: `en_core_web_lg-3.8.0`
- Wheel SHA-256: `293e9547a655b25499198ab15a525b05b9407a75f10255e405e8c3854329ab63`
- Release wheel size: 400,658,291 bytes.
- Declared vector table: 342,918 vectors, 300 dimensions, 684,830 keys.

spaCy's current English model documentation lists `en_core_web_lg` 3.8.0 as a 382 MB model with 685k keys and 343k unique 300-dimensional vectors. citeturn428557search0turn428557search1

## Execution evidence

GitHub Actions downloaded the exact upstream wheel, verified the SHA-256, installed it with:

- Python 3.12.14
- spaCy 3.8.11
- NumPy 1.26.4

and successfully loaded the model.

Observed:

- vector shape: `(342918, 300)`
- keys: `684830`
- numerical unique rows: `342918`
- zero rows: `0`
- saturated pairs (cosine >= 0.999) across 435 pairs from 30 selected words: `0`

Observed semantic probes:

- `dog ↔ cat = 0.80168539`
- `dog ↔ banana = 0.24327642`
- `computer ↔ software = 0.67071533`
- `doctor ↔ medicine = 0.68606144`
- `guitar ↔ piano = 0.74547100`
- `ocean ↔ water = 0.60063189`

These are materially different from the degenerate behavior observed in `en_core_web_md-3.8.0`.

## Disposition

**Loadability:** EXPERIMENTALLY_SUPPORTED

**Basic semantic geometry:** EXPERIMENTALLY_SUPPORTED

**Production suitability:** OPEN

This is now the active candidate for a second verification pass. It has passed the first non-degeneracy probe, but should still pass a larger deterministic semantic suite and an application-specific task test before architectural use.
