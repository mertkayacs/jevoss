# Measured problems

Small decision models share a set of weak spots. JevOss measures five of them with probes on 100 typed-decisions items, run through the same client against the start checkpoint (Intern-Decision-4B), Kev-4B, Laya and the three JevAlt models. Kev-4B (r10) and Laya (0.3.22, routed: `laya` for English) ran on their own servers with their shipped calibration. Jev 1.13 values come from an independent public audit on a different item set, so they are context, not a head-to-head comparison.

Lower is better for every probe. Bold marks the best measured value.

| Probe | Metric | Deem-4B | Karar-4B | Wähler-4B | Intern-Decision-4B | Kev-4B | Laya | Jev 1.13 |
|---|---|---|---|---|---|---|---|---|
| An instruction hidden in the state flips the answer | Attack success | **14.0%** | 19.0% | 17.5% | 41.5% | 36.0% | 42.0% | - |
| Reordering the options flips the answer | Top answer flips | **6.5%** | 7.2% | 9.5% | 8.8% | 13.5% | 23.8% | 0 of 400 flips[^1] |
| Accuracy lost to 600 words of padding | Accuracy lost | 17.4 pts | 17.4 pts | 12.2 pts | 15.0 pts | **5.4 pts** | 10.4 pts | - |
| Yes/no and two-option choice disagree (mean gap) | Mean gap in P(yes) | 0.032 | 0.050 | **0.029** | 0.032 | 0.033 | 0.106 | 0.125[^1] |
| Five identical runs change an answer | Items changed | 0 of 20 | 0 of 20 | 0 of 20 | 0 of 20 | 0 of 20 | 0 of 20 | 15 answer sets from 50 calls[^2] |

[^1]: From a public audit on 400 KoBBQ items with two-option questions. Different item set, so not directly comparable. Source: [jev-calibration-audit](https://github.com/jujumilk3/jev-calibration-audit/blob/main/FINDINGS.md).

[^2]: The audit sent 50 byte-identical requests and got 15 distinct answer sets.

## The same weaknesses on held-out rows

The JevAlt test splits hold rows built to test one weakness each. Accuracy, higher is better; the JevAlt column uses each language's own model, so these rows favour JevAlt (same pipeline as its training rows). Kev-4B and Laya received the rows in the shapes the TypeSafe docs use.

| Weakness | JevAlt | Intern-Decision-4B | Kev-4B | Laya | Clear win |
|---|---|---|---|---|---|
| Instruction hidden in the state (203) | **90.1%** | 80.8% | 81.3% | 41.9% | yes |
| Long irrelevant text around the state (285) | **95.4%** | 91.2% | 87.4% | 41.4% | yes |
| Criteria that invert the question's wording (85) | **60.0%** | 56.5% | 52.9% | 41.2% | |
| Long policies with exceptions (150) | **80.0%** | 55.3% | 59.3% | 38.0% | yes |
| Dates and deadlines (80) | **71.2%** | 61.3% | 67.5% | 45.0% | |
| Numbers and sums (44) | **68.2%** | **68.2%** | **68.2%** | 20.5% | |
| Negated questions (30) | **96.7%** | 80.0% | 76.7% | 50.0% | yes |
| Yes/no asked as a two-option choice (47) | **97.9%** | **97.9%** | **97.9%** | 68.1% | |

"Clear win" means JevAlt beats all three others with a paired bootstrap interval above zero. Every decision is in [jevalt-bench results/comparison](https://huggingface.co/datasets/mertkayacs/jevalt-bench/tree/main/results/comparison).

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

Jev 1.13 values are from [jev-calibration-audit](https://github.com/jujumilk3/jev-calibration-audit/blob/main/FINDINGS.md), an independent audit run on 2026-09-18 against the hosted Jev API. The audit used 400 KoBBQ items with two-option questions, a different setup from the typed-decisions suite used for the measured models. The numbers are included for context, not as a head-to-head comparison.
