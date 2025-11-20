#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
advisor_agent.py
----------------
Legge l'ultimo file di segnali in logs/signals_YYYY-MM-DD.csv,
seleziona i migliori LONG e SHORT, e chiede a OpenAI di generare
un commento "da gestore" in lingua italiana.

Richiede:
- OPENAI_API_KEY impostata (es. in .env)
- librerie: pandas, python-dotenv, openai
"""

import os
import glob
import datetime
from typing import List, Tuple

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


LOG_DIR = "logs"
N_TOP_LONG = 5   # quanti long mostrare
N_TOP_SHORT = 5  # quanti short mostrare
OPENAI_MODEL = "gpt-4o-mini"  # puoi cambiarlo se vuoi


# ==========================================================
#   UTILITY: MACRO CATEGORIA
# ==========================================================

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
#   CARICAMENTO ULTIMO FILE DI SEGNALI
# ==========================================================

def load_latest_signals(log_dir: str = LOG_DIR) -> Tuple[pd.DataFrame, datetime.date]:
    """
    Trova l'ultimo file logs/signals_YYYY-MM-DD.csv,
    lo carica in un DataFrame e ritorna (df, data).
    """
    pattern = os.path.join(log_dir, "signals_*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Nessun file trovato in {log_dir} con pattern signals_*.csv")

    # ultimo per data nel nome
    latest_path = max(
        files,
        key=lambda p: p.split("_")[1].split(".")[0]
    )
    fname = os.path.basename(latest_path)
    date_str = fname.split("_")[1].split(".")[0]
    signal_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    df = pd.read_csv(latest_path)

    # normalizza alcune colonne che ci servono
    if "category" not in df.columns:
        df["category"] = "UNKNOWN"

    df["macro_category"] = df["category"].apply(to_macro_category)

    # se non ci sono queste colonne, le inizializzo
    if "ensemble_score" not in df.columns:
        raise ValueError("Manca la colonna 'ensemble_score' nel file dei segnali.")

    if "tech_decision" not in df.columns:
        df["tech_decision"] = "N/A"

    if "tech_score" not in df.columns:
        df["tech_score"] = 0

    if "news_score" not in df.columns:
        df["news_score"] = 0.0

    if "name" not in df.columns:
        df["name"] = df["symbol"]

    return df, signal_date


# ==========================================================
#   SELEZIONE TOP LONG E SHORT
# ==========================================================

def select_top_signals(df: pd.DataFrame,
                       n_long: int = N_TOP_LONG,
                       n_short: int = N_TOP_SHORT) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Seleziona:
    - top LONG: decisione BUY / STRONG BUY, ensemble_score > 0
    - top SHORT: decisione SELL / STRONG SELL, ensemble_score < 0
    """
    # Filtra long
    long_mask = df["tech_decision"].isin(["BUY", "STRONG BUY"]) & (df["ensemble_score"] > 0)
    long_df = df[long_mask].copy()
    long_df = long_df.sort_values(by="ensemble_score", ascending=False).head(n_long)

    # Filtra short
    short_mask = df["tech_decision"].isin(["SELL", "STRONG SELL"]) & (df["ensemble_score"] < 0)
    short_df = df[short_mask].copy()
    short_df = short_df.sort_values(by="ensemble_score", ascending=True).head(n_short)

    return long_df, short_df


def format_signals_table(df: pd.DataFrame, title: str) -> str:
    """
    Crea una tabella testuale semplice per il terminale.
    """
    if df.empty:
        return f"{title}\n(nessun segnale)\n"

    lines = [title]
    lines.append(
        f"{'Sym':<10} {'Cat':<8} {'Decisione':<12} {'Ens.':>6} {'Tech':>6} {'News':>6}"
    )
    lines.append("-" * 60)

    for _, row in df.iterrows():
        sym = str(row.get("symbol", ""))[:10]
        macro = str(row.get("macro_category", ""))[:8]
        dec = str(row.get("tech_decision", ""))[:12]
        ens = float(row.get("ensemble_score", 0.0))
        tech = int(row.get("tech_score", 0))
        news = float(row.get("news_score", 0.0))
        lines.append(
            f"{sym:<10} {macro:<8} {dec:<12} {ens:>+6.2f} {tech:>6d} {news:>+6.2f}"
        )

    lines.append("")
    return "\n".join(lines)


# ==========================================================
#   CHIAMATA A OPENAI
# ==========================================================

def build_ai_prompt(signal_date: datetime.date,
                    long_df: pd.DataFrame,
                    short_df: pd.DataFrame) -> str:
    """
    Costruisce il testo da dare al modello OpenAI come contesto.
    """
    lines = []
    lines.append(f"Data segnali: {signal_date.isoformat()}")
    lines.append("")
    lines.append("TOP LONG (BUY / STRONG BUY):")
    if long_df.empty:
        lines.append(" - nessun segnale long.")
    else:
        for _, row in long_df.iterrows():
            lines.append(
                f" - {row['symbol']} ({row['macro_category']}) | "
                f"decisione={row['tech_decision']}, "
                f"ensemble={row['ensemble_score']:+.2f}, "
                f"tech_score={int(row['tech_score'])}, "
                f"news_score={float(row['news_score']):+.2f}"
            )

    lines.append("")
    lines.append("TOP SHORT (SELL / STRONG SELL):")
    if short_df.empty:
        lines.append(" - nessun segnale short.")
    else:
        for _, row in short_df.iterrows():
            lines.append(
                f" - {row['symbol']} ({row['macro_category']}) | "
                f"decisione={row['tech_decision']}, "
                f"ensemble={row['ensemble_score']:+.2f}, "
                f"tech_score={int(row['tech_score'])}, "
                f"news_score={float(row['news_score']):+.2f}"
            )

    return "\n".join(lines)


def ask_openai_advice(context_text: str) -> str:
    """
    Usa OpenAI (model=OPENAI_MODEL) per generare un commento in italiano
    sui segnali passati.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY non impostata. Aggiungila al tuo .env.")

    client = OpenAI(api_key=api_key)

    system_instructions = (
        "Sei un analista quantitativo e portfolio manager. "
        "Ricevi un elenco di segnali generati da un sistema tecnico+news "
        "su crypto, azioni e ETF. "
        "Devi rispondere in italiano, in modo sintetico e professionale. "
        "Non fornire consulenza finanziaria personalizzata, "
        "ma limita la risposta a un commento generale sui segnali ricevuti. "
        "Evidenzia:\n"
        "- eventuali cluster (es. molte tech forti, molte crypto deboli, ecc.)\n"
        "- 3-5 opportunità long più interessanti secondo i dati\n"
        "- 3-5 rischi / short / aree da evitare\n"
        "- un breve riepilogo del sentiment generale del portafoglio segnali.\n"
        "Chiudi SEMPRE con una frase del tipo: "
        "\"Questo non è un consiglio finanziario ma solo un'analisi tecnica/statistica dei segnali.\""
    )

    # Usiamo l'API Responses (nuovo standard) oppure chat.completions.
    # Qui uso Responses per allinearci alla libreria moderna.
    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=system_instructions,
        input=context_text,
    )

    # metodo comodo per ottenere il testo
    try:
        return response.output_text
    except Exception:
        # fallback generico nel caso la struttura della response sia diversa
        return str(response)


# ==========================================================
#   MAIN
# ==========================================================

def main():
    print("=== ADVISOR AGENT ===\n")

    # 1) Carica l'ultimo file di segnali
    signals, signal_date = load_latest_signals(LOG_DIR)
    print(f"Ultimo file segnali: {signal_date.isoformat()}")
    print(f"Numero totale di asset analizzati: {len(signals)}\n")

    # 2) Seleziona i top long e short
    long_df, short_df = select_top_signals(signals, N_TOP_LONG, N_TOP_SHORT)

    # 3) Mostra tabelle locali
    print(format_signals_table(long_df, ">>> TOP LONG (BUY / STRONG BUY)"))
    print(format_signals_table(short_df, ">>> TOP SHORT (SELL / STRONG SELL)"))

    # 4) Costruisci il contesto da passare a OpenAI
    context_text = build_ai_prompt(signal_date, long_df, short_df)

    print("Invio i segnali all'IA di OpenAI per generare un commento...\n")

    # 5) Chiamata al modello OpenAI
    try:
        advice = ask_openai_advice(context_text)
    except Exception as e:
        print(f"[ERRORE OpenAI] {e}")
        return

    print("===== COMMENTO DELL'ADVISOR IA =====\n")
    print(advice)
    print("\n=====================================\n")


if __name__ == "__main__":
    main()
