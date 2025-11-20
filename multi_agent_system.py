# ============================
#   AI MULTI-AGENT SYSTEM
#   Versione didattica - 1 ciclo
# ============================

import threading
import queue
from datetime import datetime
import yfinance as yf
import random
from dataclasses import dataclass

# -----------------------------------
# DATACLASS PER I RISULTATI DEGLI AGENTI
# -----------------------------------

@dataclass
class MarketData:
    agent: str
    symbol: str
    price: float
    trend: str
    timestamp: str

@dataclass
class NewsData:
    agent: str
    symbol: str
    sentiment: str
    score: int
    timestamp: str

# -----------------------------------
# AGENTE DI MERCATO
# -----------------------------------

class MarketAgent(threading.Thread):
    def __init__(self, symbol, output_queue):
        super().__init__()
        self.symbol = symbol
        self.output_queue = output_queue

    def run(self):
        print(f"[MarketAgent] Acquisizione dati di mercato per {self.symbol}...")

        ticker = yf.Ticker(self.symbol)
        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            print(f"[MarketAgent] Nessun dato trovato per {self.symbol}")
            result = MarketData("MarketAgent", self.symbol, None, "unknown", self._now())
        else:
            last_close = data["Close"].iloc[-1]
            trend = self._compute_trend(data)
            result = MarketData("MarketAgent", self.symbol, float(last_close), trend, self._now())

        self.output_queue.put(result)
        print(f"[MarketAgent] Completato per {self.symbol}")

    def _compute_trend(self, df):
        if df["Close"].iloc[-1] > df["Close"].iloc[-5]:
            return "bullish"
        elif df["Close"].iloc[-1] < df["Close"].iloc[-5]:
            return "bearish"
        else:
            return "neutral"

    def _now(self):
        return datetime.utcnow().isoformat()


# -----------------------------------
# AGENTE DI NEWS / SENTIMENT
# -----------------------------------

class NewsAgent(threading.Thread):
    def __init__(self, symbol, output_queue):
        super().__init__()
        self.symbol = symbol
        self.output_queue = output_queue

    def run(self):
        print(f"[NewsAgent] Analisi sentiment per {self.symbol}...")

        sentiments = ["very_bullish", "bullish", "neutral", "bearish", "very_bearish"]
        sentiment = random.choice(sentiments)
        score = {
            "very_bullish": 2,
            "bullish": 1,
            "neutral": 0,
            "bearish": -1,
            "very_bearish": -2
        }[sentiment]

        result = NewsData("NewsAgent", self.symbol, sentiment, score, self._now())
        self.output_queue.put(result)

        print(f"[NewsAgent] Completato per {self.symbol}")

    def _now(self):
        return datetime.utcnow().isoformat()


# -----------------------------------
# MANAGER: COMBINA I RISULTATI
# -----------------------------------

class Manager:
    def __init__(self, symbols):
        self.symbols = symbols
        self.market_queue = queue.Queue()
        self.news_queue = queue.Queue()
        self.results = {}

    def run_cycle(self):
        print("\n==============================")
        print("    INIZIO CICLO DI ANALISI")
        print("==============================")

        # Avvia agenti
        market_agents = [MarketAgent(sym, self.market_queue) for sym in self.symbols]
        news_agents = [NewsAgent(sym, self.news_queue) for sym in self.symbols]

        for a in market_agents + news_agents:
            a.start()

        for a in market_agents + news_agents:
            a.join()

        # Recupera risultati
        for _ in self.symbols:
            market_data = self.market_queue.get()
            news_data = self.news_queue.get()
            self.results[market_data.symbol] = (market_data, news_data)

        self._make_decisions()

    # -----------------------------------
    # DECISION ENGINE
    # -----------------------------------
    def _make_decisions(self):
        print("\n=== RISULTATI FINALI ===")
        for sym, (mkt, news) in self.results.items():

            print(f"\n🔵 Asset: {sym}")
            print(f"   Prezzo: {mkt.price}")
            print(f"   Trend: {mkt.trend}")
            print(f"   Sentiment: {news.sentiment} ({news.score})")

            decision = self._decide(mkt, news)
            print(f"👉 Decisione finale: {decision}")

    def _decide(self, market: MarketData, news: NewsData):

        if market.price is None:
            return "WAIT (nessun dato di mercato)"

        if market.trend == "bullish" and news.score > 0:
            return "BUY"
        if market.trend == "bearish" and news.score < 0:
            return "SELL"

        return "HOLD"


# -----------------------------------
# MAIN
# -----------------------------------

def main():
    symbols = ["BTC-USD", "ETH-USD", "AAPL"]
    manager = Manager(symbols)
    manager.run_cycle()

if __name__ == "__main__":
    main()
