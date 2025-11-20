# ensemble_manager.py
from typing import Dict, Any, List
import csv
from datetime import datetime

from assets_config import ALL_ASSETS
from technical_agent import run_technical_agent

TECH_WEIGHT = 1.0   # solo tecnica
NEWS_WEIGHT = 0.0   # news disattivate per ora


def analyze_one(asset: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analizza un singolo asset con sola analisi tecnica.
    Ritorna un dizionario con tutti i dettagli.
    Se i dati sono insufficienti, tech_score = 0 e decisione = 'N/A'.
    """
    symbol = asset["symbol"]
    name = asset.get("name", symbol)
    category = asset.get("category", "UNKNOWN")

    print(f">>> Analisi {symbol} [{category}]")

    tech_score = 0
    tech_decision = "N/A"
    tech_reasons: List[str] = []

    news_score: float = 0.0
    news_titles: List[str] = []

    try:
        # 365 giorni 1D per avere abbastanza barre per SMA200 / Ichimoku
        result = run_technical_agent(
            symbol=symbol,
            style="Position",
            period=365,
            interval="1d",
        )
        tech_score = result["score"]
        tech_decision = result["decision"]
        tech_reasons = result["reasons"]

    except Exception as e:
        print(f"[ERRORE tecnico] {symbol}: {e}")

    ensemble_score = TECH_WEIGHT * float(tech_score) + NEWS_WEIGHT * float(news_score)

    return {
        "symbol": symbol,
        "name": name,
        "category": category,
        "tech_score": int(tech_score),
        "tech_decision": tech_decision,
        "tech_reasons": tech_reasons,
        "news_score": float(news_score),
        "news_titles": news_titles,
        "ensemble_score": float(ensemble_score),
    }


def save_ranking_csv(results: List[Dict[str, Any]], filename: str = "ranking_log.csv") -> None:
    fieldnames = [
        "timestamp",
        "symbol",
        "name",
        "category",
        "tech_score",
        "news_score",
        "ensemble_score",
        "tech_decision",
    ]
    now_iso = datetime.utcnow().isoformat()

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(
                {
                    "timestamp": now_iso,
                    "symbol": r["symbol"],
                    "name": r["name"],
                    "category": r["category"],
                    "tech_score": r["tech_score"],
                    "news_score": r["news_score"],
                    "ensemble_score": r["ensemble_score"],
                    "tech_decision": r["tech_decision"],
                }
            )


def print_rankings(results: List[Dict[str, Any]]) -> None:
    buy_like = [r for r in results if r["tech_decision"] in ("BUY", "STRONG BUY")]
    sell_like = [r for r in results if r["tech_decision"] in ("SELL", "STRONG SELL")]

    buy_like = sorted(buy_like, key=lambda r: r["ensemble_score"], reverse=True)[:15]
    sell_like = sorted(sell_like, key=lambda r: r["ensemble_score"])[:15]

    print("\n=== CLASSIFICA FINALE (TOP 15 BUY / STRONG BUY) ===")
    for i, r in enumerate(buy_like, start=1):
        print(
            f"{i:2d}. {r['symbol']:<8} {r['category']:<20} "
            f"Ensemble={r['ensemble_score']:+.2f}  "
            f"Tech={r['tech_score']:+d}  "
            f"News={r['news_score']:+.2f}  "
            f"Decisione tecnica: {r['tech_decision']}"
        )

    print("\n=== CLASSIFICA FINALE (TOP 15 SELL / STRONG SELL) ===")
    for i, r in enumerate(sell_like, start=1):
        print(
            f"{i:2d}. {r['symbol']:<8} {r['category']:<20} "
            f"Ensemble={r['ensemble_score']:+.2f}  "
            f"Tech={r['tech_score']:+d}  "
            f"News={r['news_score']:+.2f}  "
            f"Decisione tecnica: {r['tech_decision']}"
        )


def main() -> None:
    print("=== ENSEMBLE AGENT: RANKING MULTI-ASSET ===")
    print("Stile di analisi: position\n")

    results: List[Dict[str, Any]] = []

    total = len(ALL_ASSETS)
    for idx, asset in enumerate(ALL_ASSETS, start=1):
        print(f"--- Asset {idx}/{total} ---")
        res = analyze_one(asset)
        results.append(res)

    save_ranking_csv(results)
    print_rankings(results)


if __name__ == "__main__":
    main()
