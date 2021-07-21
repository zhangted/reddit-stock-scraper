from reddit_scraper import models
import requests

base_url = "https://www.marketwatch.com/investing/stock/"
td = models.Subreddit.objects.get(subreddit='wallstreetbets').TickerFrequencyObj.all().values('ticker')
for i in td:
    ticker = i['ticker']
    html_elements = requests.get(base_url+ticker)
    html_text = html.fromstring(html_elements.text)
    name_html = html_text.cssselect("h1")
    info_html = html_text.cssselect("ul.list.list--kv.list--col50 > li > span")
    info2_html = html_text.cssselect("tbody.remove-last-border > tr > td")
    if len(name_html):
        name = name_html[0].text_content()
    else:
        name = ''
    if len(info_html):
        lohi = info_html[2].text_content()
        lo, hi = lohi.split("-")
        lo, hi = lo.replace(' ', ''), hi.replace(' ', '')
        mkcp = info_html[8].text_content()
    if len(info2_html):
        close = info2_html[0].text_content()
        chg = float(info2_html[1].text_content())
        chg_pct = info2_html[2].text_content()
    
    #print(name, lo, hi, mkcp, close, chg, chg_pct)
    