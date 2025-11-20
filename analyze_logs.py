"""
analyze_logs.py
Script di analisi dei log generati dagli agenti:
- signals_log.csv
- ranking_log.csv
- orders_log.csv

Obiettivo: darti una vista "da prodotto" su cosa sta facendo la tua AI.
"""

import os
import csv
from collections import defaultdict, Counter
from statistics import mean
from typing import List, Dict, Any


def load_csv(path: str) -> List[Dict[str, Any]]:
    """
    Carica un CSV e ritorna una lista di dict.
    Se il file non esiste, ritorna lista vuota.
    """
    if not os.path.isfile(path):
        print(f"[INFO] File non trovato: {path}")
        return []

    rows: List[Dict[str, Any]] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


# =========================================================
# ANALISI SIGNALS_LOG
# =========================================================

def analyze_signals_log():
    rows = load_csv("signals_log.csv")
    if not rows:
        print("\n[signals_log] Nessun dato da analizzare.\n")
        return

    print("\n========== ANALISI signals_log.csv ==========\n")
    print(f"Numero totale di segnali tecnici: {len(rows)}")

    # Conteggio per symbol
    per_symbol_scores = defaultdict(list)

    for r in rows:
        sym = r.get("symbol", "UNKNOWN")
        try:
            score = float(r.get("score", 0.0))
        except Exception:
            score = 0.0
        per_symbol_scores[sym].append(score)

    print(f"Numero di asset diversi (signals): {len(per_symbol_scores)}\n")

    # Calcolo media score per symbol
    symbol_avg = []
    for sym, scores in per_symbol_scores.items():
        symbol_avg.append((sym, mean(scores), len(scores)))

    # Ordiniamo per media score decrescente
    symbol_avg.sort(key=lambda x: x[1], reverse=True)

    print("Top 10 asset per score tecnico medio:")
    for sym, avg_score, count in symbol_avg[:10]:
        print(f"  - {sym:10s} | score medio = {avg_score:5.2f} | segnali = {count}")

    # Ordiniamo anche per score medio più basso (bearish)
    symbol_avg.sort(key=lambda x: x[1])

    print("\nTop 10 asset più bearish (score medio più basso):")
    for sym, avg_score, count in symbol_avg[:10]:
        print(f"  - {sym:10s} | score medio = {avg_score:5.2f} | segnali = {count}")

    print()


# =========================================================
# ANALISI RANKING_LOG
# =========================================================

def analyze_ranking_log():
    rows = load_csv("ranking_log.csv")
    if not rows:
        print("\n[ranking_log] Nessun dato da analizzare.\n")
        return

    print("\n========== ANALISI ranking_log.csv ==========\n")
    print(f"Numero totale di righe di ranking: {len(rows)}")

    per_symbol_data = defaultdict(lambda: {
        "composite": [],
        "category": None,
        "name": None,
    })

    for r in rows:
        sym = r.get("symbol", "UNKNOWN")
        comp = r.get("composite")
        cat = r.get("category")
        name = r.get("name")

        try:
            comp_val = float(comp)
        except Exception:
            comp_val = 0.0

        per_symbol_data[sym]["composite"].append(comp_val)
        if cat:
            per_symbol_data[sym]["category"] = cat
        if name:
            per_symbol_data[sym]["name"] = name

    summary = []
    for sym, data in per_symbol_data.items():
        if not data["composite"]:
            continue
        avg_comp = mean(data["composite"])
        count = len(data["composite"])
        summary.append((
            sym,
            data["name"] or sym,
            data["category"] or "UNKNOWN",
            avg_comp,
            count,
        ))

    # Più bullish per composite medio
    summary.sort(key=lambda x: x[3], reverse=True)

    print("Top 10 asset per composite score medio (più bullish):")
    for sym, name, cat, avg_comp, count in summary[:10]:
        print(f"  - {name:20s} ({sym:8s}) [{cat:6s}] | composite medio = {avg_comp:5.2f} | occorrenze = {count}")

    # Più bearish
    summary.sort(key=lambda x: x[3])

    print("\nTop 10 asset per composite score medio (più bearish):")
    for sym, name, cat, avg_comp, count in summary[:10]:
        print(f"  - {name:20s} ({sym:8s}) [{cat:6s}] | composite medio = {avg_comp:5.2f} | occorrenze = {count}")

    print()


# =========================================================
# ANALISI ORDERS_LOG
# =========================================================

def analyze_orders_log():
    rows = load_csv("orders_log.csv")
    if not rows:
        print("\n[orders_log] Nessun dato da analizzare.\n")
        return

    print("\n========== ANALISI orders_log.csv ==========\n")
    print(f"Numero totale di ordini proposti: {len(rows)}")

    # Conteggio LONG/SHORT
    side_counter = Counter()
    cat_counter = Counter()
    symbol_counter = Counter()

    for r in rows:
        side_counter[r.get("side", "UNKNOWN")] += 1
        cat_counter[r.get("category", "UNKNOWN")] += 1
        symbol_counter[r.get("symbol", "UNKNOWN")] += 1

    print("\nDistribuzione per side (LONG/SHORT):")
    for side, cnt in side_counter.items():
        print(f"  - {side:6s}: {cnt}")

    print("\nDistribuzione per categoria (CRYPTO/STOCK/ETF):")
    for cat, cnt in cat_counter.items():
        print(f"  - {cat:8s}: {cnt}")

    print("\nTop 10 asset per numero di ordini generati:")
    for sym, cnt in symbol_counter.most_common(10):
        print(f"  - {sym:10s}: {cnt} ordini")

    # Mostriamo anche gli ultimi 5 ordini
    print("\nUltimi 5 ordini generati:")
    for r in rows[-5:]:
        sym = r.get("symbol", "UNKNOWN")
        name = r.get("name", sym)
        cat = r.get("category", "UNKNOWN")
        side = r.get("side", "?")
        try:
            entry = float(r.get("entry", 0.0))
            sl = float(r.get("stop_loss", 0.0))
            tp = float(r.get("take_profit", 0.0))
            rr = float(r.get("reward_risk", 0.0))
            pos_size = float(r.get("position_size", 0.0))
            notional = float(r.get("notional", 0.0))
            risk_amount = float(r.get("risk_amount", 0.0))
        except Exception:
            entry = sl = tp = rr = pos_size = notional = risk_amount = 0.0

        print(
            f"  - {name} ({sym}) [{cat}] | {side} | "
            f"Entry={entry:.4f}, SL={sl:.4f}, TP={tp:.4f}, RR={rr:.2f} | "
            f"Qty={pos_size:.4f}, Notional={notional:.2f}, Risk={risk_amount:.2f}"
        )

# =========================================================
# MAIN
# =========================================================

def main():
    print("\n================ ANALISI COMPLESSIVA DEI LOG ================\n")
    analyze_signals_log()
    analyze_ranking_log()
    analyze_orders_log()
    print("\n====================== FINE REPORT ======================\n")


if __name__ == "__main__":
    main()
