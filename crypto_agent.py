# crypto_agent.py
# Agente tecnico dedicato alle CRYPTO

from typing import List
from technical_agent import run_technical_agent


# Lista di default se il file non esiste
DEFAULT_CRYPTO_SYMBOLS = [
    "BTC-USD",   # Bitcoin
    "ETH-USD",   # Ethereum
    "SOL-USD",   # Solana
    "BNB-USD",   # BNB
    "XRP-USD",   # XRP
    "ADA-USD",   # Cardano
    "AVAX-USD",  # Avalanche
    "DOGE-USD",  # Dogecoin
    "TRX-USD",   # Tron
    "TON-USD",   # Toncoin
    "LTC-USD",   # Litecoin
    "BCH-USD",   # Bitcoin Cash
    "LINK-USD",  # Chainlink
    "MATIC-USD", # Polygon
    "DOT-USD",   # Polkadot
    "ATOM-USD",  # Cosmos
    "XLM-USD",   # Stellar
    "XMR-USD",   # Monero
    "UNI-USD",   # Uniswap
    "APT-USD",   # Aptos
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

def analyze_cryptos(symbols: List[str] | None = None) -> None:
    if symbols is None:
        symbols = load_symbols_from_file("crypto_universe.txt", DEFAULT_CRYPTO_SYMBOLS)

    print("\n==============================")
    print("        SEZIONE: CRYPTO")
    print("==============================\n")

    for sym in symbols:
        print(f"\n>>> ANALISI CRYPTO: {sym}\n")
        try:
            run_technical_agent(symbol=sym)
        except Exception as e:
            print(f"[ERRORE] Impossibile analizzare {sym}: {e}")
        print("\n" + "-" * 40 + "\n")


if __name__ == "__main__":
    analyze_cryptos()
