import itertools
import json
import math
from pathlib import Path

import numpy as np
import spacy

MODEL = "en_core_web_lg"
EXPECTED_MODEL_VERSION = "3.8.0"
EXPECTED_SHAPE = (342_918, 300)
EXPECTED_KEYS = 684_830

SEMANTIC_WORDS = [
    "dog", "cat", "banana", "computer", "software", "doctor", "hospital",
    "guitar", "ocean", "river", "airplane", "airport", "teacher", "school",
    "lawyer", "court", "restaurant", "food", "king", "queen", "winter",
    "summer", "money", "bank", "book", "library", "coffee", "tea", "rose",
    "flower", "vehicle", "car", "medicine", "music", "bread", "butter",
    "fruit", "water", "keyboard", "phone", "house", "tree", "mountain",
    "piano", "camera", "engine", "forest", "student", "sea", "air",
]

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


def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"not JSON serializable: {type(value)!r}")


def main():
    nlp = spacy.load(MODEL)
    vectors = nlp.vocab.vectors

    shape = tuple(int(x) for x in vectors.shape)
    raw_rows = vectors.data
    row_norms = np.linalg.norm(raw_rows, axis=1)

    finite_all = bool(np.isfinite(raw_rows).all())
    zero_rows = int(np.count_nonzero(row_norms == 0))
    nonzero_rows = int(np.count_nonzero(row_norms > 0))
    unique_rows = int(np.unique(raw_rows, axis=0).shape[0])
    duplicate_rows = int(shape[0] - unique_rows)
    unique_nonzero_rows = int(
        np.unique(raw_rows[row_norms > 0], axis=0).shape[0]
    )
    duplicate_nonzero_rows = int(nonzero_rows - unique_nonzero_rows)

    cache = {}
    for word in set(SEMANTIC_WORDS + [w for row in PAIRWISE_SANITY for w in row]):
        cache[word] = nlp.vocab[word].vector
    norms = {word: float(np.linalg.norm(vec)) for word, vec in cache.items()}

    vector_presence = {
        word: bool(nlp.vocab[word].has_vector)
        for word in cache
    }

    pairwise = []
    for anchor, related, unrelated in PAIRWISE_SANITY:
        related_score = cosine(cache[anchor], cache[related])
        unrelated_score = cosine(cache[anchor], cache[unrelated])
        pairwise.append({
            "anchor": anchor,
            "related": related,
            "unrelated": unrelated,
            "related_similarity": related_score,
            "unrelated_similarity": unrelated_score,
            "margin": related_score - unrelated_score,
            "pass": related_score > unrelated_score,
        })

    pairwise_accuracy = sum(row["pass"] for row in pairwise) / len(pairwise)
    mean_margin = sum(row["margin"] for row in pairwise) / len(pairwise)

    semantic_pairs = []
    for left, right in itertools.combinations(SEMANTIC_WORDS, 2):
        score = cosine(cache[left], cache[right])
        semantic_pairs.append({
            "left": left,
            "right": right,
            "similarity": score,
            "saturated": score >= 0.999,
        })

    saturated_pairs = [
        row for row in semantic_pairs if row["saturated"]
    ]
    similarities = np.asarray(
        [row["similarity"] for row in semantic_pairs], dtype=np.float64
    )

    oov_word = "qzxvplmn_unseen_token"
    oov = nlp.vocab[oov_word]

    dog = cache["dog"]
    cat = cache["cat"]

    identity = cosine(dog, dog)
    dog_cat = cosine(dog, cat)
    cat_dog = cosine(cat, dog)

    probes = {
        "dog_cat": dog_cat,
        "dog_banana": cosine(dog, cache["banana"]),
        "doctor_hospital": cosine(cache["doctor"], cache["hospital"]),
        "doctor_music": cosine(cache["doctor"], cache["music"]),
        "computer_software": cosine(cache["computer"], cache["software"]),
        "computer_banana": cosine(cache["computer"], cache["banana"]),
        "king_queen": cosine(cache["king"], cache["queen"]),
        "king_banana": cosine(cache["king"], cache["banana"]),
    }

    checks = {
        "model_version": nlp.meta["version"] == EXPECTED_MODEL_VERSION,
        "vector_shape": shape == EXPECTED_SHAPE,
        "vector_keys": bool(vectors.n_keys == EXPECTED_KEYS),
        "vector_mode_default": vectors.mode == "default",
        "vectors_finite": finite_all,
        "zero_rows_none": zero_rows == 0,
        "all_probe_words_have_vectors": all(vector_presence.values()),
        "nonzero_probe_norms": all(norm > 0 for norm in norms.values()),
        "identity_similarity": math.isclose(
            identity, 1.0, rel_tol=0, abs_tol=1e-6
        ),
        "symmetry": math.isclose(
            dog_cat, cat_dog, rel_tol=0, abs_tol=1e-6
        ),
        "oov_has_no_vector": not oov.has_vector,
        "oov_zero_norm": oov.vector_norm == 0,
        "pairwise_sanity_accuracy": pairwise_accuracy >= 0.80,
        "mean_pairwise_margin_positive": mean_margin > 0,
        "no_nonidentical_similarity_saturation": len(saturated_pairs) == 0,
        "unique_nonzero_rows_equals_nonzero_rows": (
            unique_nonzero_rows == nonzero_rows
        ),
    }

    nearest_neighbors = {}
    for word in ("dog", "computer", "doctor", "king"):
        query = cache[word].reshape(1, -1)
        keys, _, scores = vectors.most_similar(query, n=9)
        rows = []
        for key, score in zip(keys[0], scores[0]):
            candidate = nlp.vocab.strings[int(key)]
            if candidate == word:
                continue
            rows.append({
                "word": candidate,
                "similarity": float(score),
            })
            if len(rows) == 8:
                break
        nearest_neighbors[word] = rows

    result = {
        "spacy_version": spacy.__version__,
        "model": MODEL,
        "model_version": nlp.meta["version"],
        "vectors_shape": list(shape),
        "vector_keys": int(vectors.n_keys),
        "vector_mode": vectors.mode,
        "nonzero_rows": nonzero_rows,
        "zero_rows": zero_rows,
        "unique_rows": unique_rows,
        "duplicate_row_count": duplicate_rows,
        "unique_nonzero_rows": unique_nonzero_rows,
        "duplicate_nonzero_rows": duplicate_nonzero_rows,
        "probe_word_count": len(cache),
        "pair_count": len(semantic_pairs),
        "saturated_pair_count": len(saturated_pairs),
        "max_nonidentical_similarity": float(similarities.max()),
        "similarity_quantiles": {
            "p50": float(np.quantile(similarities, 0.50)),
            "p90": float(np.quantile(similarities, 0.90)),
            "p99": float(np.quantile(similarities, 0.99)),
        },
        "pairwise_sanity_accuracy": pairwise_accuracy,
        "mean_pairwise_margin": mean_margin,
        "probes": probes,
        "oov": {
            "text": oov_word,
            "has_vector": bool(oov.has_vector),
            "vector_norm": float(oov.vector_norm),
        },
        "identity_similarity": identity,
        "symmetry": {
            "dog_cat": dog_cat,
            "cat_dog": cat_dog,
        },
        "saturated_pairs": saturated_pairs,
        "pairwise_sanity": pairwise,
        "nearest_neighbors": nearest_neighbors,
        "checks": checks,
        "all_pass": all(checks.values()),
    }

    print(json.dumps(result, indent=2, sort_keys=True, default=json_default))
    Path("lg-vector-verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, default=json_default) + "\n",
        encoding="utf-8",
    )

    if not result["all_pass"]:
        raise SystemExit("lg vector verification failed")


if __name__ == "__main__":
    main()
