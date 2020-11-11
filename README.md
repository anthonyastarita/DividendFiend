# DividendFiend
Want to create a dividend stock screener, tracker, trading bot? We have all your dividend stock needs in one package!

# Quickstart

pip install dividendfiend

```
import DividendFiend as df
stockInfo = df.StockInfo()
stockInfo.getStockInfo(<insert ticker here>)
```

# getStockInfo

This package only has 1 public function: 

getStockInfo(ticker)

```
getStockInfo("AAPL")

{'Ticker': 'AAPL',
 'Company': 'Apple Inc.',
 'Price': '115.97',
 'Dividend': 0.82,
 'EPS Growth': 12.7025,
 'Dividend Growth': 0.8559219973649527,
 'Payout': 24.1,
 'Debt': 1.73,
 'PE': 35.5,
 'PB': 30.28,
 'under or over valued': 'Undervalued',
 'Consecutive Years of Div Inc': 9.0}
 ```
 
 We grab data from finviz, marketwatch, seeking alpha to bring you concise and useful dividend stock data.
 
 
 # Use as a screener
 
 Use this boilerplate code to use the file tickerList.xls (a curated list of a few thousand stocks) to iterate through and get dividend stocks that meet your criteria
 ```
import pandas as pd

xls = pd.ExcelFile("tickerList.xls")
sheetX = xls.parse(0)
tickers = sheetX['Tickers']

for ticker in tickers:
    print(stockInfo.getStockInfo(ticker))
 ```
 
 These are all of the Dividend Aristocrats (Stocks that have increased their dividend payouts for 25+ consecutive years)
 
 ```
 tickers = ["GPC", "DOV", "EMR", "PG", "MMM", "CINF", "KO", "JNJ", "LOW", "CL", "HRL", "TGT", "SWK", "SYY", "BDX", "LEG", "PPG", "GWW", "KMB", "PEP", "VFC", "ABBV", "NUE", "SPGI", "ABT", "WMT", "ED", "ITW", "ADM", "ADP", "WBA", "MCD", "PNR", "CLX", "MDT", "SHW", "BEN", "AFL", "CTAS", "XOM", "ATO", "TROW", "MKC", "CVX", "GD", "ECL", "LIN", "PBCT", "ROP", "O", "AOS", "CAT", "CB", "RTX", "OTIS", "CARR", "ESS", "EXPD", "ROST", "ALB", "AMCR"] 

for ticker in tickers:
    try:
        if meetsCriteria(ticker):
            print(ticker, stockInfo.getStockInfo(ticker))
    except:
        continue
 ```
 
 # Sample stock criteria
 
An undervalued dividend stock might have most or all of these criteria:

EPS growth > 8%

Dividend Growth > 8%

Payout ratio <= 75%

Debt < 70%

P/E Ratio < 25

Is the current dividend yield higher than the average dividend yield? (under or over valued)

P/B Ratio < 3
 
 
 
