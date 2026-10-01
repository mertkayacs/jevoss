import math

from jevoss.metrics import Decision, accuracy, brier, coverage_at_risk, ece, kl_to_gold, nll, paired_difference, selective_auroc


def d(i, probs, gold, dist=None):
    return Decision(item=str(i), field="q", kind="choice", lang="en", values=("a", "b"), probs=probs, gold=gold, gold_dist=dist)


def test_perfect_model():
    ds = [d(i, (1.0, 0.0), "a") for i in range(10)]
    assert accuracy(ds) == 1.0 and brier(ds) == 0.0 and ece(ds) == 0.0
    assert nll(ds) < 1e-9


def test_brier_and_nll_values():
    ds = [d(0, (0.8, 0.2), "a")]
    assert math.isclose(brier(ds), 0.2**2 + 0.2**2)
    assert math.isclose(nll(ds), -math.log(0.8))


def test_ece_detects_overconfidence():
    ds = [d(i, (0.9, 0.1), "a" if i < 5 else "b") for i in range(10)]
    assert math.isclose(ece(ds, bins=1), 0.4)


def test_kl_zero_when_matching_gold():
    ds = [d(0, (0.7, 0.3), "a", (0.7, 0.3))]
    assert kl_to_gold(ds) < 1e-12


def test_auroc_and_coverage():
    ds = [d(0, (0.9, 0.1), "a"), d(1, (0.6, 0.4), "b"), d(2, (0.8, 0.2), "a")]
    assert selective_auroc(ds) == 1.0
    assert math.isclose(coverage_at_risk(ds, 0.0), 2 / 3)


def test_paired_difference_sign():
    a = [d(i, (0.6, 0.4), "a") for i in range(20)]
    b = [d(i, (0.9, 0.1), "a") for i in range(20)]
    point, (lo, hi) = paired_difference(a, b, brier, n=200)
    assert point < 0 and hi < 0
