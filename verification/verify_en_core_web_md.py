import json
import math
from pathlib import Path

import numpy as np
import spacy

MODEL = "en_core_web_md"
EXPECTED_MODEL_VERSION = "3.8.0"
EXPECTED_SHAPE = (20_000, 300)
EXPECTED_KEYS = 684_830

# Independent execution reference for en_core_web_md 3.8.0:
# dog/cat ~= 0.80168545 and dog/banana ~= 0.24327646.
# These are regression anchors, not a claim of general model quality.
REFERENCE_SIMILARITIES = {
    ("dog", "cat"): 0.80168545,
    ("dog", "banana"): 0.24327646,
    ("cat", "banana"): 0.28154364,
}
REFERENCE_ABS_TOL = 1e-5

PAIRWISE_SANITY = [
    ("dog", "cat", "banana"),
    ("doctor", "hospital", "music"),
    ("teacher", "school", "banana"),
    ("car", "vehicle", "banana"),
    ("computer", "software", "banana"),
    ("coffee", "tea", "airplane"),
    ("guitar", "music", "hospital"),
    ("ocean", "sea", "computer"),
    ("lawyer", "court", "banana"),
    ("airplane", "airport", "rose"),
    ("banana", "fruit", "hospital"),
    ("rose", "flower", "computer"),
    ("river", "water", "software"),
    ("book", "library", "banana"),
    ("medicine", "doctor", "guitar"),
    ("restaurant", "food", "airplane"),
    ("king", "queen", "banana"),
    ("winter", "summer", "hospital"),
    ("bread", "butter", "computer"),
    ("money", "bank", "banana"),
]


def token(nlp, word):
    return nlp(word)[0]


def similarity(nlp, a, b):
    return float(token(nlp, a).similarity(token(nlp, b)))


def row_diagnostics(nlp, words):
    out = {}
    for word in words:
        orth = nlp.vocab.strings[word]
        row = nlp.vocab.vectors.key2row.get(orth)
        vec = nlp.vocab[word].vector
        out[word] = {
            "orth": int(orth),
            "row": None if row is None else int(row),
            "norm": float(np.linalg.norm(vec)),
            "first8": [float(x) for x in vec[:8]],
        }
    dog = nlp.vocab["dog"].vector
    cat = nlp.vocab["cat"].vector
    dog_norm = float(np.linalg.norm(dog))
    cat_norm = float(np.linalg.norm(cat))
    manual = float(np.dot(dog, cat) / (dog_norm * cat_norm))
    out["_dog_cat_manual_cosine"] = manual
    out["_dog_cat_vector_equal"] = bool(np.array_equal(dog, cat))
    return out


def nearest_words(nlp, word, n=8):
    query = token(nlp, word)
    keys, _, scores = nlp.vocab.vectors.most_similar(
        query.vector.reshape(1, -1), n=n + 1
    )
    out = []
    for key, score in zip(keys[0], scores[0]):
        candidate = nlp.vocab.strings[int(key)]
        if candidate == word:
            continue
        out.append({"word": candidate, "similarity": float(score)})
        if len(out) == n:
            break
    return out


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"not JSON serializable: {type(value)!r}")


def main():
    nlp = spacy.load(MODEL)
    vectors = nlp.vocab.vectors

    shape = tuple(int(x) for x in vectors.shape)
    raw_rows = vectors.data
    finite_all = bool(np.isfinite(raw_rows).all())
    nonzero_rows = int(np.count_nonzero(np.linalg.norm(raw_rows, axis=1) > 0))
    unique_rows = int(np.unique(raw_rows, axis=0).shape[0])
    duplicate_row_count = int(shape[0] - unique_rows)

    common_words = sorted({w for row in PAIRWISE_SANITY for w in row})
    vector_presence = {
        w: bool(token(nlp, w).has_vector) for w in common_words
    }

    oov_word = "qzxvplmn_unseen_token"
    oov = token(nlp, oov_word)

    identity = similarity(nlp, "dog", "dog")
    symmetry_ab = similarity(nlp, "dog", "cat")
    symmetry_ba = similarity(nlp, "cat", "dog")

    reference_results = {}
    for pair, expected in REFERENCE_SIMILARITIES.items():
        actual = similarity(nlp, *pair)
        reference_results[f"{pair[0]}::{pair[1]}"] = {
            "expected": expected,
            "actual": actual,
            "absolute_error": abs(actual - expected),
            "pass": abs(actual - expected) <= REFERENCE_ABS_TOL,
        }

    pairwise = []
    for anchor, related, unrelated in PAIRWISE_SANITY:
        rel = similarity(nlp, anchor, related)
        unr = similarity(nlp, anchor, unrelated)
        pairwise.append(
            {
                "anchor": anchor,
                "related": related,
                "unrelated": unrelated,
                "related_similarity": rel,
                "unrelated_similarity": unr,
                "margin": rel - unr,
                "pass": rel > unr,
            }
        )

    pairwise_accuracy = sum(x["pass"] for x in pairwise) / len(pairwise)
    mean_pairwise_margin = sum(x["margin"] for x in pairwise) / len(pairwise)

    probes = {
        "dog_cat": similarity(nlp, "dog", "cat"),
        "dog_banana": similarity(nlp, "dog", "banana"),
        "doctor_hospital": similarity(nlp, "doctor", "hospital"),
        "doctor_music": similarity(nlp, "doctor", "music"),
        "computer_software": similarity(nlp, "computer", "software"),
        "computer_banana": similarity(nlp, "computer", "banana"),
        "king_queen": similarity(nlp, "king", "queen"),
        "king_banana": similarity(nlp, "king", "banana"),
    }

    checks = {
        "model_version": nlp.meta["version"] == EXPECTED_MODEL_VERSION,
        "vector_shape": shape == EXPECTED_SHAPE,
        "vector_keys": bool(vectors.n_keys == EXPECTED_KEYS),
        "vectors_finite": finite_all,
        "nonzero_vector_rows": nonzero_rows > 1_000,
        "unique_rows_recorded": unique_rows > 0,
        "sanity_words_have_vectors": all(vector_presence.values()),
        "dog_has_vector": token(nlp, "dog").has_vector,
        "dog_vector_nonzero": token(nlp, "dog").vector_norm > 0,
        "identity_similarity": math.isclose(
            identity, 1.0, rel_tol=0, abs_tol=1e-6
        ),
        "symmetry": math.isclose(
            symmetry_ab, symmetry_ba, rel_tol=0, abs_tol=1e-6
        ),
        "oov_has_no_vector": not oov.has_vector,
        "oov_zero_norm": oov.vector_norm == 0,
        "reference_similarities": all(
            row["pass"] for row in reference_results.values()
        ),
        "pairwise_sanity_accuracy": pairwise_accuracy >= 0.80,
        "mean_pairwise_margin_positive": mean_pairwise_margin > 0,
    }

    result = {
        "spacy_version": spacy.__version__,
        "model": MODEL,
        "model_version": nlp.meta["version"],
        "vectors_shape": list(shape),
        "vector_keys": int(vectors.n_keys),
        "nonzero_vector_rows": nonzero_rows,
        "unique_rows": unique_rows,
        "duplicate_row_count": duplicate_row_count,
        "vector_presence": vector_presence,
        "oov": {
            "text": oov_word,
            "has_vector": bool(oov.has_vector),
            "vector_norm": float(oov.vector_norm),
        },
        "identity_similarity": identity,
        "symmetry": {
            "dog_cat": symmetry_ab,
            "cat_dog": symmetry_ba,
        },
        "reference_similarities": reference_results,
        "probes": probes,
        "pairwise_sanity_accuracy": pairwise_accuracy,
        "mean_pairwise_margin": mean_pairwise_margin,
        "pairwise_sanity": pairwise,
        "row_diagnostics": row_diagnostics(nlp, ["dog", "cat", "banana", "computer", "software", "doctor", "hospital", "king", "queen"]),
        "nearest_neighbors": {
            word: nearest_words(nlp, word)
            for word in ("dog", "computer", "doctor", "king")
        },
        "checks": checks,
        "all_pass": all(checks.values()),
    }

    print(json.dumps(result, indent=2, sort_keys=True, default=json_default))
    Path("vector-verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if not result["all_pass"]:
        raise SystemExit("vector verification failed")


if __name__ == "__main__":
    main()
