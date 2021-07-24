"""reddit_scraper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from reddit_scraper import views, serializers



urlpatterns = [
    path('admin/', admin.site.urls),
    path('add/', views.add_subreddit, name='add'),
    path('view_sub/', views.view_subreddit, name='view'),
    path('delete_sub/', views.delete_subreddit, name='delete'),
    path('update_tickers/', views.update_tickers, name='updatetickers'),
    path('scrape_reddit/', views.scrape_reddit, name='scrapereddit'),
    path('links/', views.links, name='links'),
    path('api/', serializers.FrequencyEntriesList.as_view()),
    path('daily/', views.DailyList.as_view()),
    path('', views.IndexView, name='index')
]
