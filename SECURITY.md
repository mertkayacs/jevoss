# Security policy

## Reporting a vulnerability

Please report security problems privately through GitHub's private vulnerability reporting. On the repository page, open the **Security and quality** tab and choose **Report a vulnerability**, or go straight to the [advisory form](https://github.com/mertkayacs/jevoss/security/advisories/new). Please do not open a public issue for a security problem.

Include the affected file or command, the steps to reproduce it and the impact you expect. I read every report and reply in the private advisory.

## Scope

This policy covers the code in this repository: the `jevoss` package and its command line, the probes, the suites and the recipes. JevOss sends each request to the server you name with `--endpoint` and sends the `--api-key` value to that server as a bearer token.

A probe result that shows a model following a planted instruction or changing its answer is a finding about that model and is out of scope here. Please open an ordinary issue for a problem with a probe, a suite or a recipe.

## Supported versions

Fixes go to the `main` branch. The repository has no release branches.
