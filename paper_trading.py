# paper_trading.py
# Gestione semplice di "paper trading" (account virtuale).
# Salva le operazioni in paper_trades.csv nella cartella del progetto.

from __future__ import annotations

import os
import csv
from typing import Dict
from datetime import datetime

import pandas as pd

TRADES_FILE = "paper_trades.csv"

COLUMNS = [
    "id",
    "symbol",
    "side",
    "style",
    "lot",
    "entry",
    "stop_loss",
    "take_profit",
    "open_time",
    "close_time",
    "status",        # OPEN / CLOSED
    "last_price",
    "pnl",
    "pnl_pct",
    "risk_amount",
    "gain_amount",
]


def _ensure_file() -> None:
    """Crea il file CSV se non esiste."""
    if not os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()


def load_trades() -> pd.DataFrame:
    """Carica tutte le operazioni di paper trading."""
    _ensure_file()
    df = pd.read_csv(TRADES_FILE)
    return df


def save_trades(df: pd.DataFrame) -> None:
    """Salva il DataFrame nel file CSV."""
    df.to_csv(TRADES_FILE, index=False)


def open_trade(
    symbol: str,
    side: str,
    style: str,
    lot: float,
    entry: float,
    stop_loss: float,
    take_profit: float,
    capital: float,
) -> Dict:
    """
    Apre un nuovo trade virtuale e lo aggiunge al CSV.
    Ritorna il dict della riga creata.
    """
    _ensure_file()
    df = load_trades()

    new_id = int(df["id"].max()) + 1 if not df.empty else 1

    side_u = side.upper()
    risk_per_unit = abs(entry - stop_loss)
    gain_per_unit = (
        max(take_profit - entry, 0.0) if side_u == "LONG" else max(entry - take_profit, 0.0)
    )

    risk_amount = risk_per_unit * lot
    gain_amount = gain_per_unit * lot

    now_iso = datetime.utcnow().isoformat()

    row = {
        "id": new_id,
        "symbol": symbol,
        "side": side_u,
        "style": style,
        "lot": float(lot),
        "entry": float(entry),
        "stop_loss": float(stop_loss),
        "take_profit": float(take_profit),
        "open_time": now_iso,
        "close_time": "",
        "status": "OPEN",
        "last_price": float(entry),
        "pnl": 0.0,
        "pnl_pct": 0.0,
        "risk_amount": float(risk_amount),
        "gain_amount": float(gain_amount),
    }

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_trades(df)

    return row


def update_trades_with_price(
    symbol: str,
    last_price: float,
    capital: float,
) -> pd.DataFrame:
    """
    Aggiorna P/L e stato di tutti i trade su `symbol` usando last_price:
      - aggiorna last_price e pnl / pnl_pct
      - se il prezzo tocca TP o SL, chiude il trade (status = CLOSED)
    Ritorna il DataFrame completo aggiornato.
    """
    _ensure_file()
    df = load_trades()
    if df.empty:
        return df

    changed = False
    for idx, row in df[df["symbol"].astype(str) == str(symbol)].iterrows():
        if str(row["status"]).upper() != "OPEN":
            continue

        side = str(row["side"]).upper()
        entry = float(row["entry"])
        sl = float(row["stop_loss"])
        tp = float(row["take_profit"])
        lot = float(row["lot"])

        # Hit TP / SL?
        if side == "LONG":
            hit_tp = last_price >= tp
            hit_sl = last_price <= sl
            pnl = (last_price - entry) * lot
        else:  # SHORT
            hit_tp = last_price <= tp
            hit_sl = last_price >= sl
            pnl = (entry - last_price) * lot

        df.at[idx, "last_price"] = float(last_price)
        df.at[idx, "pnl"] = float(pnl)
        df.at[idx, "pnl_pct"] = float((pnl / capital * 100.0) if capital > 0 else 0.0)

        if hit_tp or hit_sl:
            df.at[idx, "status"] = "CLOSED"
            df.at[idx, "close_time"] = datetime.utcnow().isoformat()

        changed = True

    if changed:
        save_trades(df)

    return df
