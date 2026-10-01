"""Tests for the needs_unknown fix in runner.py."""

from jevoss.runner import needs_unknown, to_decisions, run, UNKNOWN
from jevoss.metrics import Decision


def _resp_choice(probs):
    """Build a fake response with given probabilities for one choice field."""
    return {"answers": {"q1": {"type": "choice", "choice": max(probs, key=probs.get), "probabilities": probs, "confidence": 0.9}}}


def test_needs_unknown_by_abstain_flag():
    item = {"abstain": True, "state": "x", "questions": {}, "targets": {}}
    assert needs_unknown(item) is True


def test_needs_unknown_by_label():
    item = {"state": "x", "questions": {}, "targets": {"q1": {"label": "unknown"}}}
    assert needs_unknown(item) is True


def test_needs_unknown_by_dist():
    item = {"state": "x", "questions": {}, "targets": {"q1": {"label": "a", "dist": {"a": 0.7, "unknown": 0.3}}}}
    assert needs_unknown(item) is True


def test_needs_unknown_false_normal():
    item = {"state": "x", "questions": {}, "targets": {"q1": {"label": "a", "dist": {"a": 0.9, "b": 0.1}}}}
    assert needs_unknown(item) is False


def test_f1_item_gold_unknown_scored_correct():
    """An F1-style item where gold is 'unknown': the model puts most mass on unknown, and it counts as correct."""
    item = {
        "id": "f1-001",
        "lang": "en",
        "state": "The customer asks about a plan but does not mention which one.",
        "questions": {
            "q1": {
                "type": "choice",
                "instructions": "Which plan?",
                "criteria": {"basic": "Free plan", "plus": "Paid monthly", "pro": "Paid yearly"},
            }
        },
        "targets": {
            "q1": {"label": "unknown", "dist": {"basic": 0.1, "plus": 0.1, "pro": 0.1, "unknown": 0.7}}
        },
    }
    response = _resp_choice({"basic": 0.05, "plus": 0.05, "pro": 0.05, "unknown": 0.85})
    decisions = to_decisions(item, response)
    assert len(decisions) == 1
    d = decisions[0]
    assert UNKNOWN in d.values
    assert d.gold == "unknown"
    assert d.probs[d.values.index(UNKNOWN)] > 0.8
    # gold_dist sums to 1 including unknown
    assert d.gold_dist is not None
    assert abs(sum(d.gold_dist) - 1.0) < 0.01
    # argmax of probs is unknown = gold
    assert d.values[d.probs.index(max(d.probs))] == "unknown"


def test_normal_item_unchanged():
    """A normal item: no abstain in request, no unknown in values."""
    item = {
        "id": "normal-001",
        "lang": "en",
        "state": "Refund request within 30 days.",
        "questions": {
            "q1": {
                "type": "choice",
                "instructions": "Which team?",
                "criteria": {"billing": "Invoices", "technical": "Bugs"},
            }
        },
        "targets": {"q1": {"label": "billing", "dist": {"billing": 0.9, "technical": 0.1}}},
    }
    response = _resp_choice({"billing": 0.9, "technical": 0.1})
    decisions = to_decisions(item, response)
    d = decisions[0]
    assert UNKNOWN not in d.values
    assert d.gold == "billing"


def test_run_sets_abstain_when_needed():
    """run() adds abstain=True to the request when the item needs unknown."""
    captured = []

    def fake_predict(request):
        captured.append(request)
        return _resp_choice({"basic": 0.05, "plus": 0.05, "pro": 0.05, "unknown": 0.85})

    item = {
        "id": "f1-002",
        "lang": "en",
        "state": "No plan mentioned.",
        "questions": {"q1": {"type": "choice", "instructions": "Which plan?", "criteria": {"basic": "Free", "plus": "Paid", "pro": "Yearly"}}},
        "targets": {"q1": {"label": "unknown", "dist": {"basic": 0.1, "plus": 0.1, "pro": 0.1, "unknown": 0.7}}},
    }
    run([item], fake_predict)
    assert captured[0].get("abstain") is True


def test_run_does_not_set_abstain_for_normal():
    """run() does not add abstain for normal items."""
    captured = []

    def fake_predict(request):
        captured.append(request)
        return _resp_choice({"billing": 0.9, "technical": 0.1})

    item = {
        "id": "normal-002",
        "lang": "en",
        "state": "Refund within 30 days.",
        "questions": {"q1": {"type": "choice", "instructions": "Which team?", "criteria": {"billing": "Invoices", "technical": "Bugs"}}},
        "targets": {"q1": {"label": "billing", "dist": {"billing": 0.9, "technical": 0.1}}},
    }
    run([item], fake_predict)
    assert "abstain" not in captured[0]


def test_run_extra_abstain_not_overridden():
    """When extra sets abstain explicitly, run() does not override it."""
    captured = []

    def fake_predict(request):
        captured.append(request)
        return _resp_choice({"billing": 0.9, "technical": 0.1})

    item = {
        "id": "normal-003",
        "lang": "en",
        "state": "Refund.",
        "questions": {"q1": {"type": "choice", "instructions": "Which team?", "criteria": {"billing": "Invoices", "technical": "Bugs"}}},
        "targets": {"q1": {"label": "billing", "dist": {"billing": 0.9, "technical": 0.1}}},
    }
    run([item], fake_predict, extra={"abstain": False})
    assert captured[0].get("abstain") is False
