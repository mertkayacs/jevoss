# Measured problems

Five robustness probes run against three open-weight decision models on 100 typed-decisions items. Jev 1.13 values are from an independent public audit on a different item set, so they are context, not a head-to-head comparison. JevAlt values are pending.

Lower is better for every probe. For determinism, 0 changes is best.

## Results

| Probe | Metric | Intern-Decision-4B | Kev-4B | Laya-multilingual | Jev 1.13 | JevAlt |
|---|---|---|---|---|---|---|
| Option order | Top answer flips | 8.8% | 13.5% | 23.8% | 0.0%[^1] | pending |
| Prompt injection | Attack success | 41.5% | 36.0% | 42.0% | - | pending |
| Distractors | Accuracy lost | 15.0 pts | 5.4 pts | 10.4 pts | - | pending |
| Noul vs Choice | Mean gap in P(yes) | 0.032 | 0.033 | 0.106 | 0.125[^1] | pending |
| Determinism | Largest change | 0.000 | 0.000 | 0.000 | -[^2] | pending |

[^1]: From a public audit on 400 KoBBQ items with two-option questions. Different item set, so not directly comparable. Source: [jev-calibration-audit](https://github.com/jujumilk3/jev-calibration-audit/blob/main/FINDINGS.md).

[^2]: The audit sent 50 byte-identical requests and got 15 distinct answer sets, so Jev 1.13 is not deterministic on that setup. The metric here (largest probability change) was not reported.

Bold marks the best value among the three measured models (Intern-Decision-4B, Kev-4B, Laya-multilingual). Published audit values are excluded from the best-value comparison.

## How to reproduce

Install JevOss and start a model server:

```bash
pip install "jevoss[suites] @ git+https://github.com/mertkayacs/jevoss"
jevalt serve
```

Run each probe against the server (default endpoint `http://127.0.0.1:8000`):

```bash
jevoss probe typed-decisions --probes permutation
jevoss probe typed-decisions --probes injection
jevoss probe typed-decisions --probes distractors
jevoss probe typed-decisions --probes noul
jevoss probe typed-decisions --probes determinism
```

Or run all five at once:

```bash
jevoss probe typed-decisions --limit 100
```

Each probe prints a JSON object with the metrics. The `--limit` flag caps the number of items. The `--probes` flag selects which probes to run; the default is all five.

To point at a different server, pass `--endpoint`:

```bash
jevoss --endpoint https://api.typesafe.ai --api-key "$TYPESAFE_API_KEY" probe typed-decisions
```

## Audit citation

Jev 1.13 values are from [jev-calibration-audit](https://github.com/jujumilk3/jev-calibration-audit/blob/main/FINDINGS.md), an independent audit run on 2026-09-18 against the hosted Jev API. The audit used 400 KoBBQ items with two-option questions, a different setup from the typed-decisions suite used for the other three models. The numbers are included for context, not as a head-to-head comparison.
