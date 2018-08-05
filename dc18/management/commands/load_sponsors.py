import pathlib

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db.models import Q

from wafer.sponsors.models import File, Sponsor, SponsorshipPackage

import yaml


class Command(BaseCommand):
    help = 'Load sponsor definitions from YAML files into the DB'

    def handle(self, *args, **options):
        for metafile in pathlib.Path(settings.SPONSORS_DIR).glob('*.yml'):
            logo = metafile.with_suffix('.svg')
            if not logo.exists():
                self.stderr.write('Missing SVG logo for %s, skipping\n'
                                  % metafile.stem)
                continue
            self.load_sponsor(metafile, logo)

    def save_logo(self, file_, logofile):
        with logofile.open() as f:
            new_logo = f.read()
        try:
            old_logo = file_.item.read().decode('utf8')
        except (FileNotFoundError, ValueError):
            old_logo = None
        if new_logo == old_logo:
            return
        file_.item.save(logofile.name, ContentFile(new_logo))

    def ensure_only(self, m2m_field, item):
        if m2m_field.filter(~Q(pk=item.id)).exists():
            m2m_field.clear()
        if not m2m_field.all().exists():
            m2m_field.add(item)

    def load_sponsor(self, metafile, logofile):
        with metafile.open() as f:
            meta = yaml.load(f)

        file_, created = File.objects.get_or_create(name=meta['name'])
        file_.description = meta['name']
        self.save_logo(file_, logofile)
        file_.save()

        package = SponsorshipPackage.objects.get(name=meta['package'])

        sponsor, created = Sponsor.objects.get_or_create(name=meta['name'])
        sponsor.description = meta['name']
        sponsor.order = meta['order']
        sponsor.url = meta['url']
        self.ensure_only(sponsor.packages, package)
        self.ensure_only(sponsor.files, file_)
        sponsor.save()

        self.stdout.write('Loaded sponsor %s\n' % meta['name'])
