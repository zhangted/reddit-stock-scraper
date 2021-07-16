import json
from reddit_scraper import models



def run():
    f = open('tickers.json',)
    d = json.load(f)

    for i in d:
        if not models.Ticker.objects.filter(ticker=i).exists():
            TickerObj = models.Ticker(ticker=i)
            if TickerObj:
                TickerInfoBasicObj = models.TickerInfoBasic(ticker=TickerObj)
                if TickerInfoBasicObj:
                    TickerObj.save()
                    TickerInfoBasicObj.save()