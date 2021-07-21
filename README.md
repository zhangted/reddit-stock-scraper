# reddit-stock-scraper

1. Install requirements via <code>pip install -r requirements.txt</code>
2. Input your reddit username/password and API client/secret key in <code>/scripts/get_reddit.py</code>. For more info on how to get client/secret key, see https://github.com/reddit-archive/reddit/wiki/OAuth2
3. Run in cli/term:  <code>./manage.py makemigrations reddit_scraper</code>  and   <code>./manage.py migrate</code> to setup Postgres database
4. Run in cli/term:  <code>./manage.py createsuperuser</code>    to make admin account
5. Go to <code>BaseURL/admin/</code> and login, then go to <code>BaseURL/links/</code> for the admin panel
6. Add subreddits to scrape @ <code>BaseURL/add/</code>
7. Run <code>./manage.py update_tickers</code> to add valid tickers and company names to database.
8. Run <code>./manage.py scrape_reddit</code> to scrape reddit. (Schedule this command for automated scraping)
