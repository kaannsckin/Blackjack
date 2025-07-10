"""W&B + TensorBoard başlangıç yardımcıları (FAZ 0 – F0.4)"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Any, Dict, Optional

import wandb
from torch.utils.tensorboard import SummaryWriter  # noqa: E402 – optional dep; SB3 kurulumunda Torch gelir


def init_wandb(
    project: str = "blackjack-ai-sim",
    entity: Optional[str] = None,
    name: Optional[str] = None,
    run_name: Optional[str] = None,
    config: Dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> wandb.wandb_sdk.wandb_run.Run:
    run = wandb.init(
        project=project,
        entity=entity,
        name=name or run_name,
        config=config,
        tags=tags,
        save_code=True,
        monitor_gym=True,
    )
    return run


def get_tb_writer(log_dir: str | Path | None = None) -> SummaryWriter:
    """Tarih‑damgalı TensorBoard log dizini oluşturur."""
    if log_dir is None:
        log_dir = Path("runs") / _dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    return SummaryWriter(log_dir=str(log_dir))