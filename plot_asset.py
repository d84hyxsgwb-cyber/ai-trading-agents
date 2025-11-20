#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
plot_asset.py
-------------
Mostra un grafico per un singolo asset con:

- Prezzo di chiusura (daily, ultimi 180 giorni)
- EMA20 / EMA50 / EMA200
- Bande di Bollinger

Se disponibile, legge l'ultimo file di segnali in logs/signals_YYYY-MM-DD.csv
e mostra nell'intestazione l'ultimo segnale tecnico per quel simbolo.

Uso da terminale:

    source env/bin/activate
    python3 plot_asset.py BTC-USD
    python3 plot_asset.py AAPL
    python3 plot_asset.py SPY

Se non passi il simbolo da riga di comando, te lo chiede a input.
"""

import sys
import os
import glob
import datetime
from typing import Optional, Tuple

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from ta.trend import EMAIndicator
from ta.volatility import BollingerBands


LOG_DIR = "logs"
DEFAULT_PERIOD_DAYS = 180


# ==========================================================
#   LETTURA ULTIMO SEGNALE PER UN SIMBOLO
# ==========================================================

def load_latest_signal_for_symbol(symbol: str, log_dir: str = LOG_DIR) -> Optional[dict]:
    """
    Cerca l'ultimo file logs/signals_YYYY-MM-DD.csv,
    filtra per il simbolo richiesto e ritorna l'ultima riga come dict,
    oppure None se non trova nulla.
    """
    pattern = os.path.join(log_dir, "signals_*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        return None

    latest_path = max(
        files,
        key=lambda p: p.split("_")[1].split(".")[0]
    )

    try:
        df = pd.read_csv(latest_path)
    except Exception:
        return None

    if "symbol" not in df.columns:
        return None

    df_symbol = df[df["symbol"] == symbol].copy()
    if df_symbol.empty:
        return None

    # prendo l'ultima riga (in base all'ordine nel file)
    last_row = df_symbol.iloc[-1]

    # preparo un dict con i campi principali (se ci sono)
    info = {
        "symbol": symbol,
        "name": last_row.get("name", symbol),
        "category": last_row.get("category", ""),
        "tech_decision": last_row.get("tech_decision", "N/A"),
        "tech_score": last_row.get("tech_score", 0),
        "news_score": last_row.get("news_score", 0.0),
        "ensemble_score": last_row.get("ensemble_score", 0.0),
    }
    return info


# ==========================================================
#   DOWNLOAD E INDICATORI
# ==========================================================

def download_price_data(symbol: str,
                        days: int = DEFAULT_PERIOD_DAYS) -> pd.DataFrame:
    """
    Scarica dati daily degli ultimi 'days' giorni per il simbolo da Yahoo Finance.
    Ritorna un DataFrame con almeno la colonna 'Close'.
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days + 10)  # piccolo buffer

    df = yf.download(
        symbol,
        start=start.isoformat(),
        end=end.isoformat(),
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if df is None or df.empty:
        raise ValueError(f"Nessun dato scaricato per {symbol}.")

    # se MultiIndex, appiattisco
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if "Close" not in df.columns:
        raise ValueError(f"Per {symbol} manca la colonna 'Close' nei dati scaricati.")

    df = df[["Close"]].dropna()
    df.index = pd.to_datetime(df.index)

    # calcolo indicatori
    close = df["Close"]

    df["EMA20"] = EMAIndicator(close=close, window=20).ema_indicator()
    df["EMA50"] = EMAIndicator(close=close, window=50).ema_indicator()

    # EMA200 solo se ho abbastanza dati
    if len(df) >= 200:
        df["EMA200"] = EMAIndicator(close=close, window=200).ema_indicator()
    else:
        df["EMA200"] = None

    bb = BollingerBands(close=close, window=20, window_dev=2)
    df["BB_high"] = bb.bollinger_hband()
    df["BB_low"] = bb.bollinger_lband()

    # tengo solo gli ultimi 'days' giorni
    df = df.iloc[-days:]

    return df


# ==========================================================
#   PLOT
# ==========================================================

def plot_asset(symbol: str):
    """
    Scarica i dati, calcola indicatori e mostra il grafico.
    """
    print(f"Scarico dati per {symbol} (ultimi {DEFAULT_PERIOD_DAYS} giorni)...")
    df = download_price_data(symbol, days=DEFAULT_PERIOD_DAYS)

    # Recupero ultimo segnale (se esiste)
    signal_info = load_latest_signal_for_symbol(symbol)

    # Setup grafico
    plt.figure(figsize=(12, 6))
    ax = plt.gca()

    ax.plot(df.index, df["Close"], label="Close", linewidth=1.5)
    ax.plot(df.index, df["EMA20"], label="EMA20", linewidth=1.0)
    ax.plot(df.index, df["EMA50"], label="EMA50", linewidth=1.0)

    if df["EMA200"].notna().any():
        ax.plot(df.index, df["EMA200"], label="EMA200", linewidth=1.0)

    # bande di Bollinger
    ax.plot(df.index, df["BB_high"], linestyle="--", linewidth=0.8, label="BB high")
    ax.plot(df.index, df["BB_low"], linestyle="--", linewidth=0.8, label="BB low")

    ax.set_xlabel("Data")
    ax.set_ylabel("Prezzo")
    ax.grid(True, linestyle="--", alpha=0.4)

    # Titolo
    base_title = f"{symbol} - Prezzo con EMA e Bande di Bollinger (ultimi {DEFAULT_PERIOD_DAYS} giorni)"

    if signal_info is not None:
        dec = signal_info["tech_decision"]
        ens = float(signal_info["ensemble_score"])
        tech = int(signal_info["tech_score"])
        news = float(signal_info["news_score"])
        cat = signal_info["category"]

        subtitle = (
            f"Ultimo segnale: {dec}  |  ensemble={ens:+.2f}, tech={tech}, news={news:+.2f}, "
            f"categoria={cat}"
        )
        plt.title(base_title + "\n" + subtitle, fontsize=11)
    else:
        plt.title(base_title)

    plt.legend()
    plt.tight_layout()
    plt.show()


# ==========================================================
#   MAIN
# ==========================================================

def main():
    if len(sys.argv) >= 2:
        symbol = sys.argv[1].strip()
    else:
        symbol = input("Inserisci il simbolo (es. BTC-USD, AAPL, SPY): ").strip()

    if not symbol:
        print("Nessun simbolo inserito, esco.")
        return

    try:
        plot_asset(symbol)
    except Exception as e:
        print(f"[ERRORE] {e}")


if __name__ == "__main__":
    main()
