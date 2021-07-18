from rest_framework import serializers, viewsets, generics
from reddit_scraper import models
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 1000

class SubredditSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subreddit
        fields =  ['subreddit', 'last_updated']

class SubredditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Subreddit.objects.all()
    serializer_class = SubredditSerializer

class FrequencyEntriesSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    class Meta:
        model = models.FrequencyEntries
        fields = ['ticker', 'total']
    def get_total(self, obj):
        return obj['total']

class FrequencyEntriesList(generics.ListAPIView):
    serializer_class = FrequencyEntriesSerializer
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        queryset = models.FrequencyEntries.objects.all()
        subreddit = self.request.query_params.get('subreddit', None)
        hours_ago = int(self.request.query_params.get('hoursago', None))

        this_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
        one_hour_later = this_hour + timedelta(hours=1)
        this_hour = this_hour+timedelta(hours=-hours_ago)
        if subreddit is not None and hours_ago is not None:
            queryset = queryset.values('ticker').filter(subreddit=subreddit, last_updated__range=(this_hour, one_hour_later)).annotate(total=Sum('count')).order_by('-total')
            """SELECT ticker, SUM(count) as total
                FROM FrequencyEntries 
                WHERE subreddit=input AND DATEDIFF(hour, last_updated, now)<=input
                GROUP BY ticker 
                ORDER BY total DESC
            """
        return queryset

    @method_decorator(cache_page(60*60*2))
     def get(self, *args, **kwargs):
         return super().get(*args, **kwargs)





"""
class TFTViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FrequencyEntriesSerializer
    pagination_class = StandardResultsSetPagination
    this_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
    one_hour_later = this_hour + timedelta(hours=1)
    this_hour = this_hour+timedelta(hours=-24)
    queryset = models.FrequencyEntries.objects.all().values('ticker').filter(subreddit='wallstreetbets', last_updated__range=(this_hour, one_hour_later)).annotate(total=Sum('count')).order_by('-total')
"""
