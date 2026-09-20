import json
import math
from pathlib import Path

import numpy as np
import spacy

MODEL = "en_core_web_md"
EXPECTED_MODEL_VERSION = "3.8.0"
EXPECTED_SHAPE = (20_000, 300)
EXPECTED_KEYS = 684_830

# This is a sanity suite, not a benchmark of general semantic quality.
# Each row asks whether a clearly related word is closer to the anchor than
# an intentionally unrelated control. The test is useful for detecting
# missing/degenerate/wrong vector tables before architectural use.
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


def nearest_words(nlp, word, n=8):
    vec = token(nlp, word).vector
    keys, _, scores = nlp.vocab.vectors.most_similar(
        vec.reshape(1, -1), n=n + 1
    )
    out = []
    query_orth = token(nlp, word).orth
    for key, score in zip(keys[0], scores[0]):
        if int(key) == int(query_orth):
            continue
        out.append(
            {
                "word": nlp.vocab.strings[int(key)],
                "similarity": float(score),
            }
        )
        if len(out) == n:
            break
    return out


def main():
    nlp = spacy.load(MODEL)
    vectors = nlp.vocab.vectors

    shape = tuple(int(x) for x in vectors.shape)
    raw_rows = vectors.data
    finite_all = bool(np.isfinite(raw_rows).all())
    nonzero_rows = int(np.count_nonzero(np.linalg.norm(raw_rows, axis=1) > 0))

    common_words = sorted(
        {
            w
            for row in PAIRWISE_SANITY
            for w in row
        }
    )
    vector_presence = {
        w: bool(token(nlp, w).has_vector)
        for w in common_words
    }

    oov_word = "qzxvplmn_unseen_token"
    oov = token(nlp, oov_word)

    identity = similarity(nlp, "dog", "dog")
    symmetry_ab = similarity(nlp, "dog", "cat")
    symmetry_ba = similarity(nlp, "cat", "dog")

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
    total_positive_margin = sum(x["margin"] for x in pairwise)

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
        "vector_keys": vectors.n_keys == EXPECTED_KEYS,
        "vectors_finite": finite_all,
        "nonzero_vector_rows": nonzero_rows > 1_000,
        "sanity_words_have_vectors": all(vector_presence.values()),
        "dog_has_vector": token(nlp, "dog").has_vector,
        "dog_vector_nonzero": token(nlp, "dog").vector_norm > 0,
        "identity_similarity": math.isclose(identity, 1.0, rel_tol=0, abs_tol=1e-6),
        "symmetry": math.isclose(
            symmetry_ab, symmetry_ba, rel_tol=0, abs_tol=1e-6
        ),
        "oov_has_no_vector": not oov.has_vector,
        "oov_zero_norm": oov.vector_norm == 0,
        "pairwise_sanity_accuracy": pairwise_accuracy >= 0.80,
        "mean_pairwise_margin_positive": (
            total_positive_margin / len(pairwise) > 0
        ),
    }

    result = {
        "spacy_version": spacy.__version__,
        "model": MODEL,
        "model_version": nlp.meta["version"],
        "vectors_shape": list(shape),
        "vector_keys": vectors.n_keys,
        "nonzero_vector_rows": nonzero_rows,
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
        "probes": probes,
        "pairwise_sanity_accuracy": pairwise_accuracy,
        "pairwise_sanity": pairwise,
        "nearest_neighbors": {
            word: nearest_words(nlp, word)
            for word in ("dog", "computer", "doctor", "king")
        },
        "checks": checks,
        "all_pass": all(checks.values()),
    }

    print(json.dumps(result, indent=2, sort_keys=True))

    Path("vector-verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if not result["all_pass"]:
        raise SystemExit("vector verification failed")


if __name__ == "__main__":
    main()
