# news_agent.py
from __future__ import annotations

import os
from typing import Tuple, List

import requests
from textblob import TextBlob

# ======================================================
#  CONFIG: API KEY PER NEWSDATA
#  ------------------------------------------------------
#  Opzione 1: metti la tua API key qui direttamente:
#  NEWSDATA_API_KEY = "LA_TUA_API_KEY_NEWSDATA"
#
#  Opzione 2 (consigliata): metti la key nel file .env:
#     NEWSDATA_API_KEY=xxxxxxxx
#  e lasciala vuota qui: verrà letta da os.getenv.
# ======================================================

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "").strip()
if not NEWSDATA_API_KEY:
    # fallback: se vuoi, puoi inserire qui la key a mano
    NEWSDATA_API_KEY = "INSERISCI_LA_TUA_API_KEY_NEWSDATA"


def _fetch_news_newsdata(symbol: str, max_articles: int = 20) -> List[str]:
    """
    Recupera una lista di titoli news da NewsData per il simbolo dato.
    Restituisce una lista di stringhe (titoli).
    """
    if not NEWSDATA_API_KEY or NEWSDATA_API_KEY == "INSERISCI_LA_TUA_API_KEY_NEWSDATA":
        # Nessuna key configurata: niente errori, ma nessuna news.
        return []

    base_url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWSDATA_API_KEY,
        "q": symbol,
        "language": "en",
    }

    try:
        resp = requests.get(base_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[NewsData] ERRORE per {symbol}: {e}")
        return []

    results = data.get("results", []) or []
    titles: List[str] = []

    for art in results[:max_articles]:
        title = art.get("title") or ""
        if title:
            titles.append(title)

    return titles


def _sentiment_from_titles(titles: List[str]) -> float:
    """
    Calcola un sentiment medio (-3..+3) a partire dai titoli.
    Usa TextBlob per la polarità (-1..1), poi la scala a -3..+3.
    """
    if not titles:
        return 0.0

    scores = []
    for t in titles:
        try:
            polarity = TextBlob(t).sentiment.polarity  # -1 .. +1
            scores.append(polarity)
        except Exception:
            continue

    if not scores:
        return 0.0

    avg = float(sum(scores) / len(scores))  # -1..+1
    # scala a -3..+3 (compatibile con score tecnico)
    scaled = max(-3.0, min(3.0, avg * 3.0))
    return scaled


def get_sentiment_score(symbol: str) -> Tuple[float, List[str]]:
    """
    Funzione usata dal multi-agente.
    Ritorna:
      - news_score: float (circa da -3 a +3)
      - news_titles: lista di titoli usati per il calcolo
    In caso di errore o nessuna news, ritorna 0.0 e un messaggio di fallback.
    """
    titles = _fetch_news_newsdata(symbol)

    if not titles:
        return 0.0, ["Nessuna news trovata o API non configurata."]

    score = _sentiment_from_titles(titles)
    return score, titles[:5]  # limitiamo i titoli mostrati a 5 per non esagerare


if __name__ == "__main__":
    # piccolo test manuale
    s, ts = get_sentiment_score("AAPL")
    print("Score news AAPL:", s)
    for t in ts:
        print("-", t)
