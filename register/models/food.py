from collections import OrderedDict

from django.db import models

from register.models.attendee import Attendee


class Meal(models.Model):
    MEALS = OrderedDict((
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ))

    date = models.DateField(db_index=True)
    meal = models.CharField(max_length=16)

    @property
    def form_name(self):
        return '{}_{}'.format(self.meal, self.date.isoformat())

    def __str__(self):
        return '{}: {}'.format(self.date.isoformat(), self.meal)

    class Meta:
        ordering = ['date']
        unique_together = ('date', 'meal')


class Food(models.Model):
    DIETS = OrderedDict((
        ('', 'I will be happy to eat whatever is provided'),
        ('vegetarian', "I am lacto-ovo vegetarian, don't provide "
                       "meat/fish for me"),
        ('vegan', "I am strict vegetarian (vegan), don't provide any "
                  "animal products for me"),
        ('other', 'Other, described below'),
    ))

    attendee = models.OneToOneField(Attendee, related_name='food',
                                    on_delete=models.CASCADE)

    meals = models.ManyToManyField(Meal)
    diet = models.CharField(max_length=16, blank=True)
    gluten_free = models.BooleanField()
    special_diet = models.TextField(blank=True)

    def __str__(self):
        return 'Attendee <{}>'.format(self.attendee.user.username)
