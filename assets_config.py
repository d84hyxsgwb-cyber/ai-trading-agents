#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
assets_config.py
----------------
Definisce l'universo di asset analizzati dagli agenti.

Struttura:
- CRYPTO_ASSETS: principali crypto (majors, L2, DeFi, meme, niche)
- STOCK_ASSETS : azioni large / mega cap divise per settore
- ETF_ASSETS   : ETF index, sector, bonds, commodity, thematic, country, niche

Ogni asset è un dict con:
- symbol   : ticker Yahoo Finance
- name     : descrizione leggibile
- category : macro-categoria logica (usata anche nel backtest)
"""

# ============================
#  CRYPTO ASSETS
# ============================

CRYPTO_ASSETS = [
    # ---- MAJORS / BLUE CHIP ----
    {"symbol": "BTC-USD", "name": "Bitcoin",                "category": "CRYPTO/MAJOR"},
    {"symbol": "ETH-USD", "name": "Ethereum",               "category": "CRYPTO/MAJOR"},
    {"symbol": "BNB-USD", "name": "BNB",                    "category": "CRYPTO/MAJOR"},
    {"symbol": "SOL-USD", "name": "Solana",                 "category": "CRYPTO/MAJOR"},
    {"symbol": "XRP-USD", "name": "XRP",                    "category": "CRYPTO/MAJOR"},
    {"symbol": "ADA-USD", "name": "Cardano",                "category": "CRYPTO/MAJOR"},
    {"symbol": "DOGE-USD","name": "Dogecoin",               "category": "CRYPTO/MAJOR"},
    {"symbol": "AVAX-USD","name": "Avalanche",              "category": "CRYPTO/MAJOR"},
    {"symbol": "DOT-USD", "name": "Polkadot",               "category": "CRYPTO/MAJOR"},
    {"symbol": "LTC-USD", "name": "Litecoin",               "category": "CRYPTO/MAJOR"},
    {"symbol": "BCH-USD", "name": "Bitcoin Cash",           "category": "CRYPTO/MAJOR"},

    # ---- LAYER 2 / SCALING ----
    {"symbol": "MATIC-USD","name": "Polygon",               "category": "CRYPTO/L2"},
    {"symbol": "OP-USD",   "name": "Optimism",              "category": "CRYPTO/L2"},
    {"symbol": "ARB-USD",  "name": "Arbitrum",              "category": "CRYPTO/L2"},
    {"symbol": "IMX-USD",  "name": "Immutable X",           "category": "CRYPTO/L2"},
    {"symbol": "STX-USD",  "name": "Stacks",                "category": "CRYPTO/L2"},

    # ---- DEFI / DEX / LENDING ----
    {"symbol": "UNI-USD",  "name": "Uniswap",               "category": "CRYPTO/DEFI"},
    {"symbol": "AAVE-USD", "name": "Aave",                  "category": "CRYPTO/DEFI"},
    {"symbol": "MKR-USD",  "name": "Maker",                 "category": "CRYPTO/DEFI"},
    {"symbol": "SNX-USD",  "name": "Synthetix",             "category": "CRYPTO/DEFI"},
    {"symbol": "CAKE-USD", "name": "PancakeSwap",           "category": "CRYPTO/DEFI"},
    {"symbol": "LDO-USD",  "name": "Lido DAO",              "category": "CRYPTO/DEFI"},
    {"symbol": "CRV-USD",  "name": "Curve DAO",             "category": "CRYPTO/DEFI"},

    # ---- INFRA / ORACLES / AI ----
    {"symbol": "LINK-USD", "name": "Chainlink",             "category": "CRYPTO/INFRA"},
    {"symbol": "ATOM-USD", "name": "Cosmos",                "category": "CRYPTO/INFRA"},
    {"symbol": "APT-USD",  "name": "Aptos",                 "category": "CRYPTO/INFRA"},
    {"symbol": "NEAR-USD", "name": "NEAR Protocol",         "category": "CRYPTO/INFRA"},
    {"symbol": "GRT-USD",  "name": "The Graph",             "category": "CRYPTO/INFRA"},
    {"symbol": "INJ-USD",  "name": "Injective",             "category": "CRYPTO/INFRA"},
    {"symbol": "FET-USD",  "name": "Fetch.ai",              "category": "CRYPTO/AI"},
    {"symbol": "RNDR-USD", "name": "Render",                "category": "CRYPTO/AI"},
    {"symbol": "AGIX-USD", "name": "SingularityNET",        "category": "CRYPTO/AI"},

    # ---- STABLECOINS (per contesto di mercato) ----
    {"symbol": "USDT-USD", "name": "Tether",                "category": "CRYPTO/STABLE"},
    {"symbol": "USDC-USD", "name": "USD Coin",              "category": "CRYPTO/STABLE"},
    {"symbol": "DAI-USD",  "name": "DAI",                   "category": "CRYPTO/STABLE"},

    # ---- MEME / HIGH-RISK / NICHE ----
    {"symbol": "SHIB-USD", "name": "Shiba Inu",             "category": "CRYPTO/MEME"},
    {"symbol": "PEPE-USD", "name": "Pepe",                  "category": "CRYPTO/MEME"},
    {"symbol": "FLOKI-USD","name": "Floki",                 "category": "CRYPTO/MEME"},
    {"symbol": "BONK-USD", "name": "Bonk",                  "category": "CRYPTO/MEME"},
]


# ============================
#  STOCK ASSETS
# ============================

STOCK_ASSETS = [
    # ---- MEGA TECH / GROWTH ----
    {"symbol": "AAPL",  "name": "Apple",                    "category": "STOCK/TECH_MEGA"},
    {"symbol": "MSFT",  "name": "Microsoft",                "category": "STOCK/TECH_MEGA"},
    {"symbol": "GOOGL", "name": "Alphabet (Google)",        "category": "STOCK/TECH_MEGA"},
    {"symbol": "GOOG",  "name": "Alphabet (C)",             "category": "STOCK/TECH_MEGA"},
    {"symbol": "AMZN",  "name": "Amazon",                   "category": "STOCK/TECH_MEGA"},
    {"symbol": "META",  "name": "Meta Platforms",           "category": "STOCK/TECH_MEGA"},
    {"symbol": "NVDA",  "name": "NVIDIA",                   "category": "STOCK/TECH_MEGA"},
    {"symbol": "TSLA",  "name": "Tesla",                    "category": "STOCK/TECH_GROWTH"},
    {"symbol": "AMD",   "name": "Advanced Micro Devices",   "category": "STOCK/TECH_SEMI"},
    {"symbol": "INTC",  "name": "Intel",                    "category": "STOCK/TECH_SEMI"},

    # ---- SOFTWARE / CLOUD / SAAS ----
    {"symbol": "ORCL",  "name": "Oracle",                   "category": "STOCK/TECH_SOFTWARE"},
    {"symbol": "CRM",   "name": "Salesforce",               "category": "STOCK/TECH_SOFTWARE"},
    {"symbol": "ADBE",  "name": "Adobe",                    "category": "STOCK/TECH_SOFTWARE"},
    {"symbol": "SAP",   "name": "SAP SE",                   "category": "STOCK/TECH_SOFTWARE"},
    {"symbol": "NOW",   "name": "ServiceNow",               "category": "STOCK/TECH_SOFTWARE"},

    # ---- HEALTHCARE / PHARMA ----
    {"symbol": "JNJ",   "name": "Johnson & Johnson",        "category": "STOCK/HEALTHCARE"},
    {"symbol": "LLY",   "name": "Eli Lilly",                "category": "STOCK/HEALTHCARE"},
    {"symbol": "MRK",   "name": "Merck & Co.",              "category": "STOCK/HEALTHCARE"},
    {"symbol": "PFE",   "name": "Pfizer",                   "category": "STOCK/HEALTHCARE"},
    {"symbol": "UNH",   "name": "UnitedHealth Group",       "category": "STOCK/HEALTHCARE"},

    # ---- FINANCIALS / PAYMENT ----
    {"symbol": "JPM",   "name": "JPMorgan Chase",           "category": "STOCK/FINANCIALS"},
    {"symbol": "BAC",   "name": "Bank of America",          "category": "STOCK/FINANCIALS"},
    {"symbol": "GS",    "name": "Goldman Sachs",            "category": "STOCK/FINANCIALS"},
    {"symbol": "MS",    "name": "Morgan Stanley",           "category": "STOCK/FINANCIALS"},
    {"symbol": "V",     "name": "Visa",                     "category": "STOCK/PAYMENTS"},
    {"symbol": "MA",    "name": "Mastercard",               "category": "STOCK/PAYMENTS"},

    # ---- ENERGY / OIL & GAS ----
    {"symbol": "XOM",   "name": "Exxon Mobil",              "category": "STOCK/ENERGY"},
    {"symbol": "CVX",   "name": "Chevron",                  "category": "STOCK/ENERGY"},
    {"symbol": "BP",    "name": "BP plc",                   "category": "STOCK/ENERGY"},
    {"symbol": "SHEL",  "name": "Shell plc",                "category": "STOCK/ENERGY"},

    # ---- INDUSTRIALS / DEFENSE ----
    {"symbol": "CAT",   "name": "Caterpillar",              "category": "STOCK/INDUSTRIALS"},
    {"symbol": "BA",    "name": "Boeing",                   "category": "STOCK/INDUSTRIALS"},
    {"symbol": "GE",    "name": "General Electric",         "category": "STOCK/INDUSTRIALS"},
    {"symbol": "DE",    "name": "Deere & Co.",              "category": "STOCK/INDUSTRIALS"},
    {"symbol": "LMT",   "name": "Lockheed Martin",          "category": "STOCK/DEFENSE"},
    {"symbol": "NOC",   "name": "Northrop Grumman",         "category": "STOCK/DEFENSE"},
    {"symbol": "RTX",   "name": "RTX (Raytheon)",           "category": "STOCK/DEFENSE"},

    # ---- CONSUMER STAPLES / BEVERAGES ----
    {"symbol": "KO",    "name": "Coca-Cola",                "category": "STOCK/CONSUMER_STAPLES"},
    {"symbol": "PEP",   "name": "PepsiCo",                  "category": "STOCK/CONSUMER_STAPLES"},
    {"symbol": "PG",    "name": "Procter & Gamble",         "category": "STOCK/CONSUMER_STAPLES"},
    {"symbol": "WMT",   "name": "Walmart",                  "category": "STOCK/CONSUMER_STAPLES"},

    # ---- CONSUMER DISCRETIONARY / E-COMMERCE / LUXURY ----
    {"symbol": "MCD",   "name": "McDonald's",               "category": "STOCK/CONSUMER_DISC"},
    {"symbol": "NKE",   "name": "Nike",                     "category": "STOCK/CONSUMER_DISC"},
    {"symbol": "HD",    "name": "Home Depot",               "category": "STOCK/CONSUMER_DISC"},
    {"symbol": "COST",  "name": "Costco",                   "category": "STOCK/CONSUMER_DISC"},
    {"symbol": "TGT",   "name": "Target",                   "category": "STOCK/CONSUMER_DISC"},
    {"symbol": "SHOP",  "name": "Shopify",                  "category": "STOCK/NICHE_ECOMMERCE"},

    # ---- COMMUNICATION / MEDIA ----
    {"symbol": "DIS",   "name": "Walt Disney",              "category": "STOCK/COMMUNICATION"},
    {"symbol": "NFLX",  "name": "Netflix",                  "category": "STOCK/COMMUNICATION"},
    {"symbol": "T",     "name": "AT&T",                     "category": "STOCK/COMMUNICATION"},
    {"symbol": "VZ",    "name": "Verizon",                  "category": "STOCK/COMMUNICATION"},

    # ---- NICHE / GROWTH SPECIALE ----
    {"symbol": "PLTR",  "name": "Palantir",                 "category": "STOCK/NICHE_DATA"},
    {"symbol": "SNOW",  "name": "Snowflake",                "category": "STOCK/NICHE_DATA"},
    {"symbol": "RBLX",  "name": "Roblox",                   "category": "STOCK/NICHE_GAMING"},
]


# ============================
#  ETF ASSETS
# ============================

ETF_ASSETS = [
    # ---- BROAD INDEX US ----
    {"symbol": "SPY",   "name": "S&P 500 ETF",              "category": "ETF/INDEX_US"},
    {"symbol": "VOO",   "name": "Vanguard S&P 500",         "category": "ETF/INDEX_US"},
    {"symbol": "IVV",   "name": "iShares S&P 500",          "category": "ETF/INDEX_US"},
    {"symbol": "VTI",   "name": "Vanguard Total Market",    "category": "ETF/INDEX_US"},
    {"symbol": "QQQ",   "name": "NASDAQ 100 ETF",           "category": "ETF/INDEX_GROWTH"},
    {"symbol": "DIA",   "name": "Dow Jones ETF",            "category": "ETF/INDEX_US"},
    {"symbol": "IWM",   "name": "Russell 2000 ETF",         "category": "ETF/INDEX_US_SMALL"},

    # ---- SECTOR SPDR ----
    {"symbol": "XLK",   "name": "Technology Select",        "category": "ETF/SECTOR_TECH"},
    {"symbol": "XLF",   "name": "Financials Select",        "category": "ETF/SECTOR_FINANCIALS"},
    {"symbol": "XLE",   "name": "Energy Select",            "category": "ETF/SECTOR_ENERGY"},
    {"symbol": "XLI",   "name": "Industrials Select",       "category": "ETF/SECTOR_INDUSTRIALS"},
    {"symbol": "XLV",   "name": "Health Care Select",       "category": "ETF/SECTOR_HEALTH"},
    {"symbol": "XLY",   "name": "Consumer Discretionary",   "category": "ETF/SECTOR_CONSUMER"},
    {"symbol": "XLP",   "name": "Consumer Staples",         "category": "ETF/SECTOR_CONSUMER"},
    {"symbol": "XLU",   "name": "Utilities",                "category": "ETF/SECTOR_UTILITIES"},
    {"symbol": "XLB",   "name": "Materials",                "category": "ETF/SECTOR_MATERIALS"},
    {"symbol": "XLC",   "name": "Communication Services",   "category": "ETF/SECTOR_COMM"},

    # ---- BONDS / FIXED INCOME ----
    {"symbol": "TLT",   "name": "20+ Year Treasuries",      "category": "ETF/BONDS"},
    {"symbol": "IEF",   "name": "7-10 Year Treasuries",     "category": "ETF/BONDS"},
    {"symbol": "LQD",   "name": "Investment Grade Corp",    "category": "ETF/BONDS"},
    {"symbol": "HYG",   "name": "High Yield Corp Bond",     "category": "ETF/BONDS_HIGH_YIELD"},

    # ---- COMMODITY ----
    {"symbol": "GLD",   "name": "Gold",                     "category": "ETF/COMMODITY_GOLD"},
    {"symbol": "SLV",   "name": "Silver",                   "category": "ETF/COMMODITY_SILVER"},
    {"symbol": "USO",   "name": "US Oil",                   "category": "ETF/COMMODITY_OIL"},
    {"symbol": "DBA",   "name": "Agriculture",              "category": "ETF/COMMODITY_AGRI"},

    # ---- THEMATIC / TECH / INNOVATION ----
    {"symbol": "ARKK",  "name": "ARK Innovation",           "category": "ETF/THEMATIC_TECH"},
    {"symbol": "SMH",   "name": "Semiconductors",           "category": "ETF/THEMATIC_SEMI"},
    {"symbol": "BOTZ",  "name": "Robotics & AI",            "category": "ETF/THEMATIC_AI"},
    {"symbol": "CLOU",  "name": "Cloud Computing",          "category": "ETF/THEMATIC_CLOUD"},
    {"symbol": "HACK",  "name": "Cybersecurity",            "category": "ETF/THEMATIC_CYBER"},
    {"symbol": "BUG",   "name": "Cybersecurity",            "category": "ETF/THEMATIC_CYBER"},

    # ---- GREEN / ENERGY TRANSITION ----
    {"symbol": "ICLN",  "name": "Global Clean Energy",      "category": "ETF/THEMATIC_CLEAN_ENERGY"},
    {"symbol": "TAN",   "name": "Solar Energy",             "category": "ETF/THEMATIC_SOLAR"},
    {"symbol": "LIT",   "name": "Lithium & Battery",        "category": "ETF/THEMATIC_BATTERY"},
    {"symbol": "FAN",   "name": "Global Wind Energy",       "category": "ETF/THEMATIC_WIND"},

    # ---- COUNTRY / EM / INTERNATIONAL ----
    {"symbol": "EEM",   "name": "Emerging Markets",         "category": "ETF/INTL_EM"},
    {"symbol": "EWZ",   "name": "Brazil",                   "category": "ETF/INTL_COUNTRY"},
    {"symbol": "EWJ",   "name": "Japan",                    "category": "ETF/INTL_COUNTRY"},
    {"symbol": "EWY",   "name": "South Korea",              "category": "ETF/INTL_COUNTRY"},
    {"symbol": "EWG",   "name": "Germany",                  "category": "ETF/INTL_COUNTRY"},
    {"symbol": "FXI",   "name": "China Large-Cap",          "category": "ETF/INTL_COUNTRY"},
    {"symbol": "INDA",  "name": "India",                    "category": "ETF/INTL_COUNTRY"},

    # ---- NICHE / SPECIALTY ----
    {"symbol": "URA",   "name": "Uranium Miners",           "category": "ETF/NICHE_URANIUM"},
    {"symbol": "PHO",   "name": "Water Resources",          "category": "ETF/NICHE_WATER"},
    {"symbol": "CGW",   "name": "Global Water",             "category": "ETF/NICHE_WATER"},
]


# ============================
#  UNIONE TOTALE
# ============================

ALL_ASSETS = CRYPTO_ASSETS + STOCK_ASSETS + ETF_ASSETS
