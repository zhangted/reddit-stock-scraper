from reddit_scraper import models
from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.http import HttpResponse, request
from django.utils.translation import gettext_lazy as _
import re

class AddSubredditForm(ModelForm):
    class Meta:
        model = models.Subreddit
        fields = ['subreddit']
    def clean_subreddit(self):
        subreddit = self.cleaned_data['subreddit']
        SubredditObj = models.Subreddit.objects.filter(subreddit=subreddit)
        if subreddit.isalpha():
            if not SubredditObj.exists():
                return subreddit
            else:
                raise forms.ValidationError(_("subreddit exists"))
        else:
            raise forms.ValidationError(_("subreddit invalid"))
