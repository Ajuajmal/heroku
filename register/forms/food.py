from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout

from dc18.prices import MEAL_PRICES
from register.dates import meal_choices
from register.models.food import Food


class FoodForm(forms.Form):
    meals = forms.MultipleChoiceField(
        label='I want to eat catered food for these meals:',
        choices=meal_choices(),
        widget=forms.CheckboxSelectMultiple,
        help_text="If you don't have a food bursary, meal prices are: "
                  "Breakfast {breakfast} USD, Lunch {lunch} USD, Dinner "
                  "{dinner} USD.".format(**MEAL_PRICES),
        required=False,
    )
    diet = forms.ChoiceField(
        label='My diet',
        choices=Food.DIETS.items(),
        required=False,
    )
    gluten_free = forms.BooleanField(
        label="I require Gluten-Free food",
        required=False,
    )
    special_diet = forms.CharField(
        label='Details of my special dietary needs',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
        self.helper.layout = Layout(
            Field('meals', id='meals'),
            Field('diet', id='diet'),
            Field('gluten_free', id='gluten_free'),
            Field('special_diet', id='special_diet'),
        )

    def clean(self):
        cleaned_data = super().clean()

        if (cleaned_data.get('diet') == 'other' and
                not cleaned_data.get('special_diet')):
            self.add_error('special_diet', 'Required when diet is "other"')
