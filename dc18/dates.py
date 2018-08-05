import datetime

ORGA_ARRIVE_ON_OR_AFTER = datetime.date(2018, 7, 19)
ARRIVE_ON_OR_AFTER = datetime.date(2018, 7, 21)
LEAVE_ON_OR_BEFORE = datetime.date(2018, 8, 6)

T_SHIRT_SWAP_ON_OR_AFTER = datetime.date(2018, 8, 2)


def meals(orga=False):
    day = ARRIVE_ON_OR_AFTER
    while day <= LEAVE_ON_OR_BEFORE:
        yield ('breakfast', day)
        if day < LEAVE_ON_OR_BEFORE:
            yield ('lunch', day)
            yield ('dinner', day)
        day += datetime.timedelta(days=1)


def nights(orga=False):
    day = ARRIVE_ON_OR_AFTER
    if orga:
        day = ORGA_ARRIVE_ON_OR_AFTER
    while day < LEAVE_ON_OR_BEFORE:
        yield day
        day += datetime.timedelta(days=1)
