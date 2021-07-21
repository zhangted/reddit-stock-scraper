from rest_framework import serializers, viewsets, generics, views
from reddit_scraper import models
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import Group

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 1000

class TickerInfoBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TickerInfoBasic
        fields = ['name']

class TickerSerializer(serializers.ModelSerializer):
    basic_info = TickerInfoBasicSerializer(read_only=True)
    class Meta:
        model = models.Ticker
        fields = ['ticker', 'basic_info']

class FrequencyEntriesSerializer(serializers.ModelSerializer):
    ticker = TickerSerializer(read_only=True)
    class Meta:
        model  = models.FrequencyEntries
        fields = ['last_updated', 'count', 'ticker'] 

        #group by ticker_id here

class SubredditSerializer(serializers.ModelSerializer):
    frequency_entries = FrequencyEntriesSerializer(many=True, read_only=True)
    class Meta:
        model = models.Subreddit
        fields =  ['subreddit', 'last_updated', 'frequency_entries']

class SubredditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Subreddit.objects.all()
    serializer_class = SubredditSerializer
    
class FrequencyEntriesGroupSumSerializer(serializers.ModelSerializer):
    mentions_info = serializers.SerializerMethodField()
    class Meta:
        model  = models.FrequencyEntries
        fields = ['mentions_info'] 
    
    def get_mentions_info(self, obj):
        output = d = {}
        tickerObj = models.Ticker.objects.get(id=obj['ticker'])
        ticker = tickerObj.ticker
        d['ticker'] = ticker
        d['company_name'] = tickerObj.basic_info.name
        d['unique_mentions'] = obj['total']
        return output
    
class FrequencyEntriesList(generics.ListAPIView):
    serializer_class = FrequencyEntriesGroupSumSerializer
    pagination_class = StandardResultsSetPagination

    @method_decorator(cache_page(60*60*2))
    def get(self, *args, **kwargs):
         return super().get(*args, **kwargs)

    def get_queryset(self):
        queryset = models.Subreddit.objects.all()
        subreddit = self.request.query_params.get('subreddit', None)
        hours_ago = int(self.request.query_params.get('hoursago', None))

        this_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
        one_hour_later = this_hour + timedelta(hours=1)
        this_hour = this_hour+timedelta(hours=-hours_ago)
        if subreddit is not None and hours_ago is not None:
            queryset = queryset.get(subreddit=subreddit).frequency_entries.all()
            queryset = queryset.values('ticker').filter(last_updated__range=(this_hour, one_hour_later)).annotate(total=Sum('count')).order_by('-total')
            """SELECT ticker, SUM(count) as total
                FROM FrequencyEntries 
                WHERE subreddit=input AND DATEDIFF(hour, last_updated, now)<=input
                GROUP BY ticker 
                ORDER BY total DESC
            """
        return queryset