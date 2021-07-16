from django.core.management.base import BaseCommand, CommandError
from reddit_scraper.scripts import get_reddit

class Command(BaseCommand):
    """Run this through the heroku/terminal as './manage.py scrape_reddit.py' 
       Set the command to run every hour through a scheduler.
    """
    help = 'scrapes subreddits for ticker mentions'

    def handle(self, *args, **options):
        get_reddit.start()
        return
