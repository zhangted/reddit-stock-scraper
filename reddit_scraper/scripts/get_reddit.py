import requests
import time
from reddit_scraper import models
import re
from django.utils import timezone

#connect to reddit api
REDDIT_USERNAME = ''
REDDIT_PASSWORD = ''
APP_ID = ''
APP_SECRET = ''
base_url = 'https://www.reddit.com/'
data = {'grant_type': 'password', 'username': REDDIT_USERNAME, 'password': REDDIT_PASSWORD}
auth = requests.auth.HTTPBasicAuth(APP_ID, APP_SECRET)
headers = {'user-agent': 'reddit_scraper by txz81'}
try:
    response = requests.post(base_url + 'api/v1/access_token',
                    data=data,
                    headers=headers,
                    auth=auth)
    r = response.json()
    TOKEN = r['access_token']
    headers['Authorization'] = f'bearer {TOKEN}'
except:
    print('issue connecting to reddit api')

def start():
    """Call this to start scraping subreddits."""
    subreddits = models.Subreddit.objects.all()
    tickers = models.Ticker.objects.all()
    tickers_dict = {t.ticker for t in tickers}
    for s in subreddits:
        scraped_dict = {}
        get_post_title_data(s, 100, headers, scraped_dict)
        get_comment_data(s, 1000, headers, scraped_dict)
        store_data(s, scraped_dict)

def roundDown_Hour_UTC(utc_float):
    """Round unix time down to the nearest hour."""
    return (utc_float // 3600) * 3600

def set_PostTitle_lastTimestamp(Subreddit, utc_float):
    """Sets the last timestamp seen from a scraped post/title for a subreddit."""
    Subreddit.post_title_last_timestamp = utc_float
    Subreddit.save()

def set_Comments_lastTimestamp(Subreddit, utc_float):
    """Ssets the last timestamp seen from a scraped comment for a subreddit"""
    Subreddit.comments_last_timestamp = utc_float
    Subreddit.save()

def set_SubredditUpdateTime(Subreddit):
    """Sets the timestamp for when a subreddit was scraped."""
    Subreddit.last_updated = timezone.now()
    Subreddit.save()

def get_post_title_data(SubredditObj, limit, headers, scraped_dict):
    """Goes through a subreddit and scrapes posts/titles for stock tickers."""
    base_url = 'https://oauth.reddit.com/r/'
    subreddit = SubredditObj.subreddit
    data = requests.get(base_url + subreddit + "/new" + "?limit=" + str(limit), headers=headers).json()

    if not SubredditObj.post_title_last_timestamp:
        lastGET_utctime = roundDown_Hour_UTC(time.time())
    else:
        lastGET_utctime = max(SubredditObj.post_title_last_timestamp, roundDown_Hour_UTC(time.time()))

    TickerObj = models.Ticker.objects.all() #get all tickers
    ticker_dict = {t.ticker for t in TickerObj} #create ticker dict
    max_utc = lastGET_utctime #max utc seen so far
    set_SubredditUpdateTime(SubredditObj)
    while True: #loop
        after = data['data']['after'] #next page
        for i in data['data']['children']: #for every post
            post_data = i['data']
            time_posted = post_data['created_utc'] 
            max_utc = max(max_utc, time_posted) #update max utc seen
            if lastGET_utctime and time_posted <= lastGET_utctime:
                set_PostTitle_lastTimestamp(SubredditObj, max_utc)
                return #exit if the current post has already been scraped
            text_data = post_data['title'] + post_data['selftext']
            text_data = re.sub(r'[-()\"#_/@;:<>{+=~*|`.!?,]', '    ', text_data)
            text_data = re.sub(r'\n', '    ', text_data)
            seen = set()
            for w in text_data.split(" "):
                w = w.strip("'")
                if not w.isupper():
                    continue #exclude lowercase strings
                if w not in ticker_dict:
                    continue #exclude invalid strings
                if w in seen:
                    continue #exclude string seen alrdy in current post
                if w not in scraped_dict:
                    scraped_dict[w] = 1
                else: 
                    scraped_dict[w] += 1
                seen.add(w)#one instance of a ticker per post+title
        if not after:
            set_PostTitle_lastTimestamp(SubredditObj, max_utc)
            return
        try:
            data = requests.get(base_url + subreddit + "/" + sort + "?limit=" + limit + "?after=" + after, 
                                headers=headers).json() #get the next page
        except:
            print("Issue getting next page for title/post")
            break
    set_PostTitle_lastTimestamp(SubredditObj, max_utc)

def get_comment_data(SubredditObj, limit, headers, scraped_dict):
    """Goes through a subreddit and scrapes comments for stock tickers."""
    base_url = 'https://oauth.reddit.com/r/'
    subreddit = SubredditObj.subreddit
    data = requests.get(base_url + subreddit + "/comments/?limit=" + str(limit), headers=headers).json()

    if not SubredditObj.comments_last_timestamp:
        lastGET_utctime = roundDown_Hour_UTC(time.time())
    else:
        lastGET_utctime = max(SubredditObj.comments_last_timestamp, roundDown_Hour_UTC(time.time()))

    TickerObj = models.Ticker.objects.all() #get all tickers
    ticker_dict = {t.ticker for t in TickerObj} #create ticker dict
    max_utc = lastGET_utctime #max utc seen so far
    set_SubredditUpdateTime(SubredditObj)
    while True: #loop
        after = data['data']['after'] #next page
        for i in data['data']['children']: #for every post
            post_data = i['data']
            time_posted = post_data['created_utc'] 
            max_utc = max(max_utc, time_posted) #update max utc seen
            if lastGET_utctime and time_posted <= lastGET_utctime:
                set_Comments_lastTimestamp(SubredditObj, max_utc)
                return #exit if the current post has already been scraped
            text_data = post_data['body']
            text_data = re.sub(r'[-()\"#_/@;:<>{+=~*|`.!?,]', '    ', text_data)
            text_data = re.sub(r'\n', '    ', text_data)
            seen = set()
            for w in text_data.split(" "):
                w = w.strip("'")
                if not w.isupper():
                    continue #exclude lowercase strings
                if w not in ticker_dict:
                    continue #exclude invalid strings
                if w in seen:
                    continue #exclude string seen alrdy in current post
                if w not in scraped_dict:
                    scraped_dict[w] = 1
                else: 
                    scraped_dict[w] += 1
                seen.add(w)#one instance of a ticker per post+title
        if not after:
            set_Comments_lastTimestamp(SubredditObj, max_utc)
            return
        try:
            data = requests.get(base_url + subreddit + "/comments/?after=" + after + "&limit=" + str(limit), 
                                headers=headers).json() #get the next page
        except:
            print('Issue getting next page for comments')
            break
    set_Comments_lastTimestamp(SubredditObj, max_utc)

def store_data(SubredditObj, scraped_dict):
    """Stores dictionary created by scraping reddit posts in FrequencyEntries database."""
    print(scraped_dict)
    for t in scraped_dict:
        query = models.FrequencyEntries(subreddit=SubredditObj.subreddit, ticker=t, count=scraped_dict[t])
        query.save()


#exec(open('reddit_scraper/scripts/get_post_title.py').read())
