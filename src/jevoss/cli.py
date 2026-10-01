"""jevoss eval | probe | calibrate, against any /v1/systemone endpoint."""

from __future__ import annotations

import argparse
import json
import sys

from . import calibrate, probes, report, suites
from .runner import http_predictor, run


def _items(args):
    kwargs = {"limit": args.limit} if args.limit and not args.suite.endswith(".jsonl") and args.suite.startswith(("massive", "gmmlu")) else {}
    items = suites.load(args.suite, **kwargs)
    return items[: args.limit] if args.limit else items


def render(response: dict) -> str:
    """Terminal view: one block per question, options sorted by probability."""
    lines = []
    for name, answer in response["answers"].items():
        if answer["type"] == "noul":
            probs = {"yes": answer["noul"], "no": 1 - answer["noul"]}
            head = f"yes {answer['noul']:.2f}"
        else:
            probs = answer["probabilities"]
            head = f"{answer.get('choice') or 'score ' + format(answer['score'], '.2f')}  confidence {answer['confidence']:.2f}"
        lines.append(f"{name}: {head}")
        for key, p in sorted(probs.items(), key=lambda kv: -kv[1]):
            lines.append(f"  {key[:18]:18s} {'#' * round(p * 30):30s} {p:.2f}")
        if answer.get("set"):
            lines.append(f"  set: {', '.join(answer['set'])}")
        if answer.get("reasoning"):
            lines.append(f"  why: {answer['reasoning']}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="jevoss", description="Test and improve Jev-type decision models.")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000", help="base URL of a /v1/systemone server")
    parser.add_argument("--model", default="jev-latest")
    parser.add_argument("--api-key", default="local")
    parser.add_argument("--workers", type=int, default=1)
    sub = parser.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("eval", help="score a suite")
    e.add_argument("suite", help=f"one of {sorted(suites.registry())} or a canonical .jsonl file")
    e.add_argument("--limit", type=int, default=0)
    e.add_argument("--reasoning", choices=["off", "on", "auto"], default="off")
    e.add_argument("--out", default="")

    pr = sub.add_parser("probe", help="robustness probes on a suite")
    pr.add_argument("suite")
    pr.add_argument("--limit", type=int, default=100)
    pr.add_argument("--probes", nargs="+", default=["permutation", "injection", "distractors", "noul", "determinism"])

    a = sub.add_parser("ask", help="send one request (JSON file or string) and print the answers")
    a.add_argument("request")
    a.add_argument("--reasoning", choices=["off", "on", "auto"], default=None)
    a.add_argument("--json", action="store_true", help="print the raw response")

    cmp = sub.add_parser("compare", help="paired difference of two decision files (b minus a) with 95%% intervals")
    cmp.add_argument("a")
    cmp.add_argument("b")

    c = sub.add_parser("calibrate", help="fit temperatures on a held-out suite")
    c.add_argument("suite")
    c.add_argument("--limit", type=int, default=0)
    c.add_argument("--out", default="calibration.json")

    args = parser.parse_args(argv)
    if args.cmd == "compare":
        from .compare import compare, load

        print(json.dumps(compare(load(args.a), load(args.b)), indent=2))
        return
    predict = http_predictor(args.endpoint, model=args.model, api_key=args.api_key)
    if args.cmd == "ask":
        import os

        request = json.load(open(args.request)) if os.path.exists(args.request) else json.loads(args.request)
        if args.reasoning:
            request["reasoning"] = args.reasoning
        response = predict(request)
        print(json.dumps(response, ensure_ascii=False, indent=2) if args.json else render(response))
        return
    items = _items(args)

    if args.cmd == "eval":
        extra = {"reasoning": args.reasoning} if args.reasoning != "off" else None
        decisions, raw = run(items, predict, extra=extra, workers=args.workers, on_error="record")
        res = report.result(decisions, suite=args.suite, model=args.model, extra={"errors": sum(1 for r in raw if r["error"]), "reasoning": args.reasoning})
        print(report.table([res]))
        if args.out:
            report.dump(args.out, res)
    elif args.cmd == "probe":
        fns = {
            "permutation": lambda: probes.probe_permutations(items, predict, workers=args.workers),
            "injection": lambda: probes.probe_injections(items, predict, workers=args.workers),
            "distractors": lambda: probes.probe_distractors(items, predict, workers=args.workers),
            "noul": lambda: probes.probe_noul_twins(items, predict),
            "determinism": lambda: probes.probe_determinism(items[:20], predict),
        }
        for name in args.probes:
            print(json.dumps(fns[name](), ensure_ascii=False))
    else:
        decisions, _ = run(items, predict, workers=args.workers)
        cal = calibrate.fit(decisions)
        cal["conformal"] = calibrate.fit_conformal(calibrate.apply(decisions, cal))
        report.dump(args.out, cal)
        json.dump(cal, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
