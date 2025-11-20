# technical_agent.py
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import pandas as pd
import yfinance as yf


# ==============================
#  DOWNLOAD DATI
# ==============================

def download_data(symbol: str, period_days: int = 180, interval: str = "1d") -> pd.DataFrame:
    """
    Scarica dati OHLCV da Yahoo Finance per un singolo simbolo.
    Gestisce MultiIndex e assicura colonne standard.
    """
    period_str = f"{period_days}d"

    df = yf.download(
        symbol,
        period=period_str,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )

    if df.empty:
        return df

    # Caso: yfinance restituisce colonne MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    # Se abbiamo solo Adj Close → creiamo Close
    if "Adj Close" in df.columns and "Close" not in df.columns:
        df["Close"] = df["Adj Close"]

    needed = ["Open", "High", "Low", "Close", "Volume"]
    if "Volume" not in df.columns:
        df["Volume"] = 0.0

    available = [c for c in needed if c in df.columns]
    df = df[available].dropna()

    return df


# ==============================
#  INDICATORI TECNICI
# ==============================

def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    close = df["Close"].astype(float)

    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr


def _adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calcolo ADX con serie indicizzate come df.index per evitare mismatch.
    """
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    close = df["Close"].astype(float)

    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = pd.Series(0.0, index=df.index)
    minus_dm = pd.Series(0.0, index=df.index)

    plus_dm[(up_move > down_move) & (up_move > 0)] = up_move[(up_move > down_move) & (up_move > 0)]
    minus_dm[(down_move > up_move) & (down_move > 0)] = down_move[(down_move > up_move) & (down_move > 0)]

    tr = _atr(df, period=1)

    plus_di = 100 * plus_dm.rolling(period).sum() / tr.rolling(period).sum()
    minus_di = 100 * minus_dm.rolling(period).sum() / tr.rolling(period).sum()

    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).abs() * 100
    adx = dx.rolling(period).mean()
    return adx


def _ichimoku(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Ichimoku standard:
      - Tenkan-sen (9)
      - Kijun-sen (26)
      - Senkou Span A (shift +26)
      - Senkou Span B (52, shift +26)
      - Chikou Span (Close shift -26)
    """
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    close = df["Close"].astype(float)

    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
    chikou = close.shift(-26)

    return tenkan, kijun, senkou_a, senkou_b, chikou


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcola tutti gli indicatori necessari e ritorna un DataFrame
    con UNA riga per ogni candle, colonne:
      close, ema20, ema50, ema200, sma200, rsi14,
      macd, macd_signal, atr14, adx14,
      bb_lower, bb_upper,
      ichimoku_tenkan, ichimoku_kijun, ichimoku_span_a, ichimoku_span_b
    """
    if df.empty:
        return df

    close = df["Close"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)

    # RSI
    rsi14 = _rsi(close, 14)

    # Medie mobili
    ema20 = _ema(close, 20)
    ema50 = _ema(close, 50)
    ema200 = _ema(close, 200)
    sma200 = _sma(close, 200)

    # MACD
    ema12 = _ema(close, 12)
    ema26 = _ema(close, 26)
    macd = ema12 - ema26
    macd_signal = _ema(macd, 9)

    # ATR & ADX
    atr14 = _atr(df, 14)
    adx14 = _adx(df, 14)

    # Bollinger Bands (20, 2)
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb_mid + 2 * bb_std
    bb_lower = bb_mid - 2 * bb_std

    # Ichimoku
    tenkan, kijun, span_a, span_b, chikou = _ichimoku(df)

    out = pd.DataFrame(
        {
            "close": close,
            "ema20": ema20,
            "ema50": ema50,
            "ema200": ema200,
            "sma200": sma200,
            "rsi14": rsi14,
            "macd": macd,
            "macd_signal": macd_signal,
            "atr14": atr14,
            "adx14": adx14,
            "bb_lower": bb_lower,
            "bb_upper": bb_upper,
            "ichimoku_tenkan": tenkan,
            "ichimoku_kijun": kijun,
            "ichimoku_span_a": span_a,
            "ichimoku_span_b": span_b,
        },
        index=df.index,
    ).dropna()

    return out


# ==============================
#  SCORE & DECISIONE
# ==============================

def score_technical_indicators(ind_df: pd.DataFrame, style: str = "Swing") -> Tuple[int, List[str]]:
    last = ind_df.iloc[-1]
    score = 0
    reasons: List[str] = []

    close = last["close"]
    ema20 = last["ema20"]
    ema50 = last["ema50"]
    ema200 = last["ema200"]
    sma200 = last["sma200"]
    rsi14 = last["rsi14"]
    macd = last["macd"]
    macd_signal = last["macd_signal"]
    adx14 = last["adx14"]
    bb_lower = last["bb_lower"]
    bb_upper = last["bb_upper"]
    tenkan = last["ichimoku_tenkan"]
    kijun = last["ichimoku_kijun"]
    span_a = last["ichimoku_span_a"]
    span_b = last["ichimoku_span_b"]

    # RSI
    if rsi14 > 70:
        score -= 1
        reasons.append(f"RSI {rsi14:.1f} (ipercomprato).")
    elif rsi14 < 30:
        score += 1
        reasons.append(f"RSI {rsi14:.1f} (ipervenduto, possibile rimbalzo).")
    else:
        reasons.append(f"RSI {rsi14:.1f} (zona neutra).")

    # Trend breve con EMA20/EMA50
    if close > ema20 and close > ema50:
        score += 1
        reasons.append("Prezzo sopra EMA20 e EMA50 (trend breve positivo).")
    elif close < ema20 and close < ema50:
        score -= 1
        reasons.append("Prezzo sotto EMA20 e EMA50 (trend breve debole).")
    else:
        reasons.append("Prezzo misto rispetto a EMA20/EMA50 (trend incerto).")

    # Trend lungo con EMA200 / SMA200
    if close > ema200 and close > sma200:
        score += 2
        reasons.append("Prezzo sopra EMA200 e SMA200 (trend lungo positivo).")
    elif close < ema200 and close < sma200:
        score -= 2
        reasons.append("Prezzo sotto EMA200 e SMA200 (trend lungo debole).")
    else:
        reasons.append("Prezzo vicino a EMA200/SMA200 (zona di equilibrio di lungo periodo).")

    # MACD
    if macd > macd_signal:
        score += 1
        reasons.append("MACD sopra il segnale (momentum rialzista).")
    else:
        score -= 1
        reasons.append("MACD sotto il segnale (momentum ribassista).")

    # Bollinger
    if close < bb_lower:
        score += 1
        reasons.append("Prezzo vicino/sotto banda bassa di Bollinger (possibile rimbalzo).")
    elif close > bb_upper:
        score -= 1
        reasons.append("Prezzo vicino/sopra banda alta di Bollinger (possibile correzione).")

    # ADX solo come commento
    if adx14 < 20:
        reasons.append(f"ADX {adx14:.1f} (trend debole/laterale).")
    elif adx14 < 30:
        reasons.append(f"ADX {adx14:.1f} (trend moderato).")
    else:
        reasons.append(f"ADX {adx14:.1f} (trend forte).")

    # Ichimoku – nuvola
    cloud_top = max(span_a, span_b)
    cloud_bottom = min(span_a, span_b)

    if close > cloud_top:
        score += 1
        reasons.append("Prezzo sopra la nuvola Ichimoku (scenario rialzista).")
    elif close < cloud_bottom:
        score -= 1
        reasons.append("Prezzo sotto la nuvola Ichimoku (scenario ribassista).")
    else:
        reasons.append("Prezzo dentro la nuvola Ichimoku (zona di indecisione).")

    # Rapporto con Kijun
    if close > kijun:
        reasons.append("Prezzo sopra la Kijun-sen (supporto dinamico).")
    else:
        reasons.append("Prezzo sotto la Kijun-sen (resistenza dinamica).")

    return int(score), reasons


def decision_from_score(score: int) -> str:
    if score >= 6:
        return "STRONG BUY"
    if score >= 3:
        return "BUY"
    if score <= -6:
        return "STRONG SELL"
    if score <= -3:
        return "SELL"
    return "HOLD / WAIT"


# ==============================
#  AGENTE COMPLETO (usato da app & ensemble)
# ==============================

def run_technical_agent(
    symbol: str,
    style: str = "Swing",
    period: int = 180,
    interval: str = "1d",
    period_days: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Wrapper usato dalla web-app e dall'ensemble.
    Ritorna:
      - df: DataFrame con tutti gli indicatori
      - score: punteggio tecnico
      - decision: BUY / SELL / HOLD...
      - reasons: lista di stringhe
      - last_close: ultimo prezzo
      - atr14: ultimo ATR(14)
    """
    if period_days is not None:
        period = period_days

    df_raw = download_data(symbol, period_days=period, interval=interval)
    if df_raw.empty:
        raise ValueError(f"Nessun dato scaricato per {symbol} (periodo={period}d, interval={interval}).")

    ind_df = compute_indicators(df_raw)
    if ind_df.empty:
        raise ValueError("Dati insufficienti dopo il calcolo degli indicatori. Aumenta il periodo.")

    score, reasons = score_technical_indicators(ind_df, style=style)
    decision = decision_from_score(score)

    last = ind_df.iloc[-1]
    last_close = float(last["close"])
    atr14 = float(last["atr14"])

    return {
        "df": ind_df,
        "score": int(score),
        "decision": decision,
        "reasons": reasons,
        "last_close": last_close,
        "atr14": atr14,
    }


if __name__ == "__main__":
    # piccolo test manuale
    res = run_technical_agent("BTC-USD", style="Swing", period=365, interval="1d")
    print("TEST BTC-USD:", res["decision"], "score:", res["score"])
