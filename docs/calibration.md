# Calibration

A model is calibrated when its 0.8 answers are right about 80% of the time. Most models are close but not exact, and the gap depends on the domain and the language. JevOss fits two fixes on held-out data you trust.

```bash
jevoss --endpoint http://127.0.0.1:8000 calibrate my_labelled.jsonl --out calibration.json
```

## Temperature per question type and language

One temperature `T` rescales every distribution: `softmax(log p / T)`. `T > 1` softens an overconfident model, `T < 1` sharpens a timid one. The top option never changes.

JevOss fits `T` by minimising negative log-likelihood, separately for each question type and language when a group has at least 150 decisions, and falls back to the type, then to one global value. The output uses the same keys the JevAlt engine reads (`choice:tr`, `score`, `default`).

## Conformal sets

Split conformal prediction turns probabilities into an option set with a coverage guarantee: with `coverage = 0.9`, the set contains the correct answer for at least 90% of new decisions drawn from the same distribution as the calibration data. Clear cases get a single option, unclear cases get two or three.

JevOss stores one threshold per group and coverage level. A JevAlt server returns the set when the request asks for it:

```json
{"state": "...", "questions": {"team": {...}}, "coverage": 0.9}
```

```json
{"team": {"choice": "billing", "probabilities": {"billing": 0.71, "technical": 0.24, "sales": 0.05}, "set": ["billing", "technical"]}}
```

The guarantee holds on average over new data from the same distribution. Recalibrate when your traffic changes.

## Reading the numbers

| Metric | Good direction | What it tells you |
|---|---|---|
| accuracy | higher | top option matches the label |
| Brier | lower | squared error of the whole distribution |
| NLL | lower | how surprised the model is by the truth |
| ECE | lower | gap between stated confidence and hit rate (15 equal-mass bins) |
| KL to gold | lower | distance to a reference distribution, when the suite has one |
| AUROC | higher | whether confidence separates right from wrong answers |
| coverage@5% | higher | share of decisions you can automate while keeping errors under 5% |
