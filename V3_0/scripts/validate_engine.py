"""Simülasyon doğrulama betiği – FAZ 0 (V2.0 motor uyum)
1 000 000 el temel strateji simülasyonu çalıştırır ve kasa avantajını raporlar.
"""
from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter

import pandas as pd

import sys
import os


V2_PATH = Path(__file__).resolve().parents[2] / "V2_0"
if str(V2_PATH) not in sys.path:
    sys.path.append(str(V2_PATH))

from counting_systems import CardCounter
from simulation import BlackjackSimulation  # V2.0: sınıf adı `BlackjackSimulation` olabilir
from blackjack_engine import BlackjackGame


logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)


PLAYERS_CFG = [
    {
        "strategy": "basic",
        "bet_style": "flat",
        "min_bet": 1,
        "bankroll": 1_000,  # başlangıç bakiyesi
    }
]
N_HANDS = 1_000_000


def main() -> None:
    # --- Motoru oluştur ---
    counter = CardCounter("hi_lo",6)
    engine = BlackjackGame(players_cfg=PLAYERS_CFG, num_decks=6, counter=counter, game_id=0)

    # --- Simülasyonu çalıştır ---
    sim = BlackjackSimulation(N_HANDS, PLAYERS_CFG, num_decks=6)

    t0 = perf_counter()
    results = sim.run()  # DataFrame, liste veya None olabilir
    elapsed = perf_counter() - t0

    # --- El sayısını belirle ---
    num_hands: int | None = None
    if isinstance(results, pd.DataFrame):
        num_hands = results.shape[0]
    elif hasattr(sim, "num_hands"):
        num_hands = getattr(sim, "num_hands")
    elif hasattr(sim, "num_games"):
        num_hands = getattr(sim, "num_games")
    if not num_hands:
        num_hands = N_HANDS  # fallback

    # --- Bankroll hesapla ---
    initial_bankroll = PLAYERS_CFG[0]["bankroll"]
    final_bankroll = engine.players[0].bankroll

    player_return = (final_bankroll - initial_bankroll) / (num_hands * PLAYERS_CFG[0]["min_bet"])
    house_edge = -player_return

    theoretical_edge = 0.0053  # %0.53
    diff_pp = (house_edge - theoretical_edge) * 100

    LOGGER.info("Simülasyon tamamlandı: %.1f s (eller=%d)", elapsed, num_hands)
    LOGGER.info("House edge = %.4f (teorik=%.4f, fark=%+.2f pp)", house_edge, theoretical_edge, diff_pp)

    # --- Rapor güncelle ---
    report_path = Path(__file__).parents[1] / "reports" / "engine_validation.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)  # Klasörü oluştur
    report_path.write_text(
        "# Engine Validation\n\n"
        f"* Eller: {num_hands:,}\n"
        "* Parametreler: 6 deste, S17 (varsayılan), DAS yok\n"
        f"* House edge (simülasyon): **{house_edge:.4%}**\n"
        f"* Teorik değer: **{theoretical_edge:.4%}**\n"
        f"* Fark: **{diff_pp:+.2f} yüzde‑puan**\n"
    )


if __name__ == "__main__":
    main()