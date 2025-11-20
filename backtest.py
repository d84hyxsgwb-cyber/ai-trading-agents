#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
backtest.py
-----------
Legge tutti i log giornalieri in logs/signals_YYYY-MM-DD.csv,
scarica i prezzi storici da Yahoo Finance e calcola le performance
dei segnali (STRONG BUY, BUY, SELL, STRONG SELL) a 1, 3 e 5 giorni.

In più:
- mostra il riepilogo generale (tutti gli asset)
- mostra tre riepiloghi filtrati:
    * solo CRYPTO
    * solo STOCKS
    * solo ETF
"""

import os
import glob
import datetime
from typing import List, Dict, Any, Tuple

import pandas as pd
import numpy as np
import yfinance as yf


LOG_DIR = "logs"
HORIZONS = [1, 3, 5]  # giorni dopo il segnale


# ==========================================================
#   CARICAMENTO SEGNALI DAI CSV
# ==========================================================

def load_all_signals(log_dir: str = LOG_DIR) -> pd.DataFrame:
    """
    Carica tutti i file logs/signals_YYYY-MM-DD.csv in un unico DataFrame.
    Aggiunge una colonna 'signal_date' (datetime.date).
    """
    pattern = os.path.join(log_dir, "signals_*.csv")
    files = sorted(glob.glob(pattern))

    if not files:
        raise FileNotFoundError(f"Nessun file trovato in {log_dir} con pattern signals_*.csv")

    all_rows: List[pd.DataFrame] = []

    for fpath in files:
        fname = os.path.basename(fpath)
        # ci aspettiamo "signals_YYYY-MM-DD.csv"
        try:
            date_str = fname.split("_")[1].split(".")[0]
            signal_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            print(f"[WARN] Impossibile estrarre data da filename: {fname}, salto.")
            continue

        df = pd.read_csv(fpath)

        # aggiungo la data del segnale (non timestamp completo)
        df["signal_date"] = signal_date

        all_rows.append(df)

    if not all_rows:
        raise RuntimeError("Nessuna riga di segnali valida caricata.")

    signals = pd.concat(all_rows, ignore_index=True)

    # normalizziamo alcune colonne
    signals["symbol"] = signals["symbol"].astype(str)
    signals["tech_decision"] = signals["tech_decision"].astype(str)
    signals["category"] = signals["category"].astype(str)

    # aggiungiamo una macro-categoria: CRYPTO / STOCK / ETF / OTHER
    signals["macro_category"] = signals["category"].apply(to_macro_category)

    return signals


def to_macro_category(cat: str) -> str:
    """
    Converte la category (es. 'CRYPTO/MAJOR', 'STOCK/TECH_MEGA', 'ETF/INDEX')
    in una macro-categoria: 'CRYPTO', 'STOCK', 'ETF', 'OTHER'.
    """
    if not isinstance(cat, str):
        return "OTHER"

    cu = cat.upper()
    if cu.startswith("CRYPTO"):
        return "CRYPTO"
    if cu.startswith("STOCK"):
        return "STOCK"
    if cu.startswith("ETF"):
        return "ETF"
    return "OTHER"


# ==========================================================
#   DOWNLOAD PREZZI STORICI
# ==========================================================

def download_price_history(symbols: List[str],
                           start_date: datetime.date,
                           end_date: datetime.date) -> Dict[str, pd.DataFrame]:
    """
    Scarica i dati daily (1d) da Yahoo Finance per tutti i simboli richiesti,
    nel range [start_date - buffer, end_date + buffer].
    Ritorna un dict: symbol -> DataFrame con colonna 'Close'.
    """
    prices: Dict[str, pd.DataFrame] = {}

    # piccolo buffer per sicurezza
    start_buffer = start_date - datetime.timedelta(days=10)
    end_buffer = end_date + datetime.timedelta(days=10)

    for sym in symbols:
        try:
            df = yf.download(
                sym,
                start=start_buffer.isoformat(),
                end=end_buffer.isoformat(),
                interval="1d",
                auto_adjust=True,
                progress=False,
            )
            if df is None or df.empty:
                print(f"[PRICE] Nessun dato per {sym}, salto.")
                continue

            # teniamo solo la colonna Close
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if "Close" not in df.columns:
                print(f"[PRICE] Nessuna colonna 'Close' per {sym}, salto.")
                continue

            df = df[["Close"]].dropna()
            df.index = pd.to_datetime(df.index).date
            prices[sym] = df
            print(f"[PRICE] Scaricati {len(df)} giorni di dati per {sym}.")
        except Exception as e:
            print(f"[PRICE] Errore scaricando {sym}: {e}")

    return prices


# ==========================================================
#   UTILITY: TROVARE PREZZO FUTURO
# ==========================================================

def get_future_price(df: pd.DataFrame,
                     signal_date: datetime.date,
                     horizon_days: int) -> Tuple[float, float]:
    """
    Trova il prezzo di chiusura al giorno del segnale e
    a signal_date + horizon_days (primo giorno disponibile successivo).

    Ritorna (price_entry, price_future).
    Se uno dei due manca, ritorna (np.nan, np.nan).
    """
    if df is None or df.empty:
        return np.nan, np.nan

    dates_sorted = np.array(sorted(df.index))

    # 1) Trova il giorno di entry: primo >= signal_date
    possible_entry_dates = dates_sorted[dates_sorted >= signal_date]
    if len(possible_entry_dates) == 0:
        return np.nan, np.nan

    entry_date = possible_entry_dates[0]
    price_entry = float(df.loc[entry_date, "Close"])

    # 2) Trova il giorno futuro: primo >= signal_date + horizon_days
    target = signal_date + datetime.timedelta(days=horizon_days)
    possible_future_dates = dates_sorted[dates_sorted >= target]
    if len(possible_future_dates) == 0:
        return price_entry, np.nan

    future_date = possible_future_dates[0]
    price_future = float(df.loc[future_date, "Close"])

    return price_entry, price_future


# ==========================================================
#   CALCOLO RENDIMENTI
# ==========================================================

def compute_forward_returns(signals: pd.DataFrame,
                            prices: Dict[str, pd.DataFrame],
                            horizons: List[int]) -> pd.DataFrame:
    """
    Per ogni segnale, calcola i rendimenti a 1, 3, 5 giorni (HORIZONS).
    Aggiunge colonne return_1d, return_3d, ... in %.
    """
    # inizializza le colonne dei ritorni
    for h in horizons:
        signals[f"return_{h}d"] = np.nan

    for idx, row in signals.iterrows():
        sym = row["symbol"]
        signal_date = row["signal_date"]

        if sym not in prices:
            continue

        df_price = prices[sym]

        for h in horizons:
            price_entry, price_future = get_future_price(df_price, signal_date, h)
            if np.isnan(price_entry) or np.isnan(price_future):
                continue
            ret = (price_future - price_entry) / price_entry * 100.0
            signals.at[idx, f"return_{h}d"] = ret

    return signals


# ==========================================================
#   STATISTICHE
# ==========================================================

def summarize_by_decision(signals: pd.DataFrame,
                          horizons: List[int],
                          title: str = "RISULTATI BACKTEST PER TIPO DI SEGNALE") -> None:
    """
    Stampa un riepilogo statistico per tipo di decisione tecnica
    (STRONG BUY, BUY, HOLD / WAIT, SELL, STRONG SELL) per il sottoinsieme
    di segnali fornito.
    """
    if signals.empty:
        print(f"\n===== {title} =====")
        print("Nessun segnale disponibile per questo filtro.\n")
        return

    decisions = sorted(signals["tech_decision"].unique())

    print(f"\n===== {title} =====\n")

    for dec in decisions:
        df_dec = signals[signals["tech_decision"] == dec].copy()
        n_signals = len(df_dec)
        if n_signals == 0:
            continue

        print(f"--- {dec} ---")
        print(f"Numero segnali: {n_signals}")

        for h in horizons:
            col = f"return_{h}d"
            valid = df_dec[col].dropna()

            if valid.empty:
                print(f"  Orizzonte {h}d: nessun dato valido.")
                continue

            mean_ret = valid.mean()
            median_ret = valid.median()
            winrate = (valid > 0).mean() * 100.0

            print(
                f"  {h}d -> media: {mean_ret:+.2f}%   "
                f"mediana: {median_ret:+.2f}%   "
                f"winrate: {winrate:.1f}%   "
                f"(n={len(valid)})"
            )

        print()


def main():
    print("=== BACKTEST AVANZATO SU SEGNALI SALVATI ===\n")

    # 1) Carica tutti i segnali
    signals = load_all_signals(LOG_DIR)
    print(f"Segnali totali caricati: {len(signals)}")

    # calcoliamo il range di date per scaricare i prezzi
    min_date = signals["signal_date"].min()
    max_date = signals["signal_date"].max()
    print(f"Periodo segnali: {min_date}  ->  {max_date}")

    # 2) Scarica i prezzi per tutti i simboli
    symbols = sorted(signals["symbol"].unique())
    print(f"Numero simboli unici: {len(symbols)}")
    prices = download_price_history(symbols, min_date, max_date)

    # 3) Calcola i rendimenti futuri
    signals_with_returns = compute_forward_returns(signals, prices, HORIZONS)

    # 4) Riepilogo generale
    summarize_by_decision(
        signals_with_returns,
        HORIZONS,
        title="RISULTATI BACKTEST - TUTTI GLI ASSET",
    )

    # 5) Riepilogo per macro-categoria

    # CRYPTO
    crypto_signals = signals_with_returns[signals_with_returns["macro_category"] == "CRYPTO"]
    summarize_by_decision(
        crypto_signals,
        HORIZONS,
        title="RISULTATI BACKTEST - SOLO CRYPTO",
    )

    # STOCK
    stock_signals = signals_with_returns[signals_with_returns["macro_category"] == "STOCK"]
    summarize_by_decision(
        stock_signals,
        HORIZONS,
        title="RISULTATI BACKTEST - SOLO STOCKS",
    )

    # ETF
    etf_signals = signals_with_returns[signals_with_returns["macro_category"] == "ETF"]
    summarize_by_decision(
        etf_signals,
        HORIZONS,
        title="RISULTATI BACKTEST - SOLO ETF",
    )


if __name__ == "__main__":
    main()
