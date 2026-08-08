from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence


def run_step(title: str, command: Sequence[str]) -> None:
    print()
    print(f"==> {title}")
    print("$ " + " ".join(command))

    completed = subprocess.run(
        list(command),
        check=False,
    )

    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    python = sys.executable

    run_step(
        "Ruff lint",
        [
            python,
            "-m",
            "ruff",
            "check",
            ".",
        ],
    )

    run_step(
        "Domain static type check",
        [
            python,
            "-m",
            "mypy",
            "models/schemas.py",
            "core/scoring_policy.py",
            "core/findings.py",
            "agents/scoring_agent.py",
        ],
    )

    run_step(
        "Tests with coverage",
        [
            python,
            "-m",
            "pytest",
            "-q",
            "--cov=agents",
            "--cov=providers",
            "--cov=core",
            "--cov=models",
            "--cov=evaluation",
            "--cov-report=term-missing",
            "--cov-report=xml",
        ],
    )

    run_step(
        "Deterministic synthetic evaluation",
        [
            python,
            "scripts/run_evaluation.py",
            "--strict",
        ],
    )

    print()
    print("All Stage 6 verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
