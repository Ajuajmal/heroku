# Not actually models
from itertools import islice
from pathlib import Path
import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import yaml


NEWS_DIR = Path(settings.NEWS_DIR)


class NewsItemDoesNotExist(ObjectDoesNotExist):
    pass


class NewsItemManager(object):
    @classmethod
    def get_by_url(cls, date, slug):
        fn = '%s-%s.md' % (date, slug)
        assert '/' not in fn
        path = NEWS_DIR / fn
        if not path.exists():
            raise NewsItemDoesNotExist()
        return cls._load_item(path)

    @classmethod
    def all(cls):
        items = sorted(NEWS_DIR.iterdir(), reverse=True)
        for item in items:
            if item.name.startswith('.'):
                continue
            if not item.suffix == '.md':
                continue
            yield cls._load_item(item)

    @classmethod
    def latest(cls, number=5):
        return islice(cls.all(), number)

    @classmethod
    def _load_item(cls, path):
        year, month, day, slug = path.stem.split('-', 3)
        date = datetime.date(int(year), int(month), int(day))
        meta, body = cls._read_story(path)
        title = meta['title']
        return NewsItem(date, slug, title, body)

    @classmethod
    def _read_story(cls, path):
        with path.open(encoding='utf-8') as f:
            if f.readline() != '---\n':
                raise Exception('Missing front matter in %s\n' % path)
            front_matter = []
            for line in f:
                if line == '---\n':
                    break
                front_matter.append(line)
            meta = yaml.load(''.join(front_matter))
            contents = f.read()
        return meta, contents


class NewsItem(object):
    objects = NewsItemManager
    DoesNotExist = NewsItemDoesNotExist

    def __init__(self, date, slug, title, body):
        self.date = date
        self.slug = slug
        self.title = title
        self.body = body

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news_item', kwargs={
            'date': self.date,
            'slug': self.slug,
        })
