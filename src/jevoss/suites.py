"""Benchmark suites in one canonical shape.

Item: {"id", "lang", "state", "questions", "targets": {field: {"label", "dist"}}, "tags"}.
``dist`` maps option values to gold probabilities when the source has them.
Loaders read public Hugging Face datasets or the public Intern-Decision benchmark files.
"""

from __future__ import annotations

import json
import random
import urllib.request
from collections.abc import Iterator
from functools import cache
from typing import Any

INTERN = "https://raw.githubusercontent.com/internlm/Intern-Decision/main/benchmarks/accuracy-v1"


def option_values(question: dict[str, Any]) -> tuple[str, ...]:
    kind = question["type"]
    if kind == "noul":
        return ("no", "yes")
    criteria = question["criteria"]
    if kind == "score" and isinstance(criteria, list):
        return tuple(str(i) for i in range(len(criteria)))
    return tuple(str(k) for k in criteria)


def _noul_label(value: Any) -> str:
    return "yes" if str(value).lower() in {"yes", "true", "1"} else "no"


def _jsonl(url: str) -> Iterator[dict]:
    with urllib.request.urlopen(url, timeout=60) as response:
        for line in response.read().decode("utf-8").splitlines():
            if line.strip():
                yield json.loads(line)


def typed_decisions(split: str = "test") -> Iterator[dict]:
    """LocalLLaMA/typed-decisions: 5 questions per state, gold = teacher distributions."""
    from datasets import load_dataset

    for row in load_dataset("LocalLLaMA/typed-decisions", "all", split=split):
        questions = json.loads(row["questions"])
        gold = json.loads(row["gold"])
        targets = {}
        for name, q in questions.items():
            g = gold[name]
            if q["type"] == "noul":
                probs = {_noul_label(k): v for k, v in g["probabilities"].items()}
                targets[name] = {"label": _noul_label(g["label"]), "dist": probs}
            else:
                targets[name] = {"label": str(g["label"]), "dist": {str(k): v for k, v in g["probabilities"].items()}}
        yield {
            "id": row["id"],
            "lang": "en",
            "state": json.loads(row["state"]) if row["state"].startswith("{") else row["state"],
            "questions": questions,
            "targets": targets,
            "tags": [f"workflow:{row['workflow']}"],
        }


def jevbench(tier: str) -> Iterator[dict]:
    """Public JevBench items (easy, original, hard) as shipped with Intern-Decision."""
    for row in _jsonl(f"{INTERN}/jevbench/{tier}.jsonl"):
        q = row["question"]
        label = _noul_label(row["expected"]) if q["type"] == "noul" else str(row["expected"])
        target = {"label": label}
        if row.get("gold_probs"):
            gp = row["gold_probs"]
            target["dist"] = {(_noul_label(k) if q["type"] == "noul" else str(k)): v for k, v in gp.items()}
        yield {
            "id": row["id"],
            "lang": "en",
            "state": row["state"],
            "questions": {"q": q},
            "targets": {"q": target},
            "tags": [f"tier:{tier}", f"family:{row.get('family', '')}"],
        }


def intern_canonical(name: str) -> Iterator[dict]:
    """Intern-Decision canonical suites: agnews, toolace, typed_decisions, wildjailbreak."""
    for row in _jsonl(f"{INTERN}/{name}/test.jsonl"):
        targets = {}
        for field, q in row["questions"].items():
            label = row["targets"][field]["label"]
            targets[field] = {"label": _noul_label(label) if q["type"] == "noul" else str(label)}
        yield {"id": row["id"], "lang": "en", "state": row["state"], "questions": row["questions"], "targets": targets, "tags": [f"suite:{name}"]}


MASSIVE_Q = {
    "en": "Which scenario does this voice-assistant request belong to?",
    "tr": "Bu sesli asistan isteği hangi senaryoya ait?",
    "de": "Zu welchem Szenario gehört diese Sprachassistenten-Anfrage?",
}


def massive(lang: str, limit: int | None = None, seed: int = 0) -> Iterator[dict]:
    """MASSIVE scenario classification (CC BY 4.0), 18 options, native test utterances."""
    from datasets import load_dataset

    rows = list(load_dataset("mteb/amazon_massive_scenario", lang, split="test"))
    labels = sorted({r["label"] for r in rows})
    criteria = {label: label.replace("_", " ") for label in labels}
    random.Random(seed).shuffle(rows)
    for i, r in enumerate(rows[:limit] if limit else rows):
        yield {
            "id": f"massive-{lang}-{i}",
            "lang": lang,
            "state": r["text"],
            "questions": {"scenario": {"type": "choice", "instructions": MASSIVE_Q[lang], "criteria": criteria}},
            "targets": {"scenario": {"label": r["label"]}},
            "tags": ["suite:massive"],
        }


MMLU_Q = {
    "en": "Which answer is correct?",
    "tr": "Hangi cevap doğru?",
    "de": "Welche Antwort ist richtig?",
}


def global_mmlu(lang: str, limit: int | None = 400) -> Iterator[dict]:
    """Global-MMLU (Apache-2.0), the same questions in every language (parallel ids).

    Samples a fixed set of question ids by hash, so EN, TR and DE see identical items.
    """
    import hashlib

    from datasets import load_dataset

    rows = sorted(load_dataset("CohereLabs/Global-MMLU", lang, split="test"), key=lambda r: hashlib.sha1(r["sample_id"].encode()).hexdigest())
    for r in rows[:limit] if limit else rows:
        criteria = {k: r[f"option_{k.lower()}"] for k in "ABCD"}
        yield {
            "id": f"gmmlu-{r['sample_id']}",
            "lang": lang,
            "state": r["question"],
            "questions": {"answer": {"type": "choice", "instructions": MMLU_Q[lang], "criteria": criteria}},
            "targets": {"answer": {"label": r["answer"]}},
            "tags": ["suite:global-mmlu", f"subject:{r['subject']}", f"category:{r['subject_category']}"],
        }


def turkish_mmlu(limit: int | None = 400) -> Iterator[dict]:
    """TurkishMMLU: questions written in Turkish for Turkish exams (5 options). Evaluation only."""
    import ast
    import hashlib

    from datasets import load_dataset

    rows = sorted(load_dataset("AYueksel/TurkishMMLU", "All", split="test"), key=lambda r: hashlib.sha1(r["question"].encode()).hexdigest())
    for i, r in enumerate(rows[:limit] if limit else rows):
        choices = ast.literal_eval(r["choices"]) if isinstance(r["choices"], str) else r["choices"]
        letters = "ABCDE"[: len(choices)]
        yield {
            "id": f"trmmlu-{i}",
            "lang": "tr",
            "state": r["question"],
            "questions": {"answer": {"type": "choice", "instructions": "Hangi seçenek doğru?", "criteria": dict(zip(letters, choices))}},
            "targets": {"answer": {"label": letters[int(r["answer"])]}},
            "tags": ["suite:turkish-mmlu", f"subject:{r['subject']}"],
        }


GERMEVAL_CRITERIA = {
    "positive": "Der Text äußert sich positiv über die Deutsche Bahn.",
    "negative": "Der Text äußert sich negativ über die Deutsche Bahn.",
    "neutral": "Der Text ist sachlich oder äußert keine klare Haltung.",
}


def germeval2017(limit: int | None = 400, seed: int = 0) -> Iterator[dict]:
    """GermEval 2017 subtask B: sentiment towards Deutsche Bahn in German posts. Evaluation only (CC BY-NC)."""
    from datasets import load_dataset

    rows = [r for r in load_dataset("uhhlt/GermEval2017", split="test_syn") if r["Relevance"] in (True, "True")]
    random.Random(seed).shuffle(rows)
    for i, r in enumerate(rows[:limit] if limit else rows):
        yield {
            "id": f"germeval17-{i}",
            "lang": "de",
            "state": r["Text"],
            "questions": {"sentiment": {"type": "choice", "instructions": "Welche Haltung zur Deutschen Bahn zeigt der Text?", "criteria": GERMEVAL_CRITERIA}},
            "targets": {"sentiment": {"label": r["Sentiment"]}},
            "tags": ["suite:germeval2017"],
        }


def gnad10(limit: int | None = 400, seed: int = 0) -> Iterator[dict]:
    """10kGNAD: Austrian newspaper articles by section (9 options). Evaluation only (CC BY-NC-SA)."""
    from datasets import load_dataset

    ds = load_dataset("community-datasets/gnad10", split="test")
    names = ds.features["label"].names
    rows = list(ds)
    random.Random(seed).shuffle(rows)
    criteria = {n: None for n in names}
    for i, r in enumerate(rows[:limit] if limit else rows):
        yield {
            "id": f"gnad10-{i}",
            "lang": "de",
            "state": r["text"][:3000],
            "questions": {"section": {"type": "choice", "instructions": "In welches Ressort gehört dieser Artikel?", "criteria": criteria}},
            "targets": {"section": {"label": names[r["label"]]}},
            "tags": ["suite:gnad10"],
        }


def local(path: str) -> Iterator[dict]:
    """Any JSONL file already in canonical shape (for example our frozen JevAlt tests)."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


@cache
def registry() -> dict[str, Any]:
    return {
        "typed-decisions": lambda **kw: typed_decisions(),
        "jevbench-easy": lambda **kw: jevbench("easy"),
        "jevbench-original": lambda **kw: jevbench("original"),
        "jevbench-hard": lambda **kw: jevbench("hard"),
        "agnews": lambda **kw: intern_canonical("agnews"),
        "toolace": lambda **kw: intern_canonical("toolace"),
        "wildjailbreak": lambda **kw: intern_canonical("wildjailbreak"),
        **{f"massive-{l}": (lambda l=l, **kw: massive(l, **kw)) for l in ("en", "tr", "de")},
        **{f"gmmlu-{l}": (lambda l=l, **kw: global_mmlu(l, **kw)) for l in ("en", "tr", "de")},
        "turkish-mmlu": lambda **kw: turkish_mmlu(**kw),
        "germeval2017": lambda **kw: germeval2017(**kw),
        "gnad10": lambda **kw: gnad10(**kw),
    }


def load(name: str, **kwargs) -> list[dict]:
    if name.endswith(".jsonl"):
        return list(local(name))
    return list(registry()[name](**kwargs))
