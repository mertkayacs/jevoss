"""Group decision records and write result tables."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Sequence

from .metrics import Decision, summarize


def breakdown(ds: Sequence[Decision], key: str) -> dict[str, dict]:
    groups: dict[str, list[Decision]] = defaultdict(list)
    for d in ds:
        if key == "type":
            groups[d.kind].append(d)
        elif key == "lang":
            groups[d.lang].append(d)
        else:
            for tag in d.tags:
                if tag.startswith(key + ":"):
                    groups[tag.split(":", 1)[1]].append(d)
    return {name: summarize(group) for name, group in sorted(groups.items())}


def result(ds: Sequence[Decision], *, suite: str, model: str, extra: dict | None = None) -> dict:
    return {
        "suite": suite,
        "model": model,
        **(extra or {}),
        "overall": summarize(ds),
        "by_type": breakdown(ds, "type"),
        "by_lang": breakdown(ds, "lang"),
    }


def table(results: Sequence[dict], metrics=("accuracy", "brier", "ece", "kl_to_gold", "auroc")) -> str:
    """Markdown table, one row per (model, suite)."""
    head = "| model | suite | n | " + " | ".join(metrics) + " |"
    rows = [head, "|" + "---|" * (3 + len(metrics))]
    for r in results:
        o = r["overall"]
        cells = ["-" if o.get(m) is None else f"{o[m]:.3f}" for m in metrics]
        rows.append(f"| {r['model']} | {r['suite']} | {o['n']} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def dump(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
