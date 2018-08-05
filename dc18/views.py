from collections import Counter, Iterable, OrderedDict, defaultdict
import csv

from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin,
)
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.generic import ListView, TemplateView

from wafer.talks.models import Talk, Track
from wafer.schedule.views import ScheduleView

from bursary.models import Bursary, BURSARY_STATUS_CHOICES
from front_desk.models import CheckIn
from register.models import Accomm, Attendee, Meal, user_is_registered


class CSVExportView(ListView):
    """Export the given columns for the model as CSV."""
    columns = None
    filename = None

    def get_data_line(self, instance):
        ret = []
        for column in self.columns:
            obj = instance
            for component in column.split('.'):
                try:
                    obj = getattr(obj, component)
                except ObjectDoesNotExist:
                    obj = '%s missing!' % component
                    break
                except AttributeError:
                    obj = getattr(self, component)(obj)
                if not obj:
                    break
                if callable(obj):
                    obj = obj()
            if (not isinstance(obj, (str, bytes))
                    and isinstance(obj, Iterable)):
                ret.extend(str(i) for i in obj)
            else:
                ret.append(str(obj))

        return ret

    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="%s"' % self.filename
        )

        writer = csv.writer(response)
        writer.writerow(self.columns)
        for instance in context['object_list']:
            writer.writerow(self.get_data_line(instance))

        return response


class AttendeeAdminMixin(PermissionRequiredMixin):
    permission_required = 'register.change_attendee'


class AttendeeBadgeExport(AttendeeAdminMixin, CSVExportView):
    model = Attendee
    filename = "attendee_badges.csv"
    ordering = ('user__username',)
    columns = [
        'user.username', 'reconfirm', 'user.email', 'user.get_full_name',
        'nametag_2', 'nametag_3', 'languages', 'food.diet',
    ]


class AttendeeAccommExport(AttendeeAdminMixin, CSVExportView):
    model = Accomm
    filename = "attendee_accommodation.csv"
    ordering = ('attendee__user__username',)
    columns = [
        'attendee.user.username', 'attendee.user.get_full_name',
        'attendee.user.email', 'attendee.reconfirm', 'attendee.paid',
        'attendee.user.bursary.accommodation_status', 'attendee.gender',
        'attendee.country', 'requirements', 'special_needs',
        'family_usernames', 'get_checkin_checkouts', 'room',
    ]


class TalksExport(PermissionRequiredMixin, CSVExportView):
    model = Talk
    permission_required = 'talks.edit_private_notes'
    filename = "talk_evaluations.csv"
    ordering = ("talk_id",)
    columns = [
        'talk_id', 'title', 'get_authors_display_name', 'abstract',
        'talk_type.name', 'track.name', 'get_status_display', 'review_score',
        'review_count', 'notes', 'private_notes', 'all_review_comments',
    ]

    def all_review_comments(self, talk):
        return [
            "(%s) %s" % (review.reviewer.username, review.notes.raw)
            for review in talk.reviews.all()
            if review.notes.raw
        ]


def clean_almostdicts(value):
    if not isinstance(value, dict):
        return value

    return OrderedDict(
        (k, clean_almostdicts(v)) for k, v in value.items()
    )


class FoodExport(AttendeeAdminMixin, CSVExportView):
    model = Meal
    filename = "meals.csv"
    ordering = ('date', 'meal',)
    columns = [
        'date', 'meal', 'total', 'total_unconfirmed',
        'regular', 'gluten_free', 'vegetarian', 'vegetarian_gf',
        'vegan', 'vegan_gf', 'other', 'other_details',
    ]

    def render_to_response(self, context, **response_kwargs):
        self._confirmed_attendees = {}
        return super().render_to_response(context, **response_kwargs)

    def attendee_confirmed(self, attendee_id):
        if attendee_id not in self._confirmed_attendees:
            if CheckIn.objects.filter(attendee_id=attendee_id).exists():
                return True

            attendee = Attendee.objects.get(id=attendee_id)
            paid = attendee.paid()

            try:
                bursary = Bursary.objects.get(user=attendee.user)
            except Bursary.DoesNotExist:
                bursary = Bursary()

            confirmed = any((
                not bursary.request_any and attendee.billable() and paid,
                not bursary.request_any and not attendee.billable() and attendee.final_dates,
                bursary.request_any and bursary.status_in(None, ['accepted']),
                attendee.reconfirm,
            ))
            self._confirmed_attendees[attendee_id] = confirmed
        return self._confirmed_attendees[attendee_id]

    def get_data_line(self, meal):
        row = {
            'date': meal.date.isoformat(),
            'meal': meal.meal,
            'total': 0,
            'total_unconfirmed': meal.food_set.count(),
            'regular': 0,
            'gluten_free': 0,
            'vegetarian': 0,
            'vegetarian_gf': 0,
            'vegan': 0,
            'vegan_gf': 0,
            'other': 0,
            'other_details': [],
        }

        for food in meal.food_set.all():
            if not self.attendee_confirmed(food.attendee_id):
                continue

            diet = food.diet
            if diet == '':
                diet = 'gluten_free' if food.gluten_free else 'regular'
            elif diet == 'other':
                details = [food.attendee.user.username]
                if food.gluten_free:
                    details.append('Gluten Free')
                details.append(food.special_diet)
                row['other_details'].append(': '.join(details))
            elif food.gluten_free:
                diet = diet + '_gf'
            row[diet] += 1
            row['total'] += 1

        row['other_details'] = ', '.join(row['other_details'])
        return [row.get(key) for key in self.columns]


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'dc18/statistics.html'
    cache_key = 'dc18:statistics'
    cache_timeout = 30*60 if not settings.DEBUG else 10

    def get_context_data(self, **kwargs):
        retval = cache.get(self.cache_key)
        if retval:
            return retval

        attendees = Attendee.objects.all()
        attendees_count = len(attendees)
        attendees_registered = 0
        attendees_confirmed = 0
        attendees_by_country = defaultdict(Counter)
        attendees_by_language = defaultdict(Counter)
        attendees_by_gender = defaultdict(Counter)
        fees = defaultdict(Counter)
        tshirts = defaultdict(Counter)
        tshirts_total = Counter()
        accomm_total = 0
        accomm_confirmed = 0
        accommodation = defaultdict(Counter)
        food_total = 0
        food_confirmed = 0
        food_restrictions = defaultdict(Counter)
        food_restrictions['No restrictions']  # get that on top of the list
        meals = defaultdict(
            lambda: defaultdict(Counter)
        )
        for attendee in attendees:
            if attendee.completed_register_steps >= 10:
                attendees_registered += 1
            else:
                continue

            paid = attendee.paid()

            try:
                bursary = Bursary.objects.get(user=attendee.user)
            except Bursary.DoesNotExist:
                bursary = Bursary()

            checked_in = CheckIn.objects.filter(attendee=attendee).exists()

            reconfirm = any((
                checked_in,
                not bursary.request_any and attendee.billable() and paid,
                not bursary.request_any and not attendee.billable() and attendee.final_dates,
                bursary.request_any and bursary.status_in(None, ['accepted']),
                attendee.reconfirm,
            ))

            if reconfirm:
                attendees_confirmed += 1

            fees[attendee.fee]['all'] += 1
            if paid:
                fees[attendee.fee]['paid'] += 1

            if attendee.t_shirt_cut:
                cut = attendee.t_shirt_cut
                tshirts[attendee.t_shirt_size]['%s_all' % cut] += 1
                tshirts_total['%s_all' % cut] += 1
                if reconfirm:
                    tshirts[attendee.t_shirt_size]['%s_confirmed' % cut] += 1
                    tshirts_total['%s_confirmed' % cut] += 1

            attendees_by_country[attendee.country]['all'] += 1
            if reconfirm:
                attendees_by_country[attendee.country]['confirmed'] += 1

            attendees_by_gender[attendee.gender]['all'] += 1
            if reconfirm:
                attendees_by_gender[attendee.gender]['confirmed'] += 1

            languages = set(
                attendee.languages.lower()
                .replace(',', ' ')
                .replace('/', ' ')
                .replace(';', ' ')
                .split()
            )
            for language in languages:
                attendees_by_language[language]['all'] += 1
                if reconfirm:
                    attendees_by_language[language]['confirmed'] += 1

            try:
                accomm = attendee.accomm
                if not accomm.nights.exists():
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                pass
            else:
                accomm_total += 1
                if reconfirm:
                    accomm_confirmed += 1

                for night in attendee.accomm.nights.all():
                    accommodation[night]['all'] += 1
                    if reconfirm:
                        accommodation[night]['confirmed'] += 1

            try:
                food = attendee.food
                if not food.meals.exists():
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                pass
            else:
                food_total += 1
                if reconfirm:
                    food_confirmed += 1

                markers = []
                if food.diet:
                    markers.append(food.diet.title())
                if food.gluten_free:
                    markers.append('(gluten-free)')
                if not markers:
                    markers = ['No restrictions']

                food_restrictions[' '.join(markers)]['all'] += 1
                if reconfirm:
                    food_restrictions[' '.join(markers)]['confirmed'] += 1

                for meal in food.meals.all():
                    meals[meal.date][meal.meal]['all'] += 1
                    if reconfirm:
                        meals[meal.date][meal.meal]['confirmed'] += 1

        bursaries_by_status = defaultdict(Counter)
        bursaries_travel = Counter()
        for bursary in Bursary.objects.all():
            if not user_is_registered(bursary.user):
                continue
            for type in ('food', 'accommodation', 'travel'):
                if getattr(bursary, 'request_%s' % type):
                    status = getattr(bursary, '%s_status' % type)
                    bursaries_by_status[type]['all'] += 1
                    bursaries_by_status[type][status] += 1
                    if type == 'travel':
                        amount = bursary.travel_bursary
                        bursaries_travel['all'] += amount
                        bursaries_travel[status] += amount

        # Prepare for presentation
        fees = OrderedDict(
            (label, fees[key])
            for key, label in Attendee.FEES.items()
        )
        attendees_by_country = sorted(
            attendees_by_country.items(), key=lambda x: (-x[1]['all'], x[0])
        )
        attendees_by_gender = sorted(
            attendees_by_gender.items(), key=lambda x: (-x[1]['all'], x[0])
        )
        attendees_by_language = sorted(
            attendees_by_language.items(), key=lambda x: (-x[1]['all'], x[0])
        )
        tshirts = OrderedDict(
            (label, tshirts[key])
            for key, label in Attendee.T_SHIRT_SIZES.items()
            if key
        )
        accommodation = OrderedDict(
            sorted(
                (night.date, counts)
                for night, counts in accommodation.items()
            )
        )
        meal_labels = list(Meal.MEALS.values())
        meals = OrderedDict(
            (day, [day_meals[key] for key in Meal.MEALS])
            for day, day_meals in sorted(meals.items())
        )

        bursary_statuses = ['All'] + [
            choice[0].title() for choice in BURSARY_STATUS_CHOICES
        ]

        bursaries_by_status = OrderedDict(
            (type.title(), OrderedDict(
                (status.lower(), counter[status.lower()])
                for status in bursary_statuses
            ))
            for type, counter in bursaries_by_status.items()
        )
        bursaries_travel = OrderedDict(
            (status, bursaries_travel[status.lower()])
            for status in bursary_statuses
        )

        retval = clean_almostdicts({
            'attendees_count': attendees_count,
            'attendees_registered': attendees_registered,
            'attendees_confirmed': attendees_confirmed,
            'fees': fees,
            'tshirts': tshirts,
            'tshirts_total': tshirts_total,
            'attendees_by_country': attendees_by_country,
            'attendees_by_language': attendees_by_language,
            'attendees_by_gender': attendees_by_gender,
            'accomm_total': accomm_total,
            'accomm_confirmed': accomm_confirmed,
            'accommodation': accommodation,
            'food_total': food_total,
            'food_confirmed': food_confirmed,
            'food_restrictions': food_restrictions,
            'genders': Attendee.GENDERS,
            'meal_labels': meal_labels,
            'meals': meals,
            'bursary_statuses': bursary_statuses,
            'bursaries_by_status': bursaries_by_status,
            'bursaries_travel': bursaries_travel,
        })

        cache.set(self.cache_key, retval, self.cache_timeout)
        return retval


class RobotsView(TemplateView):
    template_name = 'dc18/robots.txt'
    content_type = 'text/plain; charset=UTF-8'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SANDBOX'] = settings.SANDBOX
        return context


class DebConfScheduleView(ScheduleView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracks'] = Track.objects.all()
        return context
