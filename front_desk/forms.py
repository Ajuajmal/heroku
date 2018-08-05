from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import Form, fields, widgets
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, HTML, Layout, Submit

from dc18.prices import MEAL_PRICES
from register.dates import meal_choices
from register.models.attendee import Attendee


class SearchForm(Form):
    q = fields.CharField(label='Find Users', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.include_media = False
        self.helper.add_input(Submit('search', 'Search'))


class CheckInForm(Form):
    t_shirt = fields.BooleanField(label='T-shirt', required=False)
    swag = fields.BooleanField(label='Swag Bag', required=False)
    nametag = fields.BooleanField(required=False)
    room_key = fields.BooleanField(required=False)
    key_card = fields.CharField(required=False)
    notes = fields.CharField(
        required=False,
        widget=widgets.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.layout = Layout(
            't_shirt',
            'swag',
            'nametag',
            'room_key',
            'key_card',
        )
        self.helper.layout.fields += [
            'notes',
            ButtonHolder(
                Submit('submit', 'Check In'),
                HTML('<a href="{}" class="btn btn-secondary">Cancel</a>'
                     .format(reverse('front_desk'))),
            ),
        ]


class CheckOutForm(Form):
    returned_key = fields.BooleanField(
        label='Returned Room Key', required=False)
    returned_card = fields.BooleanField(
        label='Returned Dorm Card', required=False)
    notes = fields.CharField(
        required=False,
        widget=widgets.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.layout = Layout(
            'returned_key',
            'returned_card',
            'notes',
            ButtonHolder(
                Submit('submit', 'Check Out'),
                HTML('<a href="{}" class="btn btn-secondary">Cancel</a>'
                     .format(reverse('front_desk'))),
            ),
        )


class TShirtForm(Form):
    cut = fields.ChoiceField(
        label='T-shirt cut',
        choices=Attendee.T_SHIRT_CUTS.items(),
        required=False,
    )
    size = fields.ChoiceField(
        label='T-shirt size',
        choices=Attendee.T_SHIRT_SIZES.items(),
        required=False,
    )

    def __init__(self, *args, username, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse(
            'front_desk.change_shirt', kwargs={'username': username})
        self.helper.include_media = False
        self.helper.add_input(Submit('update', 'Update Shirt'))


class RegisterOnSiteForm(Form):
    name = fields.CharField()
    username = fields.CharField(validators=[
        validators.RegexValidator(
            r'^[\w.@+-]+$',
            'Enter a valid username. This value may contain only letters, '
            'numbers and @/./+/-/_ characters.',
            'invalid')
        ])
    email = fields.EmailField()
    departure = fields.DateTimeField()
    coc_ack = fields.BooleanField(label='Agrees to abide by CoC')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        layout = self.helper.build_default_layout(self)
        layout.fields.append(
            ButtonHolder(
                Submit('register', 'Register'),
                HTML('<a href="{}" class="btn btn-secondary">Cancel</a>'
                     .format(reverse('front_desk'))),
            )
        )
        self.helper.add_layout(layout)

    def clean_username(self):
        username = self.cleaned_data['username']
        if get_user_model().objects.filter(username=username).exists():
            raise ValidationError('User with this username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError('User with this email already exists')
        return email


class CashInvoicePaymentForm(Form):
    receipt_number = fields.IntegerField()
    amount = fields.DecimalField(max_digits=8, decimal_places=2,
                                 validators=[validators.MinValueValidator(0)])

    def __init__(self, *args, instance, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.helper = FormHelper()
        self.helper.include_media = False
        layout = self.helper.build_default_layout(self)
        layout.fields.append(
            ButtonHolder(
                Submit('pay', 'Record Payment'),
                HTML(
                    '<a href="{}" class="btn btn-secondary">Cancel</a>'
                    .format(reverse(
                        'front_desk.check_in',
                        kwargs={'username': self.instance.recipient.username},
                    )))))
        self.helper.add_layout(layout)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        expected_amount = self.instance.total
        if amount != expected_amount:
            raise ValidationError('The invoice was for USD {}'
                                  .format(expected_amount))
        return amount


class FoodForm(Form):
    meals = fields.MultipleChoiceField(
        choices=meal_choices(),
        widget=widgets.CheckboxSelectMultiple,
        help_text="If you don't have a food bursary, meal prices are: "
                  "Breakfast {breakfast} USD, Lunch {lunch} USD, "
                  "Dinner {dinner} USD.".format(**MEAL_PRICES),
        required=False,
    )

    def __init__(self, *args, instance, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.layout = Layout(
            Field('meals', id='meals'),
            HTML('<div class="alert alert-success">'
                 'Total: USD$<span id="total">0.00</span>. '
                 '<span style="display: none">'
                 'Difference: USD$<span id="delta">0.00</span>'
                 '</span></div>'),
            ButtonHolder(
                Submit('save', 'Save'),
                HTML(
                    '<a href="{}" class="btn btn-secondary">Cancel</a>'
                    .format(reverse(
                        'front_desk.check_in',
                        kwargs={'username': self.instance.user.username},
                    )))),
        )
