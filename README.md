# JevOss

![Emberwick: every villager asks a JevAlt model what to do next](https://raw.githubusercontent.com/mertkayacs/jevalt/media/emberwick-en.gif)

*Emberwick, a village game where every villager asks a JevAlt model what to do next. Also in [Türkçe](https://huggingface.co/datasets/mertkayacs/emberwick-videos/resolve/main/gifs/emberwick-tr.gif) and [Deutsch](https://huggingface.co/datasets/mertkayacs/emberwick-videos/resolve/main/gifs/emberwick-de.gif).*

![JevOss: test any decision model that speaks the Jev API](https://raw.githubusercontent.com/mertkayacs/jevalt/media/jevoss-card.png)

Open toolkit to test and improve Jev-type decision models. Probes, calibration, conformal sets, and recipes for any `/v1/systemone` endpoint.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-mertkayacs-yellow)](https://huggingface.co/mertkayacs)
[![Docs](https://img.shields.io/badge/docs-mertkayacs.github.io/jevoss-green)](https://mertkayacs.github.io/jevoss/)

If this is useful to you, a star on GitHub helps other people find it.

## What it is

JevOss tests decision models that speak TypeSafe's `/v1/systemone` API. Point it at an endpoint and it tells you how often the model is right, how honest its probabilities are, and which of Jev's known weak spots it shares. It works with anything that answers the Jev contract: Jev itself, JevAlt, Kev, Laya, Intern-Decision, or your own server.

## What it found

![Hidden instructions, option order, long policies and negated questions: JevAlt against Intern-Decision-4B, Kev-4B and Laya](docs/assets/charts/fixes.png)

Same probes and held-out rows for every model, each as shipped. Kev-4B and Laya lose less accuracy under long padding. All results and the Jev 1.13 audit: [measured problems](docs/problems.md).

## Quickstart

```bash
pip install "jevoss[suites] @ git+https://github.com/mertkayacs/jevoss"
jevoss eval typed-decisions
```

By default JevOss talks to `http://127.0.0.1:8000`, where `jevalt serve` listens. Pass `--endpoint` for any other server.

Run probes:

```bash
jevoss probe typed-decisions --limit 100
```

Fit calibration:

```bash
jevoss calibrate typed-decisions --out calibration.json
```

Compare two decision files:

```bash
jevoss compare baseline.jsonl new.jsonl
```

Send one request:

```bash
jevoss ask recipes/support_routing.json
```

To measure Jev itself:

```bash
jevoss --endpoint https://api.typesafe.ai --api-key "$TYPESAFE_API_KEY" eval typed-decisions
```

## Suites

Built-in suites (`jevoss eval <suite>`):

`typed-decisions`, `jevbench-easy`, `jevbench-hard`, `jevbench-original`, `agnews`, `germeval2017`, `gmmlu-de`, `gmmlu-en`, `gmmlu-tr`, `gnad10`, `massive-de`, `massive-en`, `massive-tr`, `toolace`, `turkish-mmlu`, `wildjailbreak`

## Probes

`jevoss probe <suite> --probes permutation injection distractors noul determinism`

| Probe | What it changes | Metric | Good direction |
|---|---|---|---|
| `permutation` | Shuffles Choice options | Top answer flips | lower |
| `injection` | Appends a wrong-order instruction | Attack success | lower |
| `distractors` | Pads state with ~600 words of noise | Accuracy lost | lower |
| `noul` | Asks each Noul again as a Choice | Mean gap in P(yes) | lower |
| `determinism` | Sends each request 5 times | Largest change | lower |

## Reproduce

Install, start a model server, run the probes:

```bash
pip install "jevoss[suites] @ git+https://github.com/mertkayacs/jevoss"
jevalt serve
jevoss probe typed-decisions
```

Each probe prints a JSON object with the metrics. See the [docs](https://mertkayacs.github.io/jevoss/) for probe methodology, calibration, and recipes.

## License

Apache-2.0.

## Citation

```bibtex
@software{kaya2026jevoss,
  author = {Mert Kaya},
  title = {JevOss: Open Evaluation Toolkit for Jev-Type Decision Models},
  year = {2026},
  license = {Apache-2.0},
  url = {https://github.com/mertkayacs/jevoss}
}
```

## Acknowledgements

JevOss probes are based on the failure modes documented in [TypeSafe's Jev 1.13 jaggedness notes](https://docs.typesafe.ai/model-jaggedness/jev-1.13). JevOss is an independent project with no affiliation to TypeSafe AI. Jev is a TypeSafe AI model.
