class StockInfo:
    
    def percentToDecimal(rawData):
        listData = [str(s) for s in rawData]

        if listData[-1] == '%':
            strData = "".join(listData[:-1])
        else:
            strData = "".join(listData)
        return float(strData)
    
    def fillCompany(finvizData, ticker):
        return finvizData["Company"]
    
    def fillAnnualDiv(finvizData, ticker):
        return percentToDecimal(finvizData["Dividend"])
    
    def fillPrice(finvizData, ticker):
        return finvizData["Price"]
    
    def fillPayout(finvizData, ticker):
        return percentToDecimal(finvizData["Payout"])
    
    def fillPBRatio(finvizData, ticker):
        return percentToDecimal(finvizData["P/B"])
    
    def fillDebtRatio(finvizData, ticker):
        return percentToDecimal(finvizData["Debt/Eq"])

    def fillPERatio(finvizData, ticker):
        return percentToDecimal(finvizData["P/E"])
    
    
    def normalizeDividendsPerYear(dividends, splits):
        dividendPerYear = {}

        masterActions = {}

        divs = []

        divKeys = list(dividends.items())
        splitsKeys = list(splits.items())


        for split in splitsKeys:
            splitsDate = str(split[0])[:4] + str(split[0])[5:7] + str(split[0])[8:10]
            value = split[1]
            masterActions[int(splitsDate)] = [value, "Split"]


        for div in divKeys:
            divDate = str(div[0])[:4] + str(div[0])[5:7] + str(div[0])[8:10]
            value = div[1]
            masterActions[int(divDate)] = [value, "Dividend"]


        sortedActions = sorted(masterActions.keys(), reverse = True)

        normalizedDivs = {}

        splitDivider = 1

        for i in range(len(sortedActions)):
            date = sortedActions[i]
            action = masterActions[date][1]
            value = masterActions[date][0]

            if action == 'Split':
                splitDivider = splitDivider * value
            else:
                dividend = value * (1/splitDivider)
                divs.append(dividend)
                normalizedDivs[date] = dividend
                year = str(date)[:4]
                if int(year) in dividendPerYear.keys():
                    dividendPerYear[int(year)] = dividendPerYear[int(year)] + dividend
                else:
                    dividendPerYear[int(year)] = dividend



        return [dividendPerYear, sum(divs)/len(divs)]
    
    
    def getAvgDiv(ticker):
        yfinanceTickerData = yf.Ticker(ticker)
        divss = normalizeDividendsPerYear(yfinanceTickerData.dividends, yfinanceTickerData.splits)
        return (divss[1])
    
    
    def fillConsecutiveDividendYears(ticker):
        url = "https://seekingalpha.com/symbol/"+ ticker +"/dividends/scorecard"
        r = requests.get(url, allow_redirects=True, verify = False)

        soup = bs4.BeautifulSoup(r.content, "lxml")
        text = soup.findAll(text = True)
        rawSAData = text[178]
        strSAD = (str(rawSAData))
        divOccurs = [m.start() for m in re.finditer('dividend_growth', strSAD)]
        secondOccur = divOccurs[1]

        return rawSAData[secondOccur+17:secondOccur+19]
    
    
    def fillDividendGrowthPerYear(yfinanceTickerData, ticker):
        
        #lets get a dictionary with a dividend per year
        tickerDivYearDict = normalizeDividendsPerYear(yfinanceTickerData.dividends, yfinanceTickerData.splits)[0]

        divGrowths = []

        for year in tickerDivYearDict.keys():
    #         print(year, year.type())
            year = int(year-1)
            if year - 1 in tickerDivYearDict.keys() and year > 2000:
                divGrowths.append((tickerDivYearDict[year]/tickerDivYearDict[year-1]) - 1)
    #             print(year, (tickerDivYearDict[year]/tickerDivYearDict[year-1]) - 1, tickerDivYearDict[year], tickerDivYearDict[year-1])


        return (sum(divGrowths)/len(divGrowths))
    
    def fillEPSGrowthRate(ticker):
        EPS=[]

        url = "http://www.marketwatch.com/investing/stock/"+ticker+"/financials"
        r = requests.get(url, allow_redirects=True)

        soup = bs4.BeautifulSoup(r.content, "lxml")
        titles = soup.findAll('td', {'class': 'rowTitle'})

        for title in titles:
            if 'EPS (Basic)' in title.text:
                EPS = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]

        #clean that data

        EPSClean = []

        for eps in EPS:
            try:
                EPSClean.append(float(eps[:-1]))
            except:
                continue

        return (sum(EPSClean)/len(EPSClean))
    
#-----------
    
    def getStockInfo(self, ticker):
        info = {}
        
        finvizTickerData = finviz.get_stock(ticker)
        yfinanceTickerData = yf.Ticker(ticker)
        
        info["Ticker"] = ticker
        info["Price"] = fillPrice(ticker)
        info["Dividend"] = fillAnnualDiv(finvizTickerData, ticker)
        info["Company"] = fillCompany(finvizTickerData, ticker)
        info["EPS Growth"] = fillEPSGrowthRate(ticker)
        info["Dividend Growth"] = fillDividendGrowthPerYear(yfinanceTickerData, ticker)
        info["Payout"] = fillPayout(finvizTickerData, ticker)
        info["Debt"] = fillDebtRatio(finvizData, ticker)
        info["PE"] = fillPERatio(finvizTickerData, ticker)
        info["PB"] = fillPBRatio(finvizTickerData, ticker)
        
        return info

