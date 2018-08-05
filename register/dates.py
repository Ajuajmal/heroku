import datetime

from dc18.dates import meals, nights


def parse_date(date):
    return datetime.date(*(int(part) for part in date.split('-')))


def meal_choices(orga=False):
    for meal, date in meals(orga=orga):
        date = date.isoformat()
        yield ('{}_{}'.format(meal, date),
               '{} {}'.format(meal.title(), date))


def night_choices(orga=False):
    for date in nights(orga=orga):
        date = date.isoformat()
        yield ('night_{}'.format(date), 'Night of {}'.format(date))


def get_ranges_for_dates(dates):
    """Get ranges of consecutive dates for the given set of dates"""
    one = datetime.timedelta(days=1)

    ranges = []

    range_start = None
    range_end = None
    for date in sorted(dates):
        if range_start is None:
            range_start = date
        else:
            if date != range_end + one:
                # dates not consecutive, save old range and start new one
                ranges.append([range_start, range_end])
                range_start = date

        range_end = date

    ranges.append([range_start, range_end])
    return ranges
