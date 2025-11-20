# etf_agent.py
# Agente tecnico dedicato agli ETF
from typing import List
from technical_agent import run_technical_agent

DEFAULT_ETF_SYMBOLS = [
    "SPY",   # S&P 500
    "VOO",   # S&P 500 (Vanguard)
    "QQQ",   # Nasdaq 100
    "VTI",   # Total US Market
    "IWM",   # Russell 2000
    "XLK",   # Tech sector
    "XLF",   # Financial sector
    "XLV",   # Health Care sector
]


def load_symbols_from_file(path: str, default_list: List[str]) -> List[str]:
    """
    Carica i ticker da un file di testo (uno per riga).

    - Ignora le righe vuote
    - Ignora le righe che iniziano con '#'
    - Gestisce i commenti in linea: es. "BTC-USD  # Bitcoin"
      -> prende solo "BTC-USD"
    """
    try:
        symbols: List[str] = []
        with open(path, "r") as f:
            for line in f:
                # rimuovi spazi iniziali/finali
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue

                # taglia il commento in linea
                if "#" in line:
                    line = line.split("#", 1)[0].strip()

                if not line:
                    continue

                # prendi solo il primo "pezzo" (nel caso ci siano spazi)
                symbol = line.split()[0].upper()

                if symbol:
                    symbols.append(symbol)

        if not symbols:
            return default_list
        return symbols

    except FileNotFoundError:
        return default_list

def analyze_etfs(symbols: List[str] | None = None) -> None:
    if symbols is None:
        symbols = load_symbols_from_file("etf_universe.txt", DEFAULT_ETF_SYMBOLS)

    print("\n==============================")
    print("        SEZIONE: ETFS")
    print("==============================\n")

    for sym in symbols:
        print(f"\n>>> ANALISI ETF: {sym}\n")
        try:
            run_technical_agent(symbol=sym)
        except Exception as e:
            print(f"[ERRORE] Impossibile analizzare {sym}: {e}")
        print("\n" + "-" * 40 + "\n")


if __name__ == "__main__":
    analyze_etfs()
