"""Paired comparison of two runs on the same items, with bootstrap intervals.

Runs are decision-record files (JSONL, one decision per line) written by the eval jobs.
"""

from __future__ import annotations

import json

from .metrics import Decision, accuracy, brier, ece, nll, paired_difference


def load(path: str) -> list[Decision]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                d = json.loads(line)
                d["values"], d["probs"] = tuple(d["values"]), tuple(d["probs"])
                d["gold_dist"] = tuple(d["gold_dist"]) if d.get("gold_dist") else None
                d["tags"] = tuple(d.get("tags", ()))
                out.append(Decision(**d))
    return out


def dump(path: str, decisions: list[Decision]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for d in decisions:
            fh.write(json.dumps(d.__dict__, ensure_ascii=False) + "\n")


def compare(a: list[Decision], b: list[Decision], n: int = 2000) -> dict:
    """Difference b - a for each metric (negative Brier/NLL/ECE = b is better)."""
    out = {}
    for name, fn in (("accuracy", accuracy), ("brier", brier), ("nll", nll), ("ece", ece)):
        point, (lo, hi) = paired_difference(a, b, fn, n=n)
        out[name] = {"diff": round(point, 4), "ci95": [round(lo, 4), round(hi, 4)], "significant": lo > 0 or hi < 0}
    out["paired_decisions"] = len({(d.item, d.field) for d in a} & {(d.item, d.field) for d in b})
    return out
