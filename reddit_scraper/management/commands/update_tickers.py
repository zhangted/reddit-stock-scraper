from django.core.management.base import BaseCommand, CommandError
from reddit_scraper.scripts import get_tickers_no_timeout

class Command(BaseCommand):
    help = 'updates ticker database'

    def handle(self, *args, **options):
        get_tickers_no_timeout.run()
        return