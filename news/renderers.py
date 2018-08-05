from django_medusa.renderers import StaticSiteRenderer
from django.core.urlresolvers import reverse

from news.models import NewsItem


class NewsRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = []

        items = NewsItem.objects.all()
        for item in items:
            paths.append(item.get_absolute_url())
        paths.append(reverse('news'))
        return paths


renderers = [NewsRenderer, ]
