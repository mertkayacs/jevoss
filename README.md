# JevOss: test decision models and their confidence

JevOss measures how often a decision model is right, whether its probabilities match that accuracy, and which inputs change its answers. It was built to expose failures that an average score hides, such as following hidden instructions or changing a decision when options are reordered.

[Read the test methods](https://mertkayacs.github.io/jevoss/) or test a local server below. Any server implementing the Jev API (`POST /v1/systemone`) can be tested, including [JevAlt](https://github.com/mertkayacs/jevalt), Kev and Laya.

## Quick start

Requires Python 3.11 or newer and a running decision-model server. To start JevAlt's local server, follow its [installation instructions](https://github.com/mertkayacs/jevalt). Keep that terminal running.

In a second terminal:

```sh
pip install "jevoss[suites] @ git+https://github.com/mertkayacs/jevoss" && jevoss eval typed-decisions && jevoss probe typed-decisions --limit 100
```

The default server is `http://127.0.0.1:8000`. To test another server, put its base URL before the command:

```sh
jevoss --endpoint http://127.0.0.1:8000 eval typed-decisions
```

## What it tests

| Probe | Test |
| --- | --- |
| `permutation` | Does changing option order change the answer? |
| `injection` | Does a hidden instruction override the task? |
| `distractors` | Does irrelevant padding reduce accuracy? |
| `noul` | Do yes/no and equivalent two-option questions agree? |
| `determinism` | Do repeated requests return the same probabilities? |

`jevoss eval` reports accuracy and calibration. `jevoss calibrate` fits confidence on your data, and `jevoss compare` compares two recorded runs. See the [documentation](https://mertkayacs.github.io/jevoss/) for supported suites and output formats.

## Example decisions

The [recipe directory](recipes/) contains requests for ticket routing, policy checks, security triage and tool permissions. For example, after cloning this repository, send the support-routing request to your running server:

```sh
jevoss ask recipes/support_routing.json
```

[Emberwick](https://emberwick.mertkayacs.com) uses the same request format to choose villagers' next actions. Its example is [npc_decision.json](recipes/npc_decision.json).

<a href="https://emberwick.mertkayacs.com"><img src="https://raw.githubusercontent.com/mertkayacs/jevoss/main/docs/assets/emberwick-barn-fire-en.webp" width="560" alt="Emberwick at dusk: a barn burns while villagers gather at the well, and a label shows Vilma's chosen action, fight the fire, at 86% from Deem-4B"></a>

## Results and limits

The [measured-problems report](docs/problems.md) compares the models on the same probes and held-out rows, each as shipped. Kev-4B and Laya lose less accuracy than JevAlt under long padding. Hosted Jev 1.13 results use a different item set and are shown for context only.

<img src="https://raw.githubusercontent.com/mertkayacs/jevoss/main/docs/assets/charts/fixes.png" width="720" alt="Probe results for JevAlt, Kev-4B and Laya: answers flipped by hidden instructions, and accuracy with long irrelevant text, long policies and negated questions">

All recorded decisions are in [jevalt-bench](https://huggingface.co/datasets/mertkayacs/jevalt-bench/tree/main/results/comparison). Test on your own inputs before treating a suite score as evidence for your application.

## License and citation

[Apache-2.0](LICENSE). JevOss is independent of TypeSafe AI. Its probes draw on [TypeSafe's Jev 1.13 failure notes](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

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

[Project site](https://jevoss.mertkayacs.com).

<a href="https://eschatialabs.com"><picture><source media="(min-resolution: 2dppx)" srcset="https://eschatialabs.com/brand/lockup-46@2x.png"><img src="https://eschatialabs.com/brand/lockup-46@1x.png" width="124" height="46" alt="Eschatia Labs"></picture></a><br>An [Eschatia Labs](https://eschatialabs.com) project by [Mert Kaya](https://mertkayacs.com).
