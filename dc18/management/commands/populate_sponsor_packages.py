from django.core.management.base import BaseCommand

from wafer.sponsors.models import SponsorshipPackage

PACKAGES = [
    {
        'name': 'Platinum',
        'number_available': 10,
        'price': 20000,
        'description': 'Platinum Sponsors',
    },
    {
        'name': 'Gold',
        'number_available': 100,
        'price': 10000,
        'description': 'Gold Sponsors',
    },
    {
        'name': 'Silver',
        'number_available': 100,
        'price': 5000,
        'description': 'Silver Sponsors',
    },
    {
        'name': 'Bronze',
        'number_available': 100,
        'price': 2000,
        'description': 'Bronze Sponsors',
    },
    {
        'name': 'Supporter',
        'number_available': 100,
        'price': 1999,
        'description': 'Supporters',
    },
]


class Command(BaseCommand):
    help = 'Create Sponsorship Packages in the DB'

    def handle(self, *args, **options):

        for i, package in enumerate(PACKAGES):
            name = package.pop('name')
            SponsorshipPackage.objects.update_or_create(
                name=name,
                defaults=dict(
                    order=i,
                    currency='$',
                    short_description=package['description'],
                    **package))
