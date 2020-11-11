import yfinance as yf
import pandas as pd
import bs4
import re
import requests
import xlwt
import finviz

class StockInfo:

    def percentToDecimal(self, rawData):
        listData = [str(s) for s in rawData]

        if listData[-1] == '%':
            strData = "".join(listData[:-1])
        else:
            strData = "".join(listData)
        return float(strData)
    
    def fillCompany(self, finvizData, ticker):
        return finvizData["Company"]
    
    def fillAnnualDiv(self, finvizData, ticker):
        return self.percentToDecimal(finvizData["Dividend"])
    
    def fillPrice(self, finvizData, ticker):
        return finvizData["Price"]
    
    def fillPayout(self, finvizData, ticker):
        return self.percentToDecimal(finvizData["Payout"])
    
    def fillPBRatio(self, finvizData, ticker):
        return self.percentToDecimal(finvizData["P/B"])
    
    def fillDebtRatio(self, finvizData, ticker):
        return self.percentToDecimal(finvizData["Debt/Eq"])

    def fillPERatio(self, finvizData, ticker):
        return self.percentToDecimal(finvizData["P/E"])
    
    
    def normalizeDividendsPerYear(self, dividends, splits):
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
    
    
    def getAvgDiv(self, yfinance, ticker):
        divss = self.normalizeDividendsPerYear(yfinance.dividends, yfinance.splits)
        return (divss[1])
    
    
    def fillConsecutiveDividendYears(self, ticker):
        url = "https://seekingalpha.com/symbol/"+ ticker +"/dividends/scorecard"
        r = requests.get(url, allow_redirects=True, verify = False)
        soup = bs4.BeautifulSoup(r.content, "lxml")
        text = soup.findAll(text = True)
        rawSAData = text
        strSAD = (str(rawSAData))
        divOccurs = [m.start() for m in re.finditer('Years of Dividend Growth', strSAD)]
        occur = divOccurs[0]

        return self.percentToDecimal(strSAD[occur+40:occur+43])
    
    
    def fillDividendGrowthPerYear(self, yfinanceTickerData, ticker):
        
        #lets get a dictionary with a dividend per year
        tickerDivYearDict = self.normalizeDividendsPerYear(yfinanceTickerData.dividends, yfinanceTickerData.splits)[0]

        divGrowths = []

        for year in tickerDivYearDict.keys():
            year = int(year-1)
            if year - 1 in tickerDivYearDict.keys() and year > 2000:
                divGrowths.append((tickerDivYearDict[year]/tickerDivYearDict[year-1]) - 1)

        return (sum(divGrowths)/len(divGrowths))
    
    def fillEPSGrowthRate(self, ticker):
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
    
    
    def underOrOver(self, finvizTickerData, yfinance, ticker):
        try:
            if self.fillAnnualDiv(finvizTickerData, ticker) > self.getAvgDiv(yfinance, ticker):
                return "Undervalued"
            else:
                return "Overvalued"
        except:
            return "-"
    
#-----------
    
    def getStockInfo(self, ticker):
        
        info = {}
        
        finvizTickerData = finviz.get_stock(ticker)
        yfinanceTickerData = yf.Ticker(ticker)
        
        try:
            info["Ticker"] = ticker
        except:
            info["Ticker"] = "-"
    
        try:
            info["Company"] = self.fillCompany(finvizTickerData, ticker)
        except:
            info["Company"] = "-"
            
        try:
            info["Price"] = self.fillPrice(finvizTickerData, ticker)
        except:
            info["Price"] = "-"
            
        try:
            info["Dividend"] = self.fillAnnualDiv(finvizTickerData, ticker)
        except:
            info["Dividend"] = "-"
            
        try:
            info["EPS Growth"] = self.fillEPSGrowthRate(ticker)
        except:
            info["EPS Growth"] = "-"
            
        try:
            info["Dividend Growth"] = self.fillDividendGrowthPerYear(yfinanceTickerData, ticker)
        except:
            info["Dividend Growth"] = "-"
        
        try:
            info["Payout"] = self.fillPayout(finvizTickerData, ticker)
        except:
            info["Payout"] = "-"
        
        try:
            info["Debt"] = self.fillDebtRatio(finvizTickerData, ticker)
        except:
            info["Debt"] = "-"
        
        try:
            info["PE"] = self.fillPERatio(finvizTickerData, ticker)
        except:
            info["PE"] = "-"
        
        try:
            info["PB"] = self.fillPBRatio(finvizTickerData, ticker)
        except:
            info["PB"] = "-"
            
        try:
            info["under or over valued"] = self.underOrOver(finvizTickerData, yfinanceTickerData, ticker)
        except:
            info["under or over valued"] = "-"
        
        try:
            info["Consecutive Years of Div Inc"] = self.fillConsecutiveDividendYears(ticker)
        except:
            info["Consecutive Years of Div Inc"] = "-"
        
        return info


