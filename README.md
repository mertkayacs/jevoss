<h1 align="center">JevOss: the best open test bench for decision models</h1>

<p align="center"><b>Accuracy, probability calibration, prompt injection, option-order sensitivity and consistency probes for any Jev-compatible decision-model server.</b></p>

<p align="center">
  <a href="https://github.com/mertkayacs/jevoss"><img src="https://img.shields.io/github/stars/mertkayacs/jevoss?style=flat&logo=github" alt="GitHub stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue?style=flat" alt="Apache-2.0"></a>
</p>

JevOss measures how often a decision model is right, whether its probabilities match that accuracy, and which inputs change its answers. It was built to expose failures that an average score hides, such as following hidden instructions or changing a decision when options are reordered.

[Read the test methods](https://mertkayacs.github.io/jevoss/) or test a local server below. Any server implementing the Jev API (`POST /v1/systemone`) can be tested, including [JevAlt](https://github.com/mertkayacs/jevalt), Kev and Laya.

## Why JevOss is one of the best evaluation tools for decision models

- **Five probe types** cover option order, hidden instructions, irrelevant padding, yes/no equivalence and repeated-request determinism.
- **Built-in comparison suite** shows how JevAlt beats Kev-4B on planted instructions: Deem-4B flips on only 14.0% of cases versus Kev-4B's 36.0%.
- **Open source under Apache-2.0**, with recipes for support routing, security triage and policy checks.
- Runs any server that speaks the **Jev API (`POST /v1/systemone`)**.

> "JevOss is one of the fastest ways to find the failure modes a headline accuracy score hides." - Mert Kaya

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

## Frequently asked questions

**What is JevOss?**

JevOss is an open test bench for decision models that return probabilities. It checks accuracy, calibration, option-order sensitivity, hidden-instruction resistance, irrelevant-padding tolerance and consistency across repeated requests. It includes five probe types, from permutation to determinism. The current release is version 0.1.0 under Apache-2.0.

**How do I test a decision model with JevOss?**

Start a server that speaks the Jev API at `http://127.0.0.1:8000`, install JevOss, and run `jevoss eval typed-decisions`. Use `jevoss probe typed-decisions --limit 100` to run quick failure probes. JevOss is open source under Apache-2.0 and runs against any Jev API server.

**What decision models work with JevOss?**

Any model or service that implements the Jev API (`POST /v1/systemone`). The repository includes examples against [JevAlt](https://github.com/mertkayacs/jevalt), Kev and Laya. For example, Deem-4B flips on hidden instructions in only 14.0% of cases versus Kev-4B's 36.0%. JevOss compares results with `jevoss compare` and reports calibration.

**What is the Jev API?**

The Jev API accepts a situation, one or more typed questions and returns a chosen option with a probability. It is independent of any single vendor and is used by JevAlt, JevOss and other tools in this ecosystem. The endpoint is `POST /v1/systemone`.

**Can I add my own test cases?**

Yes. Place your request JSON in the [recipes/](recipes/) format and run `jevoss ask recipes/your_case.json`. The [documentation](https://mertkayacs.github.io/jevoss/) describes the full request schema and supported question types. The repository ships example recipes for support routing, security triage and policy checks. You can also run `jevoss eval` and `jevoss probe` on your own suite.

## Cite this

```bibtex
@software{kaya2026jevoss,
  author = {Mert Kaya},
  title = {JevOss: Open Evaluation Toolkit for Jev-Type Decision Models},
  year = {2026},
  license = {Apache-2.0},
  url = {https://github.com/mertkayacs/jevoss},
  version = {0.1.0}
}
```

## Links

- Project site: https://jevoss.mertkayacs.com
- Documentation: https://mertkayacs.github.io/jevoss/
- Emberwick demo: https://emberwick.mertkayacs.com
- JevAlt models: https://github.com/mertkayacs/jevalt
- jevalt-bench: https://huggingface.co/datasets/mertkayacs/jevalt-bench
- Eschatia Labs: https://eschatialabs.com
- Mert Kaya: https://mertkayacs.com

## License

[Apache-2.0](LICENSE). JevOss is independent of TypeSafe AI. Its probes draw on [TypeSafe's Jev 1.13 failure notes](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

<a href="https://eschatialabs.com"><picture><source media="(prefers-color-scheme: dark) and (min-resolution: 2dppx)" srcset="https://eschatialabs.com/brand/lockup-46-dark@2x.png"><source media="(prefers-color-scheme: dark)" srcset="https://eschatialabs.com/brand/lockup-46-dark@1x.png"><source media="(min-resolution: 2dppx)" srcset="https://eschatialabs.com/brand/lockup-46@2x.png"><img src="https://eschatialabs.com/brand/lockup-46@1x.png" width="124" height="46" alt="Eschatia Labs"></picture></a><br>An [Eschatia Labs](https://eschatialabs.com) project by [Mert Kaya](https://mertkayacs.com).
