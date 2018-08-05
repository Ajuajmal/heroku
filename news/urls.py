from django.conf.urls import url

from news.views import NewsAtomView, NewsItemView, NewsFeedView, NewsRSSView


urlpatterns = [
    url(r'^(?:page/(?P<page>[0-9]+)/)?$',
        NewsFeedView.as_view(), name='news'),
    url(r'^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})-(?P<slug>[^/]+)/$',
        NewsItemView.as_view(), name='news_item'),
    url(r'^feed/rss.xml$',
        NewsRSSView(), name='news_rss'),
    url(r'^feed/atom.xml$',
        NewsAtomView(), name='news_atom'),
]
