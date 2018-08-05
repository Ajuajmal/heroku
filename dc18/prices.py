import datetime
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from invoices.models import Invoice, InvoiceLine
from register.dates import get_ranges_for_dates


FEE_INVOICE_INFO = {
    'pro': {
        'reference': 'DC18-REG-PRO',
        'description': 'DebConf 18 Professional registration fee',
        'unit_price': 200,
    },
    'corp': {
        'reference': 'DC18-REG-CORP',
        'description': 'DebConf 18 Corporate registration fee',
        'unit_price': 500,
    },
}

MEAL_PRICES = {
    'breakfast': Decimal(3),
    'lunch': Decimal(5),
    'dinner': Decimal(5),
}

ACCOMM_INVOICE_INFO = {
    'reference': 'DC18-ACCOMM',
    'description': 'DebConf 18 on-site accommodation',
    'unit_price': 5,
}

TWD_EXCHANGE_RATE = 30


def invoice_user(user, force=False, save=False):
    from bursary.models import Bursary

    attendee = user.attendee

    try:
        bursary = user.bursary
    except Bursary.DoesNotExist:
        bursary = Bursary()

    lines = []
    fee_info = FEE_INVOICE_INFO.get(attendee.fee)
    if fee_info:
        fee_info['quantity'] = 1
        lines.append(InvoiceLine(**fee_info))

    try:
        accomm = attendee.accomm
    except ObjectDoesNotExist:
        accomm = None

    if accomm and not bursary.potential_bursary('accommodation'):
        for line in invoice_accomm(accomm):
            lines.append(InvoiceLine(**line))

    try:
        food = attendee.food
    except ObjectDoesNotExist:
        food = None

    if food and not bursary.potential_bursary('food'):
        for line in invoice_food(food):
            lines.append(InvoiceLine(**line))

    for paid_invoice in user.invoices.filter(status='paid', compound=False):
        lines.append(InvoiceLine(
            reference='INV#{}'.format(paid_invoice.reference_number),
            description='Previous Payment Received',
            unit_price=-paid_invoice.total,
            quantity=1,
        ))

    invoice = Invoice(
        recipient=user,
        status='new',
        date=timezone.now(),
        invoiced_entity=attendee.invoiced_entity,
        billing_address=attendee.billing_address
    )

    # Only save invoices if non empty
    if save and lines:
        invoice.save()

    total = 0
    for i, line in enumerate(lines):
        line.line_order = i
        total += line.total
        if save:
            line.invoice_id = invoice.id
            line.save()

    return {
        'invoice': invoice,
        'lines': lines,
        'total': total,
        'total_twd': total * TWD_EXCHANGE_RATE,
    }


def invoice_food(food):
    """Generate one invoice line per meal type per consecutive stay"""
    from register.models.food import Meal

    for meal, meal_label in Meal.MEALS.items():
        dates = [entry.date for entry in food.meals.filter(meal=meal)]
        if not dates:
            continue

        unit_price = MEAL_PRICES[meal]

        ranges = get_ranges_for_dates(dates)
        for first, last in ranges:
            n_meals = (last - first).days + 1

            if first != last:
                desc = "%s to %s" % (first, last)
            else:
                desc = str(first)

            full_desc = 'DebConf 18 %s (%s)' % (meal_label, desc)
            yield {
                'reference': 'DC18-%s' % meal.upper(),
                'description': full_desc,
                'unit_price': unit_price,
                'quantity': n_meals,
            }


def invoice_accomm(accomm):
    """Generate one invoice line per consecutive stay"""
    stays = get_ranges_for_dates(
        night.date for night in accomm.nights.all()
    )

    for first_night, last_night in stays:
        last_morning = last_night + datetime.timedelta(days=1)
        num_nights = (last_morning - first_night).days
        desc = "evening of %s to morning of %s" % (first_night,
                                                   last_morning)

        line = ACCOMM_INVOICE_INFO.copy()
        line['description'] += ' ({})'.format(desc)
        line['quantity'] = num_nights
        yield line
