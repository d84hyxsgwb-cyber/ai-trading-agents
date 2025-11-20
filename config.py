"""
config.py
Configurazione centrale per il motore AI di trading.
Qui puoi cambiare facilmente:
- dimensione conto
- rischio per trade
- peso della componente tecnica vs news
- soglie per considerare un segnale "forte"
"""

# === PARAMETRI DI CONTO / RISCHIO ===
# Dimensione teorica del conto (in USD o equivalente)
ACCOUNT_SIZE = 10000.0

# Quanto rischiare per singolo trade (in percentuale del conto)
# Es: 1.0 = 1% di ACCOUNT_SIZE
RISK_PER_TRADE_PCT = 1.0


# === PONDERAZIONE TECNICA vs NEWS ===
# Composite score = TechnicalScore * TECHNICAL_WEIGHT + NewsScoreScaled * NEWS_WEIGHT
TECHNICAL_WEIGHT = 0.7
NEWS_WEIGHT = 0.3

# Lo scaling delle news lo teniamo nel codice: da [-1,+1] a [-5,+5]


# === SOGLIE SEGNALI / ENSEMBLE ===
# Soglia di composite score oltre la quale consideriamo un segnale "forte"
# Es: 4.0 significa che sotto 4 in valore assoluto ignoriamo per order ideas
COMPOSITE_STRONG_SIGNAL = 4.0

# Soglia per considerare un segnale molto forte (non usata ancora, ma pronta)
COMPOSITE_VERY_STRONG_SIGNAL = 7.0
