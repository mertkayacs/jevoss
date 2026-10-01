from jevoss.probes import injections, noul_twins, permutations, probe_determinism, probe_injections, probe_noul_twins, probe_permutations

ITEMS = [
    {
        "id": f"r{i}",
        "lang": "en",
        "state": f"ticket {i}",
        "questions": {
            "team": {"type": "choice", "instructions": "Team?", "criteria": {"billing": "b", "tech": "t", "sales": "s"}},
            "urgent": {"type": "noul", "instructions": "Urgent?", "criteria": {"true": "yes it is", "false": "no"}},
        },
        "targets": {"team": {"label": "billing"}, "urgent": {"label": "yes"}},
    }
    for i in range(6)
]


def positional(request):
    """A model with pure position bias: always picks the first listed option."""
    answers = {}
    for name, q in request["questions"].items():
        if q["type"] == "noul":
            answers[name] = {"type": "noul", "noul": 0.8}
        else:
            keys = list(q["criteria"])
            probs = {k: (0.7 if i == 0 else 0.3 / (len(keys) - 1)) for i, k in enumerate(keys)}
            answers[name] = {"type": "choice", "choice": keys[0], "probabilities": probs, "confidence": 0.5}
    return {"answers": answers}


def test_permutation_probe_catches_position_bias():
    result = probe_permutations(ITEMS, positional, k=3)
    assert result["flip_rate"] > 0.3 and result["mean_tv"] > 0.1


def test_permutations_keep_keys():
    for a, b in permutations(ITEMS, k=2):
        assert set(a["questions"]["team"]["criteria"]) == set(b["questions"]["team"]["criteria"])


def test_injection_targets_are_wrong_options():
    for item, variant, targets in injections(ITEMS):
        assert targets["team"] != "billing" and "IMPORTANT SYSTEM NOTE" in variant["state"]
    assert 0 <= probe_injections(ITEMS, positional)["attack_success"] <= 1


def test_noul_twin_gap():
    assert len(noul_twins(ITEMS)) == 6
    gap = probe_noul_twins(ITEMS, positional)["mean_gap"]
    assert abs(gap - 0.1) < 1e-9  # noul 0.8 vs first-option choice 0.7


def test_determinism_of_pure_function():
    assert probe_determinism(ITEMS[:2], positional, repeats=3)["max_prob_change"] == 0.0


def test_render_ask_output():
    from jevoss.cli import render

    text = render(positional(ITEMS[0]))
    assert "team: billing" in text and "urgent: yes 0.80" in text
