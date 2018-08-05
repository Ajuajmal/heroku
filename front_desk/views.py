from collections import OrderedDict
import datetime
from itertools import repeat
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView

from dc18.dates import (
    ARRIVE_ON_OR_AFTER, LEAVE_ON_OR_BEFORE, T_SHIRT_SWAP_ON_OR_AFTER,
    meals as dc18_meals)
from dc18.prices import MEAL_PRICES, invoice_user
from register.dates import parse_date
from register.models import Accomm, Attendee, Food, Meal
from front_desk.forms import (
    CashInvoicePaymentForm, CheckInForm, CheckOutForm, FoodForm,
    RegisterOnSiteForm, SearchForm, TShirtForm)
from front_desk.models import CheckIn
from invoices.models import Invoice

log = logging.getLogger(__name__)


class CheckInPermissionMixin(PermissionRequiredMixin):
    permission_required = 'front_desk.change_checkin'


class CashBoxPermissionMixin(PermissionRequiredMixin):
    permission_required = 'invoices.change_invoice'


class Dashboard(CheckInPermissionMixin, TemplateView):
    template_name = 'front_desk/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SearchForm(data=self.request.GET)

        q = None
        if form.is_valid():
            q = form.cleaned_data['q']

        results = self.search_attendees(q)
        # Strip duplicates while maintaining order
        results = list(OrderedDict(zip(results, repeat(None))))

        context.update({
            'view': self,
            'form': form,
            'results': results[:20],
            'num_results': len(results),
        })
        return context

    def search_attendees(self, query):
        if not query:
            return

        yield from Attendee.objects.filter(user__username=query)

        if '@' in query:
            yield from Attendee.objects.filter(user__email=query)

        if ' ' in query:
            first, last = query.split(' ', 1)
            yield from Attendee.objects.filter(
                user__first_name__iexact=first,
                user__last_name__iexact=last,
            )
        yield from Attendee.objects.filter(user__username__icontains=query)
        yield from Attendee.objects.filter(user__email__icontains=query)
        yield from Attendee.objects.filter(user__first_name__icontains=query)
        yield from Attendee.objects.filter(user__last_name__icontains=query)


class CheckInView(CheckInPermissionMixin, SingleObjectMixin, FormView):
    template_name = 'front_desk/check_in.html'
    form_class = CheckInForm

    model = Attendee
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendee = self.object
        initial_tshirt = {
            'size': attendee.t_shirt_size,
            'cut': attendee.t_shirt_cut,
        }

        t_shirt = 'No T-Shirt'
        if attendee.t_shirt_cut:
            t_shirt = ' '.join((
                Attendee.T_SHIRT_CUTS[attendee.t_shirt_cut],
                Attendee.T_SHIRT_SIZES[attendee.t_shirt_size],
            ))

        try:
            accomm = attendee.accomm
        except Accomm.DoesNotExist:
            accomm = None

        dates = sorted(set(date for meal, date in dc18_meals(orga=True)))
        meal_labels = ['Breakfast', 'Lunch', 'Dinner']

        try:
            food = attendee.food
        except Food.DoesNotExist:
            meals = None
        else:
            meals = []
            for meal, meal_label in Meal.MEALS.items():
                cur_meal = []
                meal_dates = [entry.date
                              for entry in food.meals.filter(meal=meal)]
                for d in dates:
                    cur_meal.append((d, d in meal_dates))
                meals.append((meal_label, cur_meal))

        today = datetime.date.today()
        context.update({
            'accomm': accomm,
            'invoices': Invoice.objects.filter(recipient=attendee.user),
            'dates': dates,
            'meal_labels': meal_labels,
            'meals': meals,
            't_shirt': t_shirt,
            't_shirt_form': TShirtForm(
                initial=initial_tshirt,
                username=attendee.user.username),
            't_shirt_swap_available': T_SHIRT_SWAP_ON_OR_AFTER <= today,
            'T_SHIRT_SWAP_ON_OR_AFTER': T_SHIRT_SWAP_ON_OR_AFTER,
        })
        return context

    def get_initial(self):
        try:
            check_in = self.object.check_in
        except CheckIn.DoesNotExist:
            return {}
        return {
            't_shirt': check_in.t_shirt,
            'nametag': check_in.nametag,
            'notes': check_in.notes,
            'room_key': check_in.room_key,
            'key_card': check_in.key_card,
            'swag': check_in.swag,
        }

    def form_valid(self, form):
        attendee = self.object

        check_in, created = CheckIn.objects.update_or_create(
            attendee=attendee, defaults=form.cleaned_data)
        attendee.check_in = check_in

        log.info('Checked-in %s. Room Key: %s, Card: %s',
                 attendee.user.username, check_in.room_key, check_in.key_card)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('front_desk')


class CheckOutView(CheckInPermissionMixin, SingleObjectMixin, FormView):
    template_name = 'front_desk/check_out.html'
    form_class = CheckOutForm

    model = Attendee
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_initial(self):
        check_in = self.object.check_in
        return {
            'returned_key': check_in.returned_key,
            'returned_card': check_in.returned_card,
            'notes': check_in.notes,
        }

    def form_valid(self, form):
        attendee = self.object

        data = form.cleaned_data
        data['checked_out'] = True

        check_in, created = CheckIn.objects.update_or_create(
            attendee=attendee, defaults=data)
        attendee.check_in = check_in

        log.info('Checked-Out %s. Returned Key: %s, Card: %s',
                 attendee.user.username, check_in.returned_key,
                 check_in.returned_card)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('front_desk')


class ChangeFoodView(CashBoxPermissionMixin, SingleObjectMixin, FormView):
    form_class = FoodForm
    template_name = 'front_desk/change_food.html'

    model = Attendee
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.username = self.kwargs['username']
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prices'] = MEAL_PRICES
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.username = self.kwargs['username']
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        try:
            food = self.object.food
        except Food.DoesNotExist:
            pass
        else:
            kwargs['initial'] = {
                'meals': [meal.form_name for meal in food.meals.all()],
            }
        return kwargs

    def get_success_url(self):
        return reverse('front_desk.check_in',
                       kwargs={'username': self.username})

    def form_valid(self, form):
        data = form.cleaned_data
        user = self.object.user
        Invoice.objects.filter(
            recipient=user, status='new').update(status='canceled')
        if data['meals']:
            food, created = Food.objects.get_or_create(
                attendee=self.object, defaults={
                    'gluten_free': False,
                })
            stored_meals = set(food.meals.all())
            requested_meals = set()
            for meal in data['meals']:
                meal, date = meal.split('_')
                date = parse_date(date)
                requested_meals.add(Meal.objects.get(meal=meal, date=date))

            added_meals = requested_meals - stored_meals
            removed_meals = stored_meals - requested_meals
            food.meals.remove(*removed_meals)
            food.meals.add(*added_meals)
            log.info('Modified meals for %s: Adding %s. Removing %s',
                     self.username,
                     ', '.join(sorted(str(meal) for meal in added_meals)),
                     ', '.join(sorted(str(meal) for meal in removed_meals)))
            invoice_user(user, save=True)
        else:
            Food.objects.filter(attendee=self.object).delete()
            log.info('Cancelled all meals for %s', self.username)


        return super().form_valid(form)


class ChangeShirtView(CheckInPermissionMixin, FormView):
    form_class = TShirtForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.username = self.kwargs['username']
        kwargs['username'] = self.username
        return kwargs

    def get_success_url(self):
        return reverse('front_desk.check_in',
                       kwargs={'username': self.username})

    @transaction.atomic
    def form_valid(self, form):
        attendee = Attendee.objects.get(user__username=self.username)
        cut = form.cleaned_data['cut']
        size = form.cleaned_data['size']

        if not cut:
            size = ''
        if not size:
            cut = ''

        log.info('T-Shirt swap for %s: %s %s -> %s %s',
                 self.username, attendee.t_shirt_cut, attendee.t_shirt_size,
                 cut, size)

        attendee.t_shirt_cut = cut
        attendee.t_shirt_size = size
        attendee.save()

        return super().form_valid(form)


class RegisterOnSite(CheckInPermissionMixin, FormView):
    form_class = RegisterOnSiteForm
    template_name = 'front_desk/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'ARRIVE_ON_OR_AFTER': ARRIVE_ON_OR_AFTER,
            'LEAVE_ON_OR_BEFORE': LEAVE_ON_OR_BEFORE,
        })
        return context

    @transaction.atomic
    def form_valid(self, form):
        username = form.cleaned_data['username']
        self.username = username
        email = form.cleaned_data['email']

        names = form.cleaned_data['name'].split(None, 1)
        if len(names) > 1:
            first_name, last_name = names
        else:
            first_name, last_name = names[0], ''

        user = get_user_model().objects.create_user(
            username=username, email=email, first_name=first_name,
            last_name=last_name)
        Attendee.objects.create(
            user=user, nametag_3=username, arrival=datetime.datetime.now(),
            departure=form.cleaned_data['departure'], announce_me=False,
            register_announce=False, register_discuss=False,
            final_dates=True, reconfirm=True)

        log.info('Registered on-site: %s', username)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('front_desk.check_in',
                       kwargs={'username': self.username})


class CashInvoicePayment(CashBoxPermissionMixin, SingleObjectMixin, FormView):
    form_class = CashInvoicePaymentForm
    template_name = 'front_desk/cash_invoice_payment.html'

    model = Invoice
    slug_field = 'reference_number'
    slug_url_kwarg = 'ref'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

    def form_valid(self, form):
        invoice = self.object
        invoice.transaction_id = 'Cash: {}'.format(
            form.cleaned_data['receipt_number'])
        invoice.status = 'paid'
        invoice.save()

        log.info('Recieved cash-payment for %s: %s',
                 invoice.recipient.username, invoice.transaction_id)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('front_desk.check_in',
                       kwargs={'username': self.object.recipient.username})
