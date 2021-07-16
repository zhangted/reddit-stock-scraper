"""
from reddit_scraper import models
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import Trunc, TruncDay
import time
from django.db.models import Sum

subreddit = 'wallstreetbets'
#SubredditObj = models.Subreddit.objects.filter(subreddit=subreddit)[0]
#q = SubredditObj.Ticker.all()


cur = time.perf_counter()

this_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
this_hour2 = this_hour + timedelta(hours=-2)
one_hour_later = this_hour + timedelta(hours=1)

q = models.FrequencyEntries.objects.filter(subreddit='wallstreetbets', last_updated__range=(this_hour2, one_hour_later)).values('ticker').annotate(Sum('count'))

d = {}
for i in q:
    #k = i.records.prefetch_related('ticker.ticker', 'count').filter(last_updated__range=(this_hour2, one_hour_later))
    print(i)

fin = time.perf_counter()
print(fin-cur, "elapsed")

keys = d.keys()
keys = sorted(keys, key=lambda x: d[x])
for i in keys:
    print(i, d[i])
    #queryset.filter(created_at__date__gte=self.user_filter.from_date.date())

"""