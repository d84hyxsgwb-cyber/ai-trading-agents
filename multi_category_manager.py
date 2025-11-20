# multi_category_manager.py
# Manager che lancia tutti gli agenti:
# - Crypto
# - Stocks
# - ETF
# - News sentiment

from crypto_agent import analyze_cryptos
from stocks_agent import analyze_stocks
from etf_agent import analyze_etfs
from news_agent import analyze_topic_print_news_report


def run_all() -> None:
    print("\n\n========== AI MULTI-ASSET DASHBOARD ==========\n")

    # ===== CRYPTO =====
    analyze_cryptos()

    # ===== STOCKS =====
    analyze_stocks()

    # ===== ETFS =====
    analyze_etfs()

    # ===== NEWS SUMMARY =====
    print("\n==============================")
    print("        SEZIONE: NEWS")
    print("==============================\n")

    topics = [
        "bitcoin price",
        "ethereum price",
        "apple stock",
        "nvidia stock",
        "S&P 500 ETF",
    ]

    for t in topics:
        analyze_topic_print_news_report(t)


if __name__ == "__main__":
    run_all()
