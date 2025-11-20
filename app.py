# app.py
# Dashboard Streamlit:
#  - Classifica multi-agente da ranking_log.csv
#  - Setup su singolo asset con grafico, indicatori, lotto e paper trading

import os
from typing import Tuple

import numpy as np
import pandas as pd
import streamlit as st

from technical_agent import run_technical_agent
from paper_trading import open_trade, update_trades_with_price, load_trades


# ============================================================
# Helpers rischio / money management
# ============================================================

def compute_sl_tp(
    last_close: float,
    atr: float,
    direction: str,
    style: str,
) -> Tuple[float, float, float]:
    direction = direction.upper()
    style = style.lower()

    if style == "scalping":
        m_sl, m_tp = 1.0, 1.5
    elif style == "position":
        m_sl, m_tp = 2.0, 4.0
    else:  # swing / intraday
        m_sl, m_tp = 1.5, 3.0

    entry = last_close

    if direction == "LONG":
        stop = last_close - m_sl * atr
        take_profit = last_close + m_tp * atr
    else:
        stop = last_close + m_sl * atr
        take_profit = last_close - m_tp * atr

    return float(entry), float(stop), float(take_profit)


def compute_position_size(
    capital: float,
    risk_pct: float,
    entry: float,
    stop: float,
    take_profit: float,
    leverage: float,
    direction: str,
) -> dict:
    direction = direction.upper()
    risk_amount = capital * (risk_pct / 100.0)

    if direction == "LONG":
        per_unit_loss = entry - stop
        per_unit_gain = take_profit - entry
    else:
        per_unit_loss = stop - entry
        per_unit_gain = entry - take_profit

    per_unit_loss = abs(per_unit_loss)
    per_unit_gain = max(per_unit_gain, 0.0)

    if per_unit_loss <= 0:
        return {
            "size": 0.0,
            "risk_amount": float(risk_amount),
            "risk_pct": float(risk_pct),
            "gain_amount": 0.0,
            "gain_pct": 0.0,
            "margin_required": 0.0,
        }

    size = risk_amount / per_unit_loss
    margin_required = (entry * size / leverage) if leverage > 0 else 0.0
    gain_amount = per_unit_gain * size
    gain_pct = (gain_amount / capital * 100.0) if capital > 0 else 0.0

    return {
        "size": float(size),
        "risk_amount": float(risk_amount),
        "risk_pct": float(risk_pct),
        "gain_amount": float(gain_amount),
        "gain_pct": float(gain_pct),
        "margin_required": float(margin_required),
    }


# ============================================================
# Config Streamlit
# ============================================================

st.set_page_config(
    page_title="AI Trading Dashboard",
    layout="wide",
)

st.title("🤖 AI Trading Dashboard")
st.caption(
    "In alto: classifica multi-agente (TOP 15 BUY / SELL). "
    "Sotto: setup su singolo asset con grafico, indicatori, lotto e paper trading virtuale."
)

# ============================================================
# 1) CLASSIFICA MULTI-AGENTE
# ============================================================

ranking_full = None
ranking_path = os.path.join(os.getcwd(), "ranking_log.csv")

if os.path.exists(ranking_path):
    try:
        tmp = pd.read_csv(ranking_path)
        if not tmp.empty:
            ranking_full = tmp
    except Exception as e:
        st.warning(f"Impossibile leggere ranking_log.csv: {e}")

if ranking_full is None:
    st.info(
        "Nessuna classifica disponibile. Esegui il multi-agente "
        "(`python3 ensemble_manager.py`) per generare **ranking_log.csv**."
    )
else:
    st.subheader("🏆 Classifica Multi-Agente (TOP 15 BUY / TOP 15 SELL)")

    df_rank = ranking_full.copy()

    # filtro categoria (Crypto / Stocks / ETF ...)
    category_col = None
    for c in df_rank.columns:
        if "category" in c.lower():
            category_col = c
            break

    if category_col is not None:
        categories = ["Tutti"] + sorted(
            str(x) for x in df_rank[category_col].dropna().unique().tolist()
        )
        sel_cat = st.selectbox(
            "Filtro categoria (Crypto / Stocks / ETF / ...)", categories, index=0
        )
        if sel_cat != "Tutti":
            df_rank = df_rank[df_rank[category_col].astype(str) == sel_cat]

    ensemble_col = None
    for c in df_rank.columns:
        if "ensemble" in c.lower() and "score" in c.lower():
            ensemble_col = c
            break

    decision_col = None
    for c in df_rank.columns:
        if "decision" in c.lower():
            decision_col = c
            break

    if ensemble_col is None:
        st.info(
            "Nel file ranking_log.csv non è stata trovata una colonna 'ensemble_score'. "
            "Mostro il contenuto grezzo."
        )
        st.dataframe(df_rank.head(50), use_container_width=True)
    else:
        df_rank = df_rank.sort_values(ensemble_col, ascending=False)

        if decision_col is not None:
            decisions = df_rank[decision_col].astype(str).str.upper()
            buy_mask = decisions.isin(["BUY", "STRONG BUY"])
            sell_mask = decisions.isin(["SELL", "STRONG SELL"])
        else:
            buy_mask = df_rank[ensemble_col] > 0
            sell_mask = df_rank[ensemble_col] < 0

        top_buy = df_rank[buy_mask].head(15)
        top_sell = (
            df_rank[sell_mask]
            .sort_values(ensemble_col, ascending=True)
            .head(15)
        )

        col_buy, col_sell = st.columns(2)
        with col_buy:
            st.markdown("### 📈 Top 15 BUY / STRONG BUY")
            st.dataframe(top_buy, use_container_width=True)
        with col_sell:
            st.markdown("### 📉 Top 15 SELL / STRONG SELL")
            st.dataframe(top_sell, use_container_width=True)

st.markdown("---")

# ============================================================
# 2) SETUP SU SINGOLO ASSET
#    Grafico a sinistra, filtri a destra
# ============================================================

st.subheader("🧮 AI Trading Setup su singolo asset")

left_panel, right_panel = st.columns([2, 1])

# ---------------- FILTRI A DESTRA -----------------
with right_panel:
    st.markdown("### 🎛 Filtri & parametri")

    ticker = st.text_input(
        "Ticker (Yahoo Finance, es: BTC-USD, AAPL, SPY)",
        value="BTC-USD",
    ).strip()

    direction = st.selectbox("Direzione (side)", ["LONG", "SHORT"])
    style = st.selectbox("Stile di trading", ["Scalping", "Swing", "Position"])

    st.markdown("#### 💰 Rischio & lotto")

    capital = st.number_input(
        "Capitale disponibile",
        min_value=0.0,
        value=10_000.0,
        step=100.0,
        format="%.2f",
    )

    risk_pct = st.slider("Rischio per trade (% del capitale)", 0.1, 5.0, 1.0, 0.1)
    leverage = st.slider("Leva (x)", 1.0, 30.0, 5.0, 0.5)

    lot_input = st.number_input(
        "Lotto effettivo (MT5 / contratti)",
        min_value=0.01,
        value=0.50,
        step=0.01,
        format="%.2f",
    )

    st.markdown("#### 📅 Storico & timeframe")

    period_label = st.selectbox(
        "Storico da analizzare",
        ["30d", "90d", "180d", "365d"],
        index=2,
    )
    period_days = int(period_label.replace("d", ""))

    tf_label = st.selectbox(
        "Timeframe (interval)",
        ["1h", "4h", "1d"],
        index=0,
    )
    interval = tf_label

    # solo estetico: il calcolo viene comunque eseguito sempre
    st.button("🚀 Calcola / aggiorna setup")

# ---------------- CALCOLO SETUP -----------------

with left_panel:
    try:
        result = run_technical_agent(
            symbol=ticker,
            style=style,
            period=period_days,
            interval=interval,
        )
    except Exception as e:
        st.error(f"Errore durante l'esecuzione dell'agente tecnico: {e}")
        st.stop()

    df = result["df"]
    score = result["score"]
    decision = result["decision"]
    reasons = result["reasons"]
    last_close = float(result["last_close"])
    atr14 = float(result["atr14"])

    entry, stop_loss, take_profit = compute_sl_tp(
        last_close=last_close,
        atr=atr14,
        direction=direction,
        style=style,
    )

    mm = compute_position_size(
        capital=capital,
        risk_pct=risk_pct,
        entry=entry,
        stop=stop_loss,
        take_profit=take_profit,
        leverage=leverage,
        direction=direction,
    )

    # Perdita/guadagno sul lotto scelto
    if direction.upper() == "LONG":
        per_unit_loss = entry - stop_loss
        per_unit_gain = take_profit - entry
    else:
        per_unit_loss = stop_loss - entry
        per_unit_gain = entry - take_profit

    per_unit_loss = abs(per_unit_loss)
    per_unit_gain = max(per_unit_gain, 0.0)

    user_risk_amount = per_unit_loss * lot_input
    user_gain_amount = per_unit_gain * lot_input
    user_risk_pct = (user_risk_amount / capital * 100.0) if capital > 0 else 0.0
    user_gain_pct = (user_gain_amount / capital * 100.0) if capital > 0 else 0.0

    # aggiorna P/L dei trade virtuali su questo simbolo
    update_trades_with_price(ticker, last_close, capital)

    # Messaggio di conferma
    st.success(
        f"Setup calcolato per **{ticker}** – {direction}, stile **{style}**, "
        f"periodo {period_days} giorni, timeframe {interval}."
    )

    # ---------------- Grafico sopra a tutto ----------------
    st.markdown("### 📈 Grafico prezzo & medie mobili")
    try:
        chart_df = df[["close", "ema20", "ema50", "ema200", "sma200"]].copy()
        chart_df = chart_df.rename(
            columns={
                "close": "Close",
                "ema20": "EMA20",
                "ema50": "EMA50",
                "ema200": "EMA200",
                "sma200": "SMA200",
            }
        )
        st.line_chart(chart_df, use_container_width=True)
    except Exception as e:
        st.error(f"Errore nel grafico: {e}")

    # ---------------- Livelli & margini sotto il grafico ----------------
    st.markdown("### 💰 Livelli operativi & margini")

    col_levels, col_mm = st.columns(2)

    with col_levels:
        st.subheader("Livelli")
        st.metric("Entry", f"{entry:,.6f}")
        st.metric("Stop Loss", f"{stop_loss:,.6f}")
        st.metric("Take Profit", f"{take_profit:,.6f}")
        st.metric("ATR(14)", f"{atr14:,.6f}")

    with col_mm:
        st.subheader("Rischio teorico (lotto consigliato)")
        st.metric("Capitale", f"{capital:,.2f}")
        st.metric("Rischio per trade", f"{mm['risk_pct']:.2f}% (~ {mm['risk_amount']:.2f})")
        st.metric("Lotto teorico", f"{mm['size']:.4f}")
        st.metric("Margine stimato", f"{mm['margin_required']:.2f}")
        st.metric(
            "Guadagno potenziale teorico",
            f"{mm['gain_amount']:.2f} ({mm['gain_pct']:.2f}% del capitale)",
        )

# ============================================================
# 3) QUATTRO RIQUADRI (2x2) SOTTO IL GRAFICO
# ============================================================

st.markdown("---")
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# --- Box 1: indicatori tecnici ---
with row1_col1:
    st.subheader("📊 Indicatori tecnici (ultima candela)")
    last_row = df.iloc[-1]
    ind_table = pd.DataFrame(
        {
            "Valore": {
                "Close": last_row["close"],
                "RSI14": last_row["rsi14"],
                "EMA20": last_row["ema20"],
                "EMA50": last_row["ema50"],
                "EMA200": last_row["ema200"],
                "SMA200": last_row["sma200"],
                "MACD": last_row["macd"],
                "MACD signal": last_row["macd_signal"],
                "ATR14": last_row["atr14"],
                "ADX14": last_row["adx14"],
                "Ichimoku Tenkan": last_row.get("ichimoku_tenkan", np.nan),
                "Ichimoku Kijun": last_row.get("ichimoku_kijun", np.nan),
            }
        }
    )
    st.table(ind_table)

# --- Box 2: estratto ranking per questo asset ---
with row1_col2:
    st.subheader("🏅 Estratto classifica per questo asset")
    if ranking_full is not None:
        sym_col = None
        for c in ranking_full.columns:
            if c.lower() in ["symbol", "ticker", "asset", "name"]:
                sym_col = c
                break
        if sym_col is not None:
            sub = ranking_full[ranking_full[sym_col].astype(str).str.upper() == ticker.upper()]
            if sub.empty:
                st.info("Questo asset non è presente in ranking_log.csv.")
            else:
                st.dataframe(sub, use_container_width=True)
        else:
            st.info("Nel ranking non è presente una colonna simbolo riconoscibile.")
    else:
        st.info("Ranking non disponibile (ranking_log.csv mancante).")

# --- Box 3: consiglio IA ---
with row2_col1:
    st.subheader("🧠 Consiglio dell'agente tecnico")
    style_txt = style.capitalize()
    st.write(
        f"Stile: **{style_txt}**, direzione: **{direction}**, "
        f"rischio: **{risk_pct:.2f}%** del capitale."
    )
    st.write(
        f"Decisione complessiva: **{decision}** "
        f"(punteggio tecnico = {score})."
    )
    with st.expander("Mostra motivazioni tecniche dettagliate"):
        for r in reasons:
            st.markdown(f"- {r}")

# --- Box 4: riepilogo trade sul lotto effettivo + bottone paper trading ---
with row2_col2:
    st.subheader("📌 Riepilogo trade (lotto effettivo)")

    st.markdown(
        f"- **Entry price:** `{entry:.6f}`\n"
        f"- **Stop Loss:** `{stop_loss:.6f}`\n"
        f"- **Take Profit:** `{take_profit:.6f}`\n"
        f"- **Lotto effettivo:** `{lot_input:.2f}`"
    )

    st.markdown("#### Rischio / profitto sul lotto inserito")
    st.metric("Perdita potenziale", f"{user_risk_amount:.2f} ({user_risk_pct:.2f}%)")
    st.metric("Profitto potenziale", f"{user_gain_amount:.2f} ({user_gain_pct:.2f}%)")

    if st.button("✅ Apri trade virtuale con questi parametri"):
        trade = open_trade(
            symbol=ticker,
            side=direction,
            style=style,
            lot=float(lot_input),
            entry=float(entry),
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
            capital=float(capital),
        )
        st.success(f"Trade virtuale aperto (ID {trade['id']})")

# ============================================================
# 4) SEZIONE PAPER TRADING
# ============================================================

st.markdown("---")
st.subheader("💸 Paper trading (account virtuale)")

trades_df = load_trades()
if trades_df.empty:
    st.info("Nessun trade virtuale ancora aperto. Usa il bottone **Apri trade virtuale** sopra.")
else:
    cur = trades_df[trades_df["symbol"].astype(str).str.upper() == ticker.upper()]

    open_trades = cur[cur["status"] == "OPEN"]
    closed_trades = cur[cur["status"] == "CLOSED"]

    st.markdown("### Operazioni aperte su questo asset")
    if open_trades.empty:
        st.write("Nessuna operazione aperta su questo simbolo.")
    else:
        st.dataframe(open_trades, use_container_width=True)

    st.markdown("### Operazioni chiuse su questo asset")
    if closed_trades.empty:
        st.write("Nessuna operazione chiusa su questo simbolo.")
    else:
        st.dataframe(closed_trades, use_container_width=True)
