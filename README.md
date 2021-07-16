# reddit-stock-scraper

1. install requirements
2. input reddit username/password and api client/secret key in /scripts/get_reddit.py
3. run in cli/term:  ./manage.py makemigrations   and   ./manage.py migrate to setup database
4. run in cli/term:  ./manage.py createsuperuser    to make admin account
5. go to yourwebsite.com/admin   and login, then go to yourwebsite.com/links and run "add tickers to database"
6. add subreddits @ yourwebsite.com/add/
7. schedule './manage.py scrape_reddit.py' to run every hour
