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

## Verification status

At creation of this protocol:

- Artifact existence and metadata: ESTABLISHED from upstream GitHub release.
- Exact wheel checksum: ESTABLISHED from upstream GitHub release metadata.
- Load + runtime semantic checks: OPEN until this repository's CI executes `.github/workflows/vector-verification.yml` successfully.

Do not build production functionality on this model until the CI result is recorded.
