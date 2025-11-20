import yfinance as yf

btc = yf.Ticker("BTC-USD")

# intervallo che dà SEMPRE dati reali
data = btc.history(period="5d", interval="15m")

print("\nUltimi 10 dati ricevuti:\n")
print(data.tail(10))
