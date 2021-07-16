import requests
from lxml import html
import json
from reddit_scraper import models

def run():
    html_elements = requests.get('https://stockanalysis.com/stocks/')
    tickers = html.fromstring(html_elements.text)
    tickers = tickers.cssselect("li")
    tickers_set = set()
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
    for i in tickers:
        t = i.text_content().split(" ")[0]
        if t.isupper() and t not in invalidTickers:
            tickers_set.add(t)
            
    for t in tickers_set:
        if not models.Ticker.objects.filter(ticker=t).exists():
            TickerObj = models.Ticker(ticker=t)
            if TickerObj:
                TickerInfoBasicObj = models.TickerInfoBasic(ticker=TickerObj)
                if TickerInfoBasicObj:
                    TickerObj.save()
                    TickerInfoBasicObj.save()
                    #print(t + ' added to Tickers db')
                #else:
                    #print('Error adding ticker to db')
            #else:
                #print("Error adding ticker to db")
        #else:
            #print(t + ' exists in Tickers db')


#with open('tickers.json', 'w') as f:
    #json.dump(d, f)
