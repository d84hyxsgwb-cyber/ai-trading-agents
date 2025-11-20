# order_agent.py
# Crea proposte di ordine (long/short) a partire dall'analisi tecnica.

import os
import csv
from datetime import datetime
from typing import Optional, Dict

import config  # per ACCOUNT_SIZE e RISK_PER_TRADE_PCT

ORDER_LOG_FILE = "orders_log.csv"


def build_order_from_analysis(
    symbol: str,
    name: str,
    category: str,
    tech_analysis: Dict,
    composite_score: float,
) -> Optional[Dict]:
    """
    Crea una proposta di ordine a partire da:
      - analisi tecnica (output di analyze_for_manager)
      - composite score (tecnica + news)

    Ritorna un dict con:
      - side (LONG/SHORT)
      - entry, stop_loss, take_profit
      - reward_risk
      - position_size (numero di quote/coin)
      - notional (valore totale operazione)
      - reason_short

    oppure None se non c'è un segnale operativo chiaro.
    """

    score = tech_analysis["score"]
    decision = tech_analysis["decision"]
    ind = tech_analysis["indicators"]
    reasons = tech_analysis["reasons"]

    last_price = float(ind["last_price"])
    atr = float(ind["atr14"])

    # Se ATR è 0 o ridicolo, non possiamo definire SL sensato
    if atr <= 0 or last_price <= 0:
        return None

    # ===== Determina direzione (side) =====
    # usiamo sia la decisione tecnica sia il composite score
    if score >= 4 and composite_score >= 4:
        side = "LONG"
    elif score <= -4 and composite_score <= -4:
        side = "SHORT"
    else:
        return None  # segnale non abbastanza forte

    # ===== Fattore ATR diverso per categoria =====
    if category == "CRYPTO":
        atr_mult_sl = 2.5  # cripto più volatili
    elif category == "STOCK":
        atr_mult_sl = 1.8
    else:  # ETF
        atr_mult_sl = 1.5

    sl_distance = atr * atr_mult_sl

    # ===== Reward:Risk =====
    reward_risk = 2.0  # 2:1 di default

    if side == "LONG":
        entry = last_price
        stop_loss = entry - sl_distance
        take_profit = entry + sl_distance * reward_risk
    else:  # SHORT
        entry = last_price
        stop_loss = entry + sl_distance
        take_profit = entry - sl_distance * reward_risk

    # Non ha senso se SL o TP diventano negativi
    if stop_loss <= 0 or take_profit <= 0:
        return None

    # ===== POSITION SIZING (in base a config) =====
    # Quanto siamo disposti a perdere su questo trade
    risk_amount = config.ACCOUNT_SIZE * (config.RISK_PER_TRADE_PCT / 100.0)

    # Distanza assoluta entry-SL
    distance_to_sl = abs(entry - stop_loss)
    if distance_to_sl <= 0:
        return None

    # Quante unità (azioni/coin/quote) comprare/vendere
    position_size = risk_amount / distance_to_sl

    # Notional = valore totale del trade
    notional = position_size * entry

    # Motivo breve (prendiamo la prima motivazione tecnica)
    reason_short = reasons[0] if reasons else f"Decisione tecnica: {decision}"

    order = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "name": name,
        "category": category,
        "side": side,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "reward_risk": reward_risk,
        "technical_score": score,
        "technical_decision": decision,
        "composite_score": composite_score,
        "atr14": atr,
        "position_size": position_size,
        "notional": notional,
        "risk_amount": risk_amount,
        "reason_short": reason_short,
    }

    # Log su CSV
    _log_order(order)

    return order


def _log_order(order: Dict, log_file: str = ORDER_LOG_FILE) -> None:
    """
    Logga l'idea di ordine su CSV per storico/backtest.
    """
    fieldnames = [
        "timestamp",
        "symbol",
        "name",
        "category",
        "side",
        "entry",
        "stop_loss",
        "take_profit",
        "reward_risk",
        "technical_score",
        "technical_decision",
        "composite_score",
        "atr14",
        "position_size",
        "notional",
        "risk_amount",
        "reason_short",
    ]

    file_exists = os.path.isfile(log_file)
    with open(log_file, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(order)
