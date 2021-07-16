from django.db import models

class Ticker(models.Model):
    """Contains valid tickers."""
    ticker = models.CharField(max_length=10)
    def __str__(self):
        return self.ticker

class Subreddit(models.Model):
    """Contains subreddit name, last time frequencies were updated,
    the last unix timestamp for a scraped post/title, and last unix
    timestamp for a scraped comment, for a subreddit."""
    subreddit = models.CharField(max_length=50)
    last_updated = models.DateTimeField(null=True, blank=True)
    post_title_last_timestamp = models.FloatField(null=True, blank=True)
    comments_last_timestamp = models.FloatField(null=True, blank=True)
    first_scraped = models.DateTimeField(auto_now=True)

class TickerInfoBasic(models.Model):
    """Basic info about a ticker."""
    ticker = models.OneToOneField(Ticker, on_delete=models.CASCADE, related_name='TickerInfoBasic')
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=300, null=True, blank=True)

class FrequencyEntries(models.Model):
    """Contains frequency entries for a ticker in a subreddit w/ timestamp."""
    subreddit = models.CharField(max_length=50)
    ticker = models.CharField(max_length=10)
    last_updated = models.DateTimeField(auto_now=True)
    count = models.IntegerField()

#exec(open('reddit_scraper/scripts/print.py').read())
