"""Temperature scaling fitted on held-out decisions.

softmax(log p / T) equals softmax(logits / T), so a temperature can be fitted
from returned probabilities alone. One temperature per (type, language), with
fallbacks to the type and then to a global value when a group is small.
Argmax never changes.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence

from .metrics import Decision

EPS = 1e-12


def rescale(probs: Sequence[float], temperature: float) -> list[float]:
    logs = [math.log(max(p, EPS)) / temperature for p in probs]
    top = max(logs)
    weights = [math.exp(x - top) for x in logs]
    total = sum(weights)
    return [w / total for w in weights]


def nll_at(ds: Sequence[Decision], temperature: float) -> float:
    """Cross-entropy against the gold distribution when the suite has one, else against the label.

    Fitting a soft-gold suite against its argmax would reward sharpening towards the mode.
    """
    total = 0.0
    for d in ds:
        probs = rescale(d.probs, temperature)
        if d.gold_dist:
            total -= sum(g * math.log(max(p, EPS)) for g, p in zip(d.gold_dist, probs) if g > 0)
        else:
            total -= math.log(max(probs[d.values.index(d.gold)], EPS))
    return total / len(ds)


def fit_temperature(ds: Sequence[Decision], lo: float = 0.25, hi: float = 8.0, iters: int = 60) -> float:
    """Golden-section search on log T (NLL is unimodal in T for temperature scaling)."""
    a, b = math.log(lo), math.log(hi)
    phi = (math.sqrt(5) - 1) / 2
    c, d = b - phi * (b - a), a + phi * (b - a)
    fc, fd = nll_at(ds, math.exp(c)), nll_at(ds, math.exp(d))
    for _ in range(iters):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - phi * (b - a)
            fc = nll_at(ds, math.exp(c))
        else:
            a, c, fc = c, d, fd
            d = a + phi * (b - a)
            fd = nll_at(ds, math.exp(d))
    return round(math.exp((a + b) / 2), 4)


def fit(ds: Sequence[Decision], min_group: int = 150) -> dict:
    """Temperatures keyed like the jevalt engine expects: "type:lang", "type", "default"."""
    temps: dict[str, float] = {"default": fit_temperature(ds)}
    by_type: dict[str, list[Decision]] = defaultdict(list)
    by_pair: dict[str, list[Decision]] = defaultdict(list)
    for d in ds:
        by_type[d.kind].append(d)
        by_pair[f"{d.kind}:{d.lang}"].append(d)
    for key, group in by_type.items():
        if len(group) >= min_group:
            temps[key] = fit_temperature(group)
    for key, group in by_pair.items():
        if len(group) >= min_group:
            temps[key] = fit_temperature(group)
    return {"temperatures": temps, "fitted_on": len(ds), "min_group": min_group}


def apply(ds: Sequence[Decision], calibration: dict) -> list[Decision]:
    temps = calibration["temperatures"]
    out = []
    for d in ds:
        t = temps.get(f"{d.kind}:{d.lang}", temps.get(d.kind, temps.get("default", 1.0)))
        out.append(Decision(d.item, d.field, d.kind, d.lang, d.values, tuple(rescale(d.probs, t)), d.gold, d.gold_dist, d.tags))
    return out


def conformal_threshold(ds: Sequence[Decision], coverage: float) -> float:
    """Split conformal: nonconformity 1 - p(gold); the ceil((n+1)c)/n empirical quantile."""
    scores = sorted(1.0 - d.probs[d.values.index(d.gold)] for d in ds)
    n = len(scores)
    k = min(n, math.ceil((n + 1) * coverage))
    return round(scores[k - 1], 6)


def fit_conformal(ds: Sequence[Decision], coverages=(0.8, 0.9, 0.95), min_group: int = 150) -> dict:
    """Thresholds per "type:lang" (fallback "type", "default"), applied to calibrated probabilities."""
    groups: dict[str, list[Decision]] = defaultdict(list)
    for d in ds:
        if d.kind == "noul":
            continue  # a yes/no set is either one answer or both; report the probability instead
        groups[d.kind].append(d)
        groups[f"{d.kind}:{d.lang}"].append(d)
        groups["default"].append(d)
    return {key: {str(c): conformal_threshold(g, c) for c in coverages} for key, g in groups.items() if len(g) >= min_group or key == "default"}


def _conf(d: Decision) -> float:
    """TypeSafe-style confidence for choice/score; distance from a coin flip for noul."""
    if d.kind == "noul":
        return abs(2 * d.probs[1] - 1)
    n = len(d.probs)
    return min(1.0, max(0.0, (n * max(d.probs) - 1) / (n - 1)))


def fit_auto_threshold(off: Sequence[Decision], on: Sequence[Decision], keep_gain: float = 0.9) -> dict:
    """Per-type confidence threshold for reasoning="auto".

    `off` and `on` are the same decisions answered without and with reasoning. For each
    threshold t, decisions with confidence < t use the reasoning answer. Pick the smallest t
    whose accuracy gain reaches `keep_gain` of the best achievable gain; report the cost
    (share of decisions that would reason) next to it.
    """
    key = lambda d: (d.item, d.field)  # noqa: E731
    think = {key(d): d for d in on}
    out = {}
    for kind in sorted({d.kind for d in off}):
        pairs = [(d, think[key(d)]) for d in off if d.kind == kind and key(d) in think]
        if not pairs:
            continue
        base = sum(a.correct for a, _ in pairs) / len(pairs)
        grid = [i / 20 for i in range(21)]
        rows = []
        for t in grid:
            acc = sum((b if _conf(a) < t else a).correct for a, b in pairs) / len(pairs)
            cost = sum(_conf(a) < t for a, _ in pairs) / len(pairs)
            rows.append((t, acc, cost))
        best = max(acc for _, acc, _ in rows)
        target = base + keep_gain * (best - base)
        t, acc, cost = next(r for r in rows if r[1] >= target - 1e-12)
        out[kind] = {"threshold": t, "accuracy_off": round(base, 4), "accuracy_auto": round(acc, 4), "accuracy_on": round(sum(b.correct for _, b in pairs) / len(pairs), 4), "reasoning_share": round(cost, 4), "pairs": len(pairs)}
    return out
