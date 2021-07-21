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
    """Start scraping all subreddits in the db for their posts and comments."""
    subreddits = get_subreddits()
    for s in subreddits:
        scraped_dict = get_post_title_data(s, 100, headers, {}) #scrape post/titles
        scraped_dict = get_comment_data(s, 1000, headers, scraped_dict) #scrape comments
        store_data(s, scraped_dict) #store data in db

def get_subreddits():
    """Return all Subreddit rows."""
    return models.Subreddit.objects.all()

def get_tickers():
    """Return all Ticker rows."""
    return models.Ticker.objects.all()

def get_ticker(t):
    """Return Ticker obj with ticker=t"""
    return models.Ticker.objects.get(ticker=t)

def get_valid_tickers_dict():
    """Return all valid Tickers in a dict"""
    i = get_tickers()
    return {j.ticker for j in i}

def roundDown_Hour_UTC(utc_float):
    """Round unix time down to the nearest hour."""
    return (utc_float // 3600) * 3600

def set_PostTitle_lastTimestamp(Subreddit, utc_float):
    """Set the latest seen timestamp for post/titles in a subreddit. """
    Subreddit.post_title_last_timestamp = utc_float
    Subreddit.save()

def set_Comments_lastTimestamp(Subreddit, utc_float):
    """Set the latest seen tiestamp for comments in a subreddit."""
    Subreddit.comments_last_timestamp = utc_float
    Subreddit.save()

def set_SubredditUpdateTime(Subreddit):
    """Set the last updated time of a subreddit."""
    Subreddit.last_updated = timezone.now()
    Subreddit.save()

def substitute_invalid_characters(text):
    """Substitute characters that are invalid with spaces and returns new string. Ex. !!STOCK? --> STOCK """
    text = re.sub(r'[-()\"#_/@;:<>{+=~*|`.!?,]', '    ', text)
    text = re.sub(r'\n', '    ', text)
    return text

def check_text_for_tickers(text, valid_tickers_dict, scraped_dict):
    valid_text = substitute_invalid_characters(text)
    seen = set()
    for w in valid_text.split(" "):
        w = w.strip("'")
        #exclude lowercase strings, strings that are not tickers, or strings that have been counted already
        if not w.isupper() or w not in valid_tickers_dict or w in seen: 
            continue
        if w not in scraped_dict: 
            scraped_dict[w] = 1
        else: 
            scraped_dict[w] += 1
        seen.add(w)#add cur string to seen dictionary to prevent counting them twice
    return scraped_dict

def get_post_title_data(SubredditObj, limit, headers, scraped_dict):
    """Goes through a subreddit and scrapes posts/titles for stock tickers."""
    base_url = 'https://oauth.reddit.com/r/'
    subreddit_string = SubredditObj.subreddit
    data = requests.get(base_url + subreddit_string + "/new" + "?limit=" + str(limit), headers=headers).json()

    if not SubredditObj.post_title_last_timestamp: #if there is no timestamp for the latest seen post/title
        lastGET_utctime = roundDown_Hour_UTC(time.time()) #then the stop trigger is a post to the nearest hour, rounded down
    else: 
        lastGET_utctime = max(SubredditObj.post_title_last_timestamp, roundDown_Hour_UTC(time.time()))
        #otherwise, the stop trigger is the max(cur time rounded down to nearest hour, latest seen post/title)
    valid_tickers_dict = get_valid_tickers_dict() #get all valid tickers
    max_utc = lastGET_utctime #max utc seen so far
    set_SubredditUpdateTime(SubredditObj) #set the subreddit update time
    while True:
        after = data['data']['after'] #next page
        for i in data['data']['children']: #for every post
            post_data = i['data'] 
            time_posted = post_data['created_utc'] 
            max_utc = max(max_utc, time_posted) #update max utc seen
            if lastGET_utctime and time_posted <= lastGET_utctime: #post has been scraped
                set_PostTitle_lastTimestamp(SubredditObj, max_utc)
                return scraped_dict
            unclean_text = post_data['title'] + post_data['selftext']
            scraped_dict = check_text_for_tickers(unclean_text, valid_tickers_dict, scraped_dict)
        if not after: #if no more pages to visit, then end function
            set_PostTitle_lastTimestamp(SubredditObj, max_utc)
            return scraped_dict
        try: #after pages still exist, so get next page
            data = requests.get(base_url + subreddit + "/" + sort + "?limit=" + limit + "?after=" + after, 
                                headers=headers).json()
        except:
            print("Issue getting next page for title/post")
            break
    set_PostTitle_lastTimestamp(SubredditObj, max_utc)
    return scraped_dict

def get_comment_data(SubredditObj, limit, headers, scraped_dict):
    """Goes through a subreddit and scrapes comments for stock tickers."""
    base_url = 'https://oauth.reddit.com/r/'
    subreddit = SubredditObj.subreddit
    data = requests.get(base_url + subreddit + "/comments/?limit=" + str(limit), headers=headers).json()

    if not SubredditObj.comments_last_timestamp: #if there is no timestamp for the latest seen post/title
        lastGET_utctime = roundDown_Hour_UTC(time.time()) #then the stop trigger is a post to the nearest hour, rounded down
    else: 
        lastGET_utctime = max(SubredditObj.comments_last_timestamp, roundDown_Hour_UTC(time.time()))
        #otherwise, the stop trigger is the max(cur time rounded down to nearest hour, latest seen post/title)
    valid_tickers_dict = get_valid_tickers_dict() #get all valid tickers
    max_utc = lastGET_utctime #max utc seen so far
    set_SubredditUpdateTime(SubredditObj) #set the subreddit update time
    while True: #loop
        after = data['data']['after'] #next page
        for i in data['data']['children']: #for every post
            post_data = i['data']
            time_posted = post_data['created_utc'] 
            max_utc = max(max_utc, time_posted) #update max utc seen
            if lastGET_utctime and time_posted <= lastGET_utctime:
                set_Comments_lastTimestamp(SubredditObj, max_utc)
                return scraped_dict
            unclean_text = post_data['body']
            scraped_dict = check_text_for_tickers(unclean_text, valid_tickers_dict, scraped_dict)
        if not after: #no more pages left to scrape, end function
            set_Comments_lastTimestamp(SubredditObj, max_utc)
            return scraped_dict
        try: #try to get next page
            data = requests.get(base_url + subreddit + "/comments/?after=" + after + "&limit=" + str(limit), 
                                headers=headers).json() 
        except:
            print('Issue getting next page for comments')
            break
    set_Comments_lastTimestamp(SubredditObj, max_utc)
    return scraped_dict

def store_data(SubredditObj, scraped_dict):
    """Stores dictionary created by scraping reddit posts in FrequencyEntries object."""
    print(SubredditObj.subreddit, scraped_dict)
    for t in scraped_dict:
        query = models.FrequencyEntries(subreddit=SubredditObj, ticker=get_ticker(t), count=scraped_dict[t])
        query.save()


#exec(open('reddit_scraper/scripts/get_reddit.py').read())