from django import template

from news.models import NewsItem

register = template.Library()


@register.inclusion_tag('news/feed_snippet.html')
def recent_news(limit=5):
    return {
        'stories': NewsItem.objects.latest(limit),
    }
