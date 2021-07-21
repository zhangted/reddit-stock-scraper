import requests
from lxml import html
import json
from reddit_scraper import models

def run():
    html_elements = requests.get('https://stockanalysis.com/stocks/')
    html_elements = html.fromstring(html_elements.text)
    html_elements = html_elements.cssselect("li")
    tickers_dict = {}
    invalidTickers = {
        'A',
        'G',
        'I',
        'N',
        'P',
        'Q',
        'S',
        'X',
        'AP',
        'CA',
        'DD',
        'EV',
        'GO',
        'IE',
        'IN',
        'JC',
        'MF',
        'TO',
        'UN',
        'US',
        'WS',
        'BNN',
        'CAD',
        'CSE',
        'DIY',
        'DFV',
        'DMV',
        'ETF',
        'IPO',
        'IRL',
        'LET',
        'LIF',
        'LOL',
        'RIF',
        'RSS',
        'TSX',
        'UTC',
        'WSB',
        'WTF',
        'WTH',
        'AQAA',
        'APES',
        'BACK',
        'DRIP',
        'FOMO',
        'FUCK',
        'HERE',
        'HODL',
        'HOLD',
        'JSON',
        'LIRA',
        'LMAO',
        'NSFW',
        'NYSE',
        'OVER',
        'REIT',
        'RESP',
        'RRSP',
        'SHIT',
        'TFSA',
        'VOTE',
        'YOLO'
    }
    for line in html_elements:
        line = line.text_content().split(" ")
        ticker, name = line[0], ' '.join(line[2:])
        if ticker.isupper() and ticker not in invalidTickers:
            tickers_dict[ticker] = name


    for t in tickers_dict:
        if not models.Ticker.objects.filter(ticker=t).exists():
            TickerObj = models.Ticker(ticker=t)
            if TickerObj:
                TickerInfoBasicObj = models.TickerInfoBasic(ticker=TickerObj, name=tickers_dict[t])
                if TickerInfoBasicObj:
                    TickerObj.save()
                    TickerInfoBasicObj.save()

                    
"""
                    #print(t + ' added to Tickers db')
                #else:
                    #print('Error adding ticker to db')
            #else:
                #print("Error adding ticker to db")
        #else:
            #print(t + ' exists in Tickers db')

#with open('tickers.json', 'w') as f:
    #json.dump(d, f)
"""