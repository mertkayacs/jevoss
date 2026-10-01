"""Decision metrics: accuracy, proper scores, calibration, selective prediction.

Every metric works on flat decision records, one per answered question.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

EPS = 1e-12


@dataclass
class Decision:
    item: str  # row id, used to cluster the bootstrap
    field: str
    kind: str  # choice | score | noul
    lang: str
    values: tuple[str, ...]
    probs: tuple[float, ...]  # model probabilities, same order as values
    gold: str  # gold label
    gold_dist: tuple[float, ...] | None = None  # optional gold distribution
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def pred(self) -> str:
        best = max(range(len(self.values)), key=lambda i: (self.probs[i], -i))
        return self.values[best]

    @property
    def p_max(self) -> float:
        return max(self.probs)

    @property
    def correct(self) -> bool:
        return self.pred == self.gold

    @property
    def p_gold(self) -> float:
        return self.probs[self.values.index(self.gold)]


def accuracy(ds: Sequence[Decision]) -> float:
    return sum(d.correct for d in ds) / len(ds)


def brier(ds: Sequence[Decision]) -> float:
    """Multiclass Brier: sum over options of (p - onehot)^2, averaged over decisions."""
    total = 0.0
    for d in ds:
        g = d.values.index(d.gold)
        total += sum((p - (i == g)) ** 2 for i, p in enumerate(d.probs))
    return total / len(ds)


def soft_brier(ds: Sequence[Decision]) -> float | None:
    """Brier against the gold distribution, for suites whose gold is a distribution."""
    rows = [d for d in ds if d.gold_dist]
    if not rows:
        return None
    return sum(sum((p - g) ** 2 for p, g in zip(d.probs, d.gold_dist)) for d in rows) / len(rows)


def nll(ds: Sequence[Decision]) -> float:
    return sum(-math.log(max(d.p_gold, EPS)) for d in ds) / len(ds)


def ece(ds: Sequence[Decision], bins: int = 15) -> float:
    """Expected calibration error on the top probability, equal-mass bins."""
    ranked = sorted(ds, key=lambda d: d.p_max)
    n = len(ranked)
    total = 0.0
    for b in range(bins):
        chunk = ranked[b * n // bins : (b + 1) * n // bins]
        if chunk:
            conf = sum(d.p_max for d in chunk) / len(chunk)
            acc = sum(d.correct for d in chunk) / len(chunk)
            total += len(chunk) / n * abs(conf - acc)
    return total


def kl_to_gold(ds: Sequence[Decision]) -> float | None:
    """KL(gold || model), only over decisions that carry a gold distribution."""
    rows = [d for d in ds if d.gold_dist]
    if not rows:
        return None
    total = 0.0
    for d in rows:
        total += sum(g * math.log(max(g, EPS) / max(p, EPS)) for g, p in zip(d.gold_dist, d.probs) if g > 0)
    return total / len(rows)


def selective_auroc(ds: Sequence[Decision]) -> float | None:
    """Probability that a correct decision gets higher confidence than a wrong one."""
    pos = [d.p_max for d in ds if d.correct]
    neg = [d.p_max for d in ds if not d.correct]
    if not pos or not neg:
        return None
    ranked = sorted([(s, 1) for s in pos] + [(s, 0) for s in neg])
    rank_sum, i = 0.0, 0
    while i < len(ranked):
        j = i
        while j < len(ranked) and ranked[j][0] == ranked[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2
        rank_sum += avg_rank * sum(1 for k in range(i, j) if ranked[k][1])
        i = j
    return (rank_sum - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def coverage_at_risk(ds: Sequence[Decision], risk: float = 0.05) -> float:
    """Largest share of decisions answerable, most confident first, with error <= risk."""
    ranked = sorted(ds, key=lambda d: -d.p_max)
    best, wrong = 0, 0
    for k, d in enumerate(ranked, 1):
        wrong += not d.correct
        if wrong / k <= risk:
            best = k
    return best / len(ranked)


METRICS: dict[str, Callable[[Sequence[Decision]], float | None]] = {
    "accuracy": accuracy,
    "brier": brier,
    "nll": nll,
    "ece": ece,
    "kl_to_gold": kl_to_gold,
    "soft_brier": soft_brier,
    "auroc": selective_auroc,
    "coverage@5%": coverage_at_risk,
}


def summarize(ds: Sequence[Decision]) -> dict[str, float | None]:
    out: dict[str, float | None] = {"n": len(ds)}
    for name, fn in METRICS.items():
        out[name] = fn(ds) if ds else None
    return out


def bootstrap(ds: Sequence[Decision], fn: Callable, n: int = 1000, seed: int = 0) -> tuple[float, float]:
    """95% interval, resampling whole items so questions of one row move together."""
    groups: dict[str, list[Decision]] = {}
    for d in ds:
        groups.setdefault(d.item, []).append(d)
    keys = list(groups)
    rng = random.Random(seed)
    stats = []
    for _ in range(n):
        sample = [d for k in rng.choices(keys, k=len(keys)) for d in groups[k]]
        value = fn(sample)
        if value is not None:
            stats.append(value)
    stats.sort()
    return stats[int(0.025 * len(stats))], stats[int(0.975 * len(stats)) - 1]


def paired_difference(a: Sequence[Decision], b: Sequence[Decision], fn: Callable, n: int = 1000, seed: int = 0):
    """Mean and 95% interval of fn(b) - fn(a) over the same decisions, item-clustered."""
    key = lambda d: (d.item, d.field)  # noqa: E731
    left = {key(d): d for d in a}
    pairs = [(left[key(d)], d) for d in b if key(d) in left]
    groups: dict[str, list[tuple[Decision, Decision]]] = {}
    for pa, pb in pairs:
        groups.setdefault(pa.item, []).append((pa, pb))
    keys = list(groups)
    rng = random.Random(seed)
    diffs = []
    for _ in range(n):
        sample = [p for k in rng.choices(keys, k=len(keys)) for p in groups[k]]
        va, vb = fn([p[0] for p in sample]), fn([p[1] for p in sample])
        if va is not None and vb is not None:
            diffs.append(vb - va)
    diffs.sort()
    point = fn([p[1] for p in pairs]) - fn([p[0] for p in pairs])
    return point, (diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1])
