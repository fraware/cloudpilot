# Contributing to CloudPilot

Thank you for contributing. This document describes how to set up a development environment, run the same checks as CI, and submit changes.

## Contents

- [Reporting bugs](#reporting-bugs)
- [Feature requests](#feature-requests)
- [Development setup](#development-setup)
- [Daily workflow](#daily-workflow)
- [Code style and static analysis](#code-style-and-static-analysis)
- [Tests](#tests)
- [Environment variables for local runs](#environment-variables-for-local-runs)
- [Pull requests](#pull-requests)
- [Documentation](#documentation)
- [Communication](#communication)

## Reporting bugs

- Search existing issues before filing a duplicate.
- Include a clear title, minimal steps to reproduce, expected vs actual behavior, and environment details (OS, Python version, how you installed CloudPilot, relevant env vars).

## Feature requests

Open an issue to discuss scope and design before investing in a large pull request.

## Development setup

### Clone and install

```bash
git clone https://github.com/<your-org-or-username>/cloudpilot.git
cd cloudpilot
python -m venv .venv
source .venv/bin/activate   # or Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev,ml]" --extra-index-url https://download.pytorch.org/whl/cpu
```

Use the default PyPI index (or a CUDA index) instead of the CPU index if you need GPU builds of PyTorch.

### Alternative: uv

```bash
git clone https://github.com/<your-org-or-username>/cloudpilot.git
cd cloudpilot
uv sync --all-extras
```

The first `uv sync` with the `ml` extra may download a large PyTorch wheel.

### Optional: pre-commit

Install hooks so Ruff runs on commit:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files   # optional one-off check
```

Configuration lives in [`.pre-commit-config.yaml`](.pre-commit-config.yaml). CI does not require pre-commit; it invokes Ruff directly.

## Daily workflow

1. Create a branch from `main`.
2. Make changes with tests.
3. Run `ruff check .`, `ruff format .`, `mypy cloudpilot`, and `pytest` (see below).
4. Open a PR with a clear description and links to issues.

## Code style and static analysis

| Tool | Command | Config |
|------|---------|--------|
| Ruff (lint) | `ruff check .` | [`pyproject.toml`](pyproject.toml) `[tool.ruff]` |
| Ruff (format) | `ruff format .` | same |
| Mypy | `mypy cloudpilot` | `[tool.mypy]` |
| Bandit | `bandit -r cloudpilot -c pyproject.toml` | `[tool.bandit]` |

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs Ruff (check + format check), Mypy, Bandit, `pip-audit` on a frozen environment, and pytest with coverage on Python **3.10**, **3.11**, and **3.12**.

### Supply chain audit (local)

Mirror the CI step:

```bash
pip freeze > freeze.txt
pip-audit -r freeze.txt --desc on
rm freeze.txt   # or delete on Windows: del freeze.txt
```

`freeze.txt` is gitignored; do not commit it.

## Tests

```bash
pytest
```

Pytest defaults are set in [`pyproject.toml`](pyproject.toml) under `[tool.pytest.ini_options]`:

- `addopts` includes `-m 'not integration'`, so tests marked `@pytest.mark.integration` are skipped in the default run.
- Markers include `integration` and `requires_torch` (reserved for tests that assume the optional Torch install).

Run only integration-marked tests:

```bash
pytest -m integration
```

Run with coverage (and optional JUnit, as in CI):

```bash
pytest --junitxml=junit.xml -q --cov=cloudpilot --cov=cli --cov-report=term
```

Coverage reporting uses `[tool.coverage.report] fail_under = 45` in `pyproject.toml`.

### Writing tests

- Prefer **mocking** Kubernetes (`kubernetes.client`), AWS (`boto3`), and Prometheus rather than requiring live services.
- Add or extend tests under [`tests/`](tests/) for behavioral changes.
- Use `@pytest.mark.integration` only for checks that need a real cluster, cloud accounts, or long-running services, and document any required env vars in the test docstring.

## Environment variables for local runs

When exercising `self_heal` or K8s tuning against a real cluster:

| Variable | When to set |
|----------|-------------|
| `CLOUDPILOT_SELF_HEAL_CONFIRM=1` | Only if you intend to delete non-Running pods (dangerous on shared clusters). |
| `CLOUDPILOT_K8S_DRY_RUN=1` | To exercise tuning logic without `patch_namespaced_deployment`. |

See [README.md](README.md) for the full list.

## Pull requests

1. Fork the repository and branch from `main`.
2. Keep commits focused; use present-tense, imperative messages (for example: `Add dry-run guard for deployment patch`).
3. Ensure Ruff, Mypy, and pytest pass locally.
4. Describe what changed and why; reference related issues.

## Documentation

Update [README.md](README.md) for user-facing behavior, install paths, env vars, or CLI changes. Update this file when contributor workflow or CI steps change.

## Communication

Use GitHub issues and pull requests. For substantial refactors or API changes, open an issue first to agree on direction.

Thank you for helping improve CloudPilot.
