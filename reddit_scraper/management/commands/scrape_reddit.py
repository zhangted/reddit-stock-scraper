from django.core.management.base import BaseCommand, CommandError
from reddit_scraper.scripts import get_reddit

class Command(BaseCommand):
    help = 'scrapes subreddits for ticker mentions'

    def handle(self, *args, **options):
        get_reddit.start()
        return