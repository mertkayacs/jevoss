# JevOss

JevOss tests decision models that speak TypeSafe's `/v1/systemone` API. Point it at an endpoint and it tells you how often the model is right, how honest its probabilities are, and which of Jev's known weak spots it shares.

It works with anything that answers the Jev contract: Jev itself, JevAlt, Kev, Laya, Intern-Decision, or your own server.

```bash
pip install "jevoss[suites] @ git+https://github.com/mertkayacs/jevoss"
```

```bash
jevoss --endpoint http://127.0.0.1:8000 eval typed-decisions
jevoss --endpoint http://127.0.0.1:8000 probe typed-decisions --limit 100
```

## What you get

| Command | Answers the question |
|---|---|
| `jevoss eval <suite>` | How accurate is it, and are its probabilities calibrated? |
| `jevoss probe <suite>` | Does the answer move when it should not (option order, injected text, noise)? |
| `jevoss calibrate <suite>` | Which temperature fixes its confidence on my data, and what threshold gives 90% coverage sets? |
| `jevoss ask recipes/support_routing.json` | What does it decide for this one request? |

## Why it exists

A decision model returns a probability for every option. Software then acts on those numbers: route a ticket, block a post, stop an agent. If the probabilities are off, the automation is off. TypeSafe's own documentation lists places where Jev 1.13 struggles (counting, dates, negated questions, hostile text inside the state, long irrelevant context). JevOss turns each of those into a measurement you can run against any model in a few minutes.

If JevOss helps you, a star on [GitHub](https://github.com/mertkayacs/jevoss) helps others find it.
