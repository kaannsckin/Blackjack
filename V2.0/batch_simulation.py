# batch_simulation.py – step 5‑D: bug‑fix & log‑tabanlı KPI hesaplama
"""Tam kapsamlı batch simülasyon (v2)
=====================================
Düzeltmeler
-----------
1. **TypeError** – `BlackjackSimulation` çağrısı yanlış argüman dizilimi → şimdi
   `BlackjackSimulation(num_games, players_cfg, scenario["num_decks"])`.
2. **player_wins / losses** öznitelikleri, güncel `simulation.py` sürümünde yok.
   KPI’lar artık **log kayıtlarından** (`sim.records`) hesaplanıyor.
3. **Metrikler basitleştirildi** – toplam (oyuncu bağımsız) Win‑Rate, EV, RTP.

Çalışma mantığı
--------------
* `_aggregate_logs(records)` fonksiyonu -> `wins`, `losses`, `pushes`,
  `total_hands` döndürür.
* EV = (wins − losses)/total, RTP = 100×(EV+1).

Geçici olarak çok‑oyunculu ayırımı kaldırıldı (loglarda oyuncu ID yok). İstersek
`blackjack_engine.BlackjackGame._record()` içine `player_id` alanı ekleyip tekrar
çok‑oyunculu sütunlara dönebiliriz.
"""

from __future__ import annotations
import argparse
import itertools
import logging
from pathlib import Path
from typing import Dict, Generator, List, Optional

import pandas as pd
import sqlalchemy as sa

import blackjack_engine as eng
from simulation import BlackjackSimulation

###############################################################################
# 1) Parametre Izgarası
###############################################################################
_DECKS          = [1, 2, 6, 8]
_DEALER_RULES   = ["S17", "H17"]
_PENETRATIONS   = [0.50, 0.65, 0.75]
_DAS_OPTIONS    = [True, False]
_SURRENDER_OPTS = [True, False]

###############################################################################
# 2) Senaryo Üreticisi
###############################################################################

def generate_scenarios() -> Generator[Dict, None, None]:
    for num_decks, rule, pen, das, surr in itertools.product(
        _DECKS, _DEALER_RULES, _PENETRATIONS, _DAS_OPTIONS, _SURRENDER_OPTS
    ):
        yield {
            "num_decks": num_decks,
            "dealer_rule": rule,
            "penetration": pen,
            "das": das,
            "surrender": surr,
        }

###############################################################################
# 3) Engine Patch
###############################################################################

def _patch_engine(dealer_rule: str, penetration: float) -> None:
    eng.MIN_PENETRATION_RATIO = 1.0 - penetration

    if dealer_rule == "S17":
        def _dealer_play_s17(self, deck):
            while self.hand.value() < 17:
                self.hand.add_card(deck.deal_card())
        eng.Dealer.play = _dealer_play_s17  # type: ignore[attr-defined]
    else:
        def _dealer_play_h17(self, deck):
            while True:
                total = self.hand.value()
                soft = any(c.value == "A" for c in self.hand.cards) and total == 17
                if total > 17 or (total == 17 and not soft):
                    break
                self.hand.add_card(deck.deal_card())
        eng.Dealer.play = _dealer_play_h17  # type: ignore[attr-defined]

###############################################################################
# 4) KPI helpers (log tabanlı)
###############################################################################

def _aggregate_logs(records: List[Dict]) -> Dict[str, float]:
    wins = sum(1 for r in records if r.get("sonuc") == 2)
    losses = sum(1 for r in records if r.get("sonuc") == 0)
    pushes = sum(1 for r in records if r.get("sonuc") == 1)
    total = wins + losses + pushes or 1  # zero‑division guard
    win_rate = wins * 100 / total
    ev = (wins - losses) / total
    rtp = (ev + 1) * 100
    return {
        "win_rate": win_rate,
        "ev": ev,
        "rtp": rtp,
        "hands_played": total,
    }

###############################################################################
# 5) Senaryo Runner
###############################################################################

def run_scenario(num_games: int, players_cfg: List[Dict], scenario: Dict):
    _patch_engine(scenario["dealer_rule"], scenario["penetration"])

    sim = BlackjackSimulation(num_games, players_cfg, scenario["num_decks"])
    sim.run()
    kpi = _aggregate_logs(sim.records)

    return {
        **scenario,
        "num_games": num_games,
        **kpi,
    }

###############################################################################
# 6) Batch Runner + Persist
###############################################################################

def _persist_to_db(df: pd.DataFrame, db_url: str):
    engine = sa.create_engine(db_url)
    df.to_sql("scenario_results", engine, if_exists="append", index=False)


def run_all_scenarios(*, num_games: int, players_cfg: List[Dict], db_url: Optional[str] = None, csv_path: Optional[Path] = None) -> pd.DataFrame:
    records: List[Dict] = []
    for scn in generate_scenarios():
        logging.info("Çalışan senaryo → %s", scn)
        records.append(run_scenario(num_games, players_cfg, scn))
    df = pd.DataFrame(records)

    if csv_path:
        df.to_csv(csv_path, index=False)
        logging.info("CSV → %s", csv_path.resolve())
    if db_url:
        _persist_to_db(df, db_url)
        logging.info("DB → %s", db_url)
    return df

###############################################################################
# 7) CLI
###############################################################################

def _cli():
    p = argparse.ArgumentParser(description="Blackjack batch simulation runner")
    p.add_argument("--hands", type=int, default=10_000)
    p.add_argument("--db", type=str)
    p.add_argument("--csv", type=str, default="scenario_results.csv")
    a = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    players = [{"strategy": "smart", "bet_style": "flat"}]
    df = run_all_scenarios(num_games=a.hands, players_cfg=players, db_url=a.db, csv_path=Path(a.csv))
    print("\n=== Özet ===")
    print(df.head(10).to_string(index=False))

if __name__ == "__main__":
    _cli()
