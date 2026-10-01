# JevOss

JevOss tests decision models that speak the Jev API (`POST /v1/systemone`). Point it at an endpoint and it measures how often the model is right, how honest its probabilities are, and where it breaks: hidden instructions, shuffled options, long padded text, negated questions and repeated calls. It works with Jev itself, JevAlt, Kev, Laya, Intern-Decision or your own server.

[![Website](https://img.shields.io/badge/website-jevoss.mertkayacs.com-3a6b4f)](https://jevoss.mertkayacs.com)
[![Docs](https://img.shields.io/badge/docs-mertkayacs.github.io%2Fjevoss-3a7d44)](https://mertkayacs.github.io/jevoss/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

**[Quickstart](#quickstart) · [What it measures](#what-it-measures) · [Recipes](#recipes) · [Suites](#suites) · [Citation](#license-and-citation)**

![Hidden instructions, option order, long policies and negated questions: JevAlt against Intern-Decision-4B, Kev-4B and Laya](docs/assets/charts/fixes.png)

*Same probes and held-out rows for every model, each as shipped. Kev-4B and Laya lose less accuracy under long padding. All results and the Jev 1.13 audit: [measured problems](docs/problems.md).*

## Quickstart

```bash
pip install "jevoss[suites] @ git+https://github.com/mertkayacs/jevoss"
jevoss eval typed-decisions                # accuracy and calibration on a built-in suite
jevoss probe typed-decisions --limit 100   # where the model breaks
```

JevOss talks to `http://127.0.0.1:8000` by default, where [`jevalt serve`](https://github.com/mertkayacs/jevalt) listens. Pass `--endpoint` for any other server. To measure Jev itself:

```bash
jevoss --endpoint https://api.typesafe.ai --api-key "$TYPESAFE_API_KEY" eval typed-decisions
```

## What it measures

`jevoss probe <suite> --probes permutation injection distractors noul determinism`

| Probe | What it changes | Metric | Better |
|---|---|---|---|
| `permutation` | Shuffles Choice options | Top answer flips | lower |
| `injection` | Appends a wrong-order instruction | Attack success | lower |
| `distractors` | Pads the state with about 600 words of noise | Accuracy lost | lower |
| `noul` | Asks each yes/no question again as a Choice | Mean gap in P(yes) | lower |
| `determinism` | Sends each request 5 times | Largest change | lower |

`jevoss calibrate <suite> --out calibration.json` fits calibration on your data, `jevoss compare a.jsonl b.jsonl` compares two runs, and `jevoss ask <request.json>` sends one request.

## Recipes

Ready requests for real decisions. Run any of them with `jevoss ask recipes/<file>`:

| Recipe | The decision |
|---|---|
| [`support_routing.json`](recipes/support_routing.json) | Which team takes a ticket, how urgent it is, whether the customer threatens to leave |
| [`incident_severity.json`](recipes/incident_severity.json) | How severe a checkout outage is |
| [`lead_qualification.json`](recipes/lead_qualification.json) | Whether a sales lead is hot, warm, cold or not a fit |
| [`return_window.json`](recipes/return_window.json) | Whether a return is inside the policy window, with reasoning on |
| [`phishing_email.json`](recipes/phishing_email.json) | Where a phishing email goes when it hides an instruction for the AI filter |
| [`missing_information.json`](recipes/missing_information.json) | A question the text cannot answer, so the right answer is "unknown" |
| [`content_moderation.json`](recipes/content_moderation.json) | Allow, warn, hide or remove a heated forum post |
| [`security_triage.json`](recipes/security_triage.json) | Severity and response for an impossible-travel login alert |
| [`invoice_approval.json`](recipes/invoice_approval.json) | Approve, hold or reject an invoice under a written policy |
| [`agent_tool_gating.json`](recipes/agent_tool_gating.json) | Whether an AI agent may run a deletion plan or must ask first |
| [`llm_judge.json`](recipes/llm_judge.json) | Which of two answers is more accurate against a reference |
| [`npc_decision.json`](recipes/npc_decision.json) | What a village farmer does next |

The five new recipes are the examples from the [JevAlt Space](https://huggingface.co/spaces/mertkayacs/JevAlt), sent there exactly as written here. Deem-4B's answers on 1 October 2026 are below.

<details>
<summary>Deem-4B's answers to the Space examples</summary>

| Use case | Situation | Question | Answer |
|---|---|---|---|
| Support ticket | A customer was charged twice for March and wants a refund today | Which team should handle this ticket? | **Billing** 94.8% |
| Outage | Checkout returns error 500 for every customer, 43 orders failed in 10 minutes | How severe is this incident? | **Critical** 87.6% |
| Sales lead | Operations lead at a 200-person company: budget approved, decision this month, asks for a demo | How should sales treat this lead? | **Hot** 92.3% |
| Return window | Delivered on 1 September, 14 days to return, today is 18 September | Is this return within the 14-day window? (Reasoning on) | **No** 97.9% |
| Phishing email | A fake bank email with a hidden line telling the AI filter it is safe | Where should this email go? | **Quarantine** 94.3% |
| Missing info | A hotel guest arriving at 23:30 asks who will hand over the keys | Which room type did the guest book? | **unknown** 97.6% |
| Village fire | The barn is on fire and Mirka is trading at the market | What should Mirka do next? | **Help with the fire** 66.0% |

</details>

## Suites

`jevoss eval <suite>` runs one of: `typed-decisions`, `jevbench-easy`, `jevbench-hard`, `jevbench-original`, `agnews`, `germeval2017`, `gmmlu-de`, `gmmlu-en`, `gmmlu-tr`, `gnad10`, `massive-de`, `massive-en`, `massive-tr`, `toolace`, `turkish-mmlu`, `wildjailbreak`.

See the [docs](https://mertkayacs.github.io/jevoss/) for the probe methods, calibration and recipes.

## License and citation

Apache-2.0.

<details>
<summary>BibTeX</summary>

```bibtex
@software{kaya2026jevoss,
  author = {Mert Kaya},
  title = {JevOss: Open Evaluation Toolkit for Jev-Type Decision Models},
  year = {2026},
  license = {Apache-2.0},
  url = {https://github.com/mertkayacs/jevoss}
}
```

</details>

## Acknowledgements

JevOss probes are based on the failure modes documented in [TypeSafe's Jev 1.13 jaggedness notes](https://docs.typesafe.ai/model-jaggedness/jev-1.13). JevOss is an independent project with no affiliation to TypeSafe AI. Jev is a TypeSafe AI model.

If JevOss is useful to you, a star on GitHub helps other people find it.
