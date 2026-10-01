import random

from jevoss.calibrate import apply, fit, fit_temperature, rescale
from jevoss.metrics import Decision, ece, nll


def overconfident(n=600, seed=0):
    """True accuracy 70%, but the model says 95%."""
    rng = random.Random(seed)
    out = []
    for i in range(n):
        gold = "a" if rng.random() < 0.7 else "b"
        out.append(Decision(str(i), "q", "choice", "tr", ("a", "b"), (0.95, 0.05), gold))
    return out


def test_fit_softens_overconfident_model():
    ds = overconfident()
    t = fit_temperature(ds)
    assert t > 1.5
    fixed = apply(ds, {"temperatures": {"default": t}})
    assert ece(fixed) < ece(ds) and nll(fixed) < nll(ds)
    assert abs(fixed[0].probs[0] - 0.7) < 0.02


def test_rescale_keeps_argmax():
    assert max(range(3), key=lambda i: rescale([0.5, 0.3, 0.2], 3.0)[i]) == 0


def test_group_keys_follow_engine_format():
    cal = fit(overconfident(400), min_group=100)
    assert {"default", "choice", "choice:tr"} <= set(cal["temperatures"])


def test_conformal_sets_reach_coverage():
    from jevoss.calibrate import conformal_threshold

    rng = random.Random(1)
    calib, test = [], []
    for i in range(2000):
        gold = rng.choice("abc")
        p = [0.2, 0.2, 0.2]
        p["abc".index(gold) if rng.random() < 0.6 else rng.randrange(3)] += 0.4
        (calib if i < 1000 else test).append(Decision(str(i), "q", "choice", "en", ("a", "b", "c"), tuple(p), gold))
    q = conformal_threshold(calib, 0.9)
    covered = sum(1 - d.probs[d.values.index(d.gold)] <= q for d in test) / len(test)
    assert covered >= 0.88


def test_soft_gold_fit_does_not_sharpen():
    from jevoss.calibrate import fit_temperature

    ds = [Decision(str(i), "q", "choice", "en", ("a", "b"), (0.7, 0.3), "a", (0.7, 0.3)) for i in range(300)]
    assert abs(fit_temperature(ds) - 1.0) < 0.05


def test_auto_threshold_targets_low_confidence_errors():
    from jevoss.calibrate import fit_auto_threshold

    off, on = [], []
    for i in range(200):
        sure = i % 2 == 0
        # confident answers are right; unsure ones are wrong without reasoning and right with it
        off.append(Decision(str(i), "q", "choice", "en", ("a", "b", "c"), (0.95, 0.03, 0.02) if sure else (0.4, 0.35, 0.25), "a" if sure else "b"))
        on.append(Decision(str(i), "q", "choice", "en", ("a", "b", "c"), (0.95, 0.03, 0.02) if sure else (0.2, 0.7, 0.1), "a" if sure else "b"))
    res = fit_auto_threshold(off, on)["choice"]
    assert res["accuracy_off"] == 0.5 and res["accuracy_auto"] == 1.0
    assert res["reasoning_share"] == 0.5 and 0.1 <= res["threshold"] <= 0.95
