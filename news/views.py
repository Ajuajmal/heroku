import datetime

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import Feed
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.feedgenerator import Atom1Feed
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView

from markitup.fields import render_func

from news.models import NewsItem


class NewsItemView(TemplateView):
    template_name = 'news/item.html'

    def get_context_data(self, date, slug):
        context = super(NewsItemView, self).get_context_data()
        try:
            context['object'] = NewsItem.objects.get_by_url(date, slug)
        except NewsItem.DoesNotExist:
            raise Http404
        return context


class NewsFeedView(TemplateView):
    template_name = 'news/feed.html'

    def get_context_data(self, page=0):
        context = super(NewsFeedView, self).get_context_data()
        context['stories'] = NewsItem.objects.all()
        return context


class NewsRSSView(Feed):
    title = _('News')
    link = reverse_lazy('news')
    description = _('Conference News')

    def get_feed(self, obj, request):
        site = get_current_site(request)
        self.title = site.name
        self.description = _('News from %s') % site.name
        return super(NewsRSSView, self).get_feed(obj, request)

    def items(self):
        return NewsItem.objects.all()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return render_func(item.body)

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        dt = datetime.datetime.combine(item.date, datetime.time())
        return make_aware(dt)

    def item_updateddate(self, item):
        return self.item_pubdate(item)


class NewsAtomView(NewsRSSView):
    feed_type = Atom1Feed
    subtitle = NewsRSSView.description

    def item_author_name(self, item):
        return self.title
