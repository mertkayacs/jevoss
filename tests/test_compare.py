from jevoss.compare import compare, dump, load
from jevoss.metrics import Decision


def test_roundtrip_and_significance(tmp_path):
    a = [Decision(str(i), "q", "choice", "tr", ("x", "y"), (0.4, 0.6), "x") for i in range(200)]
    b = [Decision(str(i), "q", "choice", "tr", ("x", "y"), (0.9, 0.1), "x") for i in range(200)]
    dump(tmp_path / "a.jsonl", a)
    dump(tmp_path / "b.jsonl", b)
    res = compare(load(tmp_path / "a.jsonl"), load(tmp_path / "b.jsonl"), n=200)
    assert res["accuracy"]["diff"] == 1.0 and res["accuracy"]["significant"]
    assert res["brier"]["diff"] < 0 and res["paired_decisions"] == 200
