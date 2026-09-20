# en_core_web_md 3.8.0 verification

## Artifact

- Source repository: `explosion/spacy-models`
- Release tag: `en_core_web_md-3.8.0`
- Wheel: `en_core_web_md-3.8.0-py3-none-any.whl`
- Upstream release asset:
  https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl
- SHA-256:
  `5e6329fe3fecedb1d1a02c3ea2172ee0fede6cea6e4aefb6a02d832dba78a310`
- Declared model version: `3.8.0`
- Declared compatibility: `spacy>=3.8.0,<3.9.0`
- Declared vectors: 684830 keys, 20000 unique vectors, 300 dimensions.

## Ownership boundary

This fork does not inherit the upstream GitHub Release assets. The verification workflow therefore downloads the exact upstream wheel and verifies its SHA-256 before installation.

The fork is the durable location for the verification protocol and results, not a claim that the binary artifact has been independently mirrored.

## Verification design

The workflow pins the runtime to `spacy==3.8.11` and then verifies:

1. exact model version and vector matrix shape/key count;
2. finite and non-degenerate vector rows;
3. known-word vector presence and nonzero norm;
4. OOV behavior (no vector, zero norm);
5. identity and symmetry of cosine similarity;
6. regression anchors for the known `dog/cat`, `dog/banana`, and `cat/banana` results;
7. a 20-row related-vs-unrelated sanity suite (>=80% pairwise accuracy and positive mean margin);
8. nearest-neighbor output for manual inspection.

The semantic suite is explicitly a sanity gate, not a benchmark of general semantic quality.

## Independent execution evidence

An independent notebook currently documents an exact `en_core_web_md==3.8.0` installation and successful `spacy.load("en_core_web_md")`. It reports 300-dimensional vectors, non-zero vectors for common words, zero-vector OOV behavior, and the canonical similarity values:

- dog↔cat: approximately `0.80168545`
- dog↔banana: approximately `0.24327646`
- cat↔banana: approximately `0.28154364`

This is independent evidence about the exact model version, but not a substitute for executing this fork's pinned verifier.

## Status

- Artifact existence and release metadata: **ESTABLISHED**
- Exact wheel checksum: **ESTABLISHED**
- Exact 3.8.0 external load + vector behavior: **EXPERIMENTALLY_SUPPORTED**
- This fork's complete reproducible CI verification: **OPEN**

Do not build production functionality on this model until the fork's verifier produces a recorded PASS.
