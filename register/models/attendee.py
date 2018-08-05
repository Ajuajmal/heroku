from collections import OrderedDict

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from dc18 import prices

_pro_fee = prices.FEE_INVOICE_INFO['pro']['unit_price']
_corp_fee = prices.FEE_INVOICE_INFO['corp']['unit_price']


class Attendee(models.Model):
    FEES = OrderedDict((
        ('', 'Regular - Free'),
        ('pro', 'Professional - {} USD / {} TWD'.format(
            _pro_fee, _pro_fee * prices.TWD_EXCHANGE_RATE)),
        ('corp', 'Corporate - {} USD / {} TWD'.format(
            _corp_fee, _corp_fee * prices.TWD_EXCHANGE_RATE)),
    ))
    GENDERS = OrderedDict((
        ('', 'Decline to state'),
        ('m', 'Male'),
        ('f', 'Female'),
        ('n', 'Non-Binary'),
    ))
    T_SHIRT_SIZES = OrderedDict((
        ('', 'N/A'),
        ('xs', 'Extra Small'),
        ('s', 'Small'),
        ('m', 'Medium'),
        ('l', 'Large'),
        ('xl', 'Extra Large'),
        ('2xl', '2X Large'),
        ('3xl', '3X Large'),
        ('4xl', '4X Large'),
        ('5xl', '5X Large'),
    ))
    T_SHIRT_CUTS = OrderedDict((
        ('', 'N/A'),
        ('s', 'Straight cut'),
        ('w', "Women's fitted cut"),
    ))

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='attendee',
                                on_delete=models.PROTECT)

    # Contact information
    nametag_2 = models.CharField(max_length=50, blank=True)
    nametag_3 = models.CharField(max_length=50, blank=True)
    emergency_contact = models.TextField(blank=True)
    announce_me = models.BooleanField()
    register_announce = models.BooleanField()
    register_discuss = models.BooleanField()

    # Conference details
    coc_ack = models.BooleanField(default=False)
    fee = models.CharField(max_length=5, blank=True)
    arrival = models.DateTimeField(null=True, blank=True)
    departure = models.DateTimeField(null=True, blank=True)
    final_dates = models.BooleanField(default=False)
    reconfirm = models.BooleanField(default=False)

    # Personal information
    t_shirt_cut = models.CharField(max_length=1, blank=True)
    t_shirt_size = models.CharField(max_length=8, blank=True)
    gender = models.CharField(max_length=1, blank=True)
    country = models.CharField(max_length=2, blank=True)
    languages = models.CharField(max_length=50, blank=True)
    pgp_fingerprints = models.TextField(blank=True)

    # Billing
    invoiced_entity = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)

    # Misc
    notes = models.TextField(blank=True)
    completed_register_steps = models.IntegerField(default=0)

    def __str__(self):
        return 'Attendee <{}>'.format(self.user.username)

    def billable(self):
        """Is this user billable? (or paid)"""
        from bursary.models import Bursary

        try:
            bursary = self.user.bursary
        except Bursary.DoesNotExist:
            bursary = Bursary()

        if self.fee:
            return True

        try:
            if (self.food.meals.exists()
                    and not bursary.potential_bursary('food')):
                return True
        except ObjectDoesNotExist:
            pass

        try:
            if (self.accomm.nights.exists()
                    and not bursary.potential_bursary('accommodation')):
                return True
        except ObjectDoesNotExist:
            pass

        return False

    billable.boolean = True

    def paid(self):
        from dc18.prices import invoice_user
        invoices = self.user.invoices
        if invoices.filter(status='new').exists():
            return False

        invoice = invoice_user(self.user)
        return invoice['total'] <= 0

    paid.boolean = True

    @property
    def new_invoices(self):
        return self.user.invoices.filter(status='new')

    def save(self, *args, **kwargs):
        if self.arrival == '':
            self.arrival = None
        if self.departure == '':
            self.departure = None
        return super().save(*args, **kwargs)
