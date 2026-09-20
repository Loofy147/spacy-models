import json
from pathlib import Path

import spacy

MODEL = "en_core_web_md"
EXPECTED_MODEL_VERSION = "3.8.0"
EXPECTED_DIMS = 300
EXPECTED_KEYS = 684_830

def token(nlp, word):
    return nlp(word)[0]

def similarity(nlp, a, b):
    return float(token(nlp, a).similarity(token(nlp, b)))

def main():
    nlp = spacy.load(MODEL)
    vectors = nlp.vocab.vectors

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
        "vector_dimensions": vectors.shape[1] == EXPECTED_DIMS,
        "vector_keys": vectors.n_keys == EXPECTED_KEYS,
        "dog_has_vector": token(nlp, "dog").has_vector,
        "cat_has_vector": token(nlp, "cat").has_vector,
        "dog_cat_gt_dog_banana": probes["dog_cat"] > probes["dog_banana"],
        "doctor_hospital_gt_doctor_music": (
            probes["doctor_hospital"] > probes["doctor_music"]
        ),
        "computer_software_gt_computer_banana": (
            probes["computer_software"] > probes["computer_banana"]
        ),
        "king_queen_gt_king_banana": (
            probes["king_queen"] > probes["king_banana"]
        ),
    }

    result = {
        "spacy_version": spacy.__version__,
        "model": MODEL,
        "model_version": nlp.meta["version"],
        "vectors_shape": list(vectors.shape),
        "vector_keys": vectors.n_keys,
        "probes": probes,
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
