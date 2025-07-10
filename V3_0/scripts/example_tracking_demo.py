"""FAZ 0 – F0.4 demo: W&B + TensorBoard log akışı."""
from __future__ import annotations

import random
import time

import numpy as np
import wandb

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.tracking import get_tb_writer, init_wandb


def main() -> None:
    run = init_wandb(project="blackjack-ai-sim", run_name="tracking_demo", tags=["f0.4", "demo"])
    writer = get_tb_writer()

    # Rastgele metrik akışı (örnek)
    for step in range(100):
        reward = np.sin(step / 10) + random.gauss(0, 0.1)
        wandb.log({"reward": reward}, step=step)
        writer.add_scalar("reward", reward, global_step=step)
        time.sleep(0.02)

    writer.close()
    run.finish()


if __name__ == "__main__":
    main()

2
