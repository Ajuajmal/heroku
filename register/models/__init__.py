from register.models.accommodation import Accomm, AccommNight
from register.models.attendee import Attendee
from register.models.food import Food, Meal


def user_is_registered(user):
    from register.views import STEPS
    last_step = len(STEPS) - 1
    return Attendee.objects.filter(
        user=user, completed_register_steps=last_step).exists()
