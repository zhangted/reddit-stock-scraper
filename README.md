# reddit-stock-scraper

1. Install requirements via <code>pip install -r requirements.txt</code>
2. Input your reddit username/password and api client/secret key in /scripts/get_reddit.py
3. Run in cli/term:  <code>./manage.py makemigrations reddit_scraper</code>  and   <code>./manage.py migrate</code> to setup Postgres database
4. Run in cli/term:  <code>./manage.py createsuperuser</code>    to make admin account
5. Go to yourwebsite.com/admin   and login, then go to yourwebsite.com/links for the admin panel
6. Add subreddits to scrape @ yourwebsite.com/add/
7. Run <code>./manage.py update_tickers.py</code> to add valid tickers and company names to database.
8. Run <code>./manage.py scrape_reddit.py</code> to scrape reddit. (Schedule this command for automated scraping)
