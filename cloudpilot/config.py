"""Runtime configuration from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _truthy(name: str, default: str = "") -> bool:
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class CloudPilotSettings:
    """Settings loaded once per process; override via environment variables."""

    prometheus_url: str
    prometheus_disable_ssl: bool
    self_heal_confirm: bool
    aws_pricing_region: str
    k8s_dry_run: bool


def load_settings() -> CloudPilotSettings:
    return CloudPilotSettings(
        prometheus_url=os.environ.get(
            "CLOUDPILOT_PROMETHEUS_URL", "http://localhost:9090"
        ).strip(),
        prometheus_disable_ssl=_truthy("CLOUDPILOT_PROMETHEUS_DISABLE_SSL", "1"),
        self_heal_confirm=_truthy("CLOUDPILOT_SELF_HEAL_CONFIRM"),
        aws_pricing_region=os.environ.get(
            "CLOUDPILOT_AWS_PRICING_REGION", "us-east-1"
        ).strip(),
        k8s_dry_run=_truthy("CLOUDPILOT_K8S_DRY_RUN"),
    )
