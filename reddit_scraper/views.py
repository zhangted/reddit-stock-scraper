from reddit_scraper import models, forms, serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import Trunc, TruncDay
import time
from django.db.models import Sum, Max
from django.contrib.auth.decorators import user_passes_test
from reddit_scraper.scripts import get_tickers_no_timeout, get_reddit


@user_passes_test(lambda u: u.is_superuser)
def add_subreddit(request):
    """Superuser func to add subreddits."""
    formClass = forms.AddSubredditForm
    args = {'form':formClass}
    if request.method=='POST':
        form = formClass(data=request.POST)
        if form.is_valid():
            form.clean_subreddit()
            form.save()
            return HttpResponse("successful")
        else:
            args['form'] = form
    return render(request, "add_subreddit.html", args)

@user_passes_test(lambda u: u.is_superuser)
def view_subreddit(request):
    """Superuser func to list subreddits."""
    args = {}
    args['rows'] = models.Subreddit.objects.values('subreddit')
    return render(request, "view_subreddit.html", args)

@user_passes_test(lambda u: u.is_superuser)
def delete_subreddit(request):
    """Superuser func to delete subreddits"""
    if request.method == 'GET':
        models.Subreddit.objects.get(subreddit=request.GET['subreddit']).delete() 
        return redirect('view')

@user_passes_test(lambda u: u.is_superuser)
def update_tickers(request):
    """Superuser func to update tickers"""
    get_tickers_no_timeout.run()
    return redirect('view')

@user_passes_test(lambda u: u.is_superuser)
def links(request):
    """Links"""
    return render(request, "links.html")

@user_passes_test(lambda u: u.is_superuser)
def scrape_reddit(request):
    """Scrapes subreddits"""
    get_reddit.start()
    return redirect('links')



def IndexView(request):
    """Render api link generator."""
    args = {}
    args['subreddits'] = []
    args['timeIntervals'] = [1, 2, 3, 12, 24, 48, 168, 336, 710] #TODO: more time intervals
    args['lastUpdated'] = models.Subreddit.objects.aggregate(max=Max('last_updated'))['max']
    for i in models.Subreddit.objects.all().values_list('subreddit'):
        args['subreddits'].append(''.join(i))
    return render(request, "base.html", args)





#Unused stuff

    """
class HourlyList(APIView):
    def get(self, request):
        ans = {}
        this_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
        one_hour_later = this_hour + timedelta(hours=1)
        q = models.FrequencyEntries.objects.filter(subreddit='wallstreetbets', last_updated__range=(this_hour, one_hour_later)).values('ticker').annotate(Sum('count'))
        for i in q:
            if i['count__sum']:
                ans[i['ticker']] = i['count__sum']
        return Response(ans)
        """

class DailyList(APIView):
    def get(self, request):
        ans = {}
        this_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        one_day_later = this_day + timedelta(days=1)
        q = models.FrequencyEntries.objects.filter(subreddit='wallstreetbets', last_updated__range=(this_day, one_day_later)).values('ticker').annotate(Sum('count'))
        for i in q:
            if i['count__sum']:
                ans[i['ticker']] = i['count__sum']
        return Response(ans)