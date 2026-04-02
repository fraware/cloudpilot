from __future__ import annotations

import logging
import threading
from collections.abc import Sequence
from importlib import resources
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ACTIONS = {0: "Scale Down", 1: "Maintain", 2: "Scale Up"}

_scaler_lock = threading.Lock()
_scaler: RLScaler | None = None


def _resolve_model_path(explicit: str | None) -> str | None:
    if explicit:
        p = Path(explicit)
        return str(p) if p.is_file() else explicit
    try:
        root = resources.files("cloudpilot")
        bundled = root / "rl_scaling_model.pt"
        if bundled.is_file():
            return str(bundled)
    except (ModuleNotFoundError, OSError, TypeError):
        pass
    fallback = Path("cloudpilot/rl_scaling_model.pt")
    if fallback.is_file():
        return str(fallback)
    return None


class RLScaler:
    """Loads TorchScript scaling model when torch and a model file are available."""

    def __init__(self, model_path: str | None = None) -> None:
        self.model: Any = None
        path = _resolve_model_path(model_path)
        try:
            import torch
        except ImportError:
            logger.warning(
                "torch is not installed; scaling returns Maintain. "
                "Install with: pip install 'cloudpilot[ml]'"
            )
            return
        if not path:
            logger.info("No rl_scaling_model.pt found; scaling uses Maintain fallback.")
            return
        try:
            self.model = torch.jit.load(path)
            self.model.eval()
        except Exception as e:
            logger.warning(
                "Could not load model from %s; using Maintain fallback: %s",
                path,
                e,
            )
            self.model = None

    def get_action(self, state: Sequence[float]) -> str:
        if self.model is None:
            return "Maintain"
        import torch

        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            q_values = self.model(state_tensor)
        action_idx = int(torch.argmax(q_values, dim=1)[0].item())
        return ACTIONS.get(action_idx, "Maintain")


def get_rl_scaler(model_path: str | None = None) -> RLScaler:
    global _scaler
    if model_path is not None:
        return RLScaler(model_path=model_path)
    with _scaler_lock:
        if _scaler is None:
            _scaler = RLScaler()
        return _scaler


def recommend_scaling(
    cpu_util: float,
    mem_util: float,
    request_rate: float,
    network_latency: float,
    user_demand: float,
) -> str:
    state = [cpu_util, mem_util, request_rate, network_latency, user_demand]
    action = get_rl_scaler().get_action(state)
    return f"RL-based Recommendation: {action}"
