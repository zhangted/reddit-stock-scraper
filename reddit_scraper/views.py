from reddit_scraper import models, forms, serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.utils import timezone
import time, requests
from django.db.models import Sum, Max
from django.contrib.auth.decorators import user_passes_test
from reddit_scraper.scripts import get_tickers_no_timeout, get_tickers, get_reddit
from django.utils.html import escape

from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView

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
        return redirect('index')

@user_passes_test(lambda u: u.is_superuser)
def update_tickers(request):
    """Superuser func to update tickers"""
    get_tickers_no_timeout.run()
    return redirect('index')

@user_passes_test(lambda u: u.is_superuser)
def links(request):
    """Links"""
    return render(request, "links.html")

@user_passes_test(lambda u: u.is_superuser)
def scrape_reddit(request):
    """Scrapes subreddits"""
    get_reddit.start()
    return redirect('links')

def view_data(request, subreddit, hours_ago):
    args = {} #context data
    args['subreddit'] = escape(subreddit) #selected subreddit
    args['lastUpdated'] = models.Subreddit.objects.get(subreddit=args['subreddit']).last_updated #last update time
    args['subreddits'] = []
    for i in models.Subreddit.objects.all().values_list('subreddit'):
        args['subreddits'].append(''.join(i))
    args['hours_ago'] = int(escape(hours_ago)) #selected 'hours ago'
    args['timeIntervals'] = [1, 2, 3, 12, 24, 48, 168, 336, 720]
    return render(request, "charts.html", args)

def IndexView(request):
    return redirect('view/wallstreetbets/1')

def about(request):
    args = {}
    return render(request, "about.html", args)

def aboutAPI(request):
    args = {}
    args['subredditNames'] = [i['subreddit'] for i in models.Subreddit.objects.all().values('subreddit')]
    return render(request, "about-api.html", args)

def generate_link(subreddit, hours_ago):
    return requests.get("https://reddit-stock-scrape.herokuapp.com/api/?subreddit="+subreddit+"&hoursago="+hours_ago+"&format=json").json()

class PieChartJSONView(BaseLineChartView):
    def get_context_data(self, **kwargs): #Override to get subreddit and hours_ago variables
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        jsonData = generate_link(context['subreddit'], context['hours_ago'])
        context.update({"labels": self.get_labels(jsonData), "datasets": self.get_datasets(jsonData)})
        return context

    def get_labels(self, jsonData):
        """Return labels for the x-axis."""
        categories = []
        for entry in jsonData['results']:
            entry = entry["mentions_info"]
            categories.append([entry['ticker'], " "+entry['company_name']])
        return categories

    def get_providers(self):
        """Return names of datasets."""
        return ["A"]

    def get_datasets(self, jsonData):
        """Return datasets to plot."""
        res = {}
        counts = []
        colors = []
        pallet = ['#170e5c', '#1d1962', '#232367', '#282d6d', '#2d3672', '#323f77', '#37487c', '#3b5181', '#3f5a86', '#44628a', '#486b8f', '#4d7393', '#517b97', '#56839b', '#5b8a9f', '#6092a3', '#6599a6', '#6ba0aa', '#70a7ad', '#76aeb0', '#7bb4b3', '#81bbb6', '#88c1b8', '#8ec7bb', '#94ccbd', '#9bd1bf', '#a1d6c1', '#a8dbc3', '#afe0c4', '#b6e4c6', '#bde8c7', '#c4ecc8', '#cbefc9', '#d3f2ca', '#daf5cb', '#e1f8cb', '#e9facc', '#f0fccc', '#f8fecc', '#ffffcc']
        pallet_idx = 0
        for entry in jsonData['results']:
            entry = entry["mentions_info"]
            counts.append(entry['unique_mentions'])
            colors.append(pallet[pallet_idx % len(pallet)])
            pallet_idx += 1
        res['data'] = counts
        res['backgroundColor'] = colors
        return [res]

pie_chart = TemplateView.as_view(template_name='charts.html')
pie_chart_json = PieChartJSONView.as_view()


