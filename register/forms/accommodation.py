from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, HTML

from dc18.prices import ACCOMM_INVOICE_INFO
from register.dates import night_choices


class AccommodationForm(forms.Form):
    accomm = forms.BooleanField(
        label='I need conference-organised accommodation',
        widget=forms.Select(choices=(
            (False, 'No, I will find my own accommodation'),
            (True, 'Yes, I need accommodation'),
        )),
        required=False,
    )
    nights = forms.MultipleChoiceField(
        label="I'm requesting accommodation for these nights:",
        help_text='The "night of" is the date of the day before a night. '
                  'So accommodation on the night of 6 Aug ends on the '
                  'morning of the 7th.',
        choices=night_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    requirements = forms.CharField(
        label='Do you have any particular accommodation requirements?',
        help_text='Anything that you want us to consider for room attribution '
                  'should be listed here (ex. "I want to be with Joe Hill", '
                  '"I snore", "I go to bed early")',
        required=False,
    )
    special_needs = forms.CharField(
        label='My special needs',
        help_text='Wheelchair access or other any other needs we should be '
                  'aware of.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    childcare = forms.BooleanField(
        label='I need childcare for my kid(s)',
        required=False,
    )
    childcare_needs = forms.CharField(
        label='The childcare services I need are',
        help_text='How many hours a day? All the conference or only part of '
                  'it? etc.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    childcare_details = forms.CharField(
        label='Important informations about my kid(s)',
        help_text='Number, ages, languages spoken, special needs, etc.',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
    )
    family_usernames = forms.CharField(
        label='Usernames of my family members, '
              'who have registered separately',
        help_text="One per line. This isn't validated.",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

        accomm_details = Fieldset(
            'Accommodation Details',
            'nights',
            'requirements',
            css_id='accomm-details',
        )
        self.helper.layout = Layout(
            HTML(
                '<p>By default, the accommodation provided is in <a href="'
                'https://wiki.debconf.org/wiki/DebConf18/Accommodation#On-site'
                '" target="_blank">shared classroom dorms on premises</a>. '
                'The cost is {} USD/night for attendees who do not receive a '
                'bursary.</p>'.format(ACCOMM_INVOICE_INFO['unit_price'])),
            Field('accomm', id='accomm'),
            accomm_details,
            Field('childcare', id='childcare'),
            Fieldset(
                'Childcare Details',
                'childcare_needs',
                'childcare_details',
                css_id='childcare-details',
            ),
            Field('special_needs'),
            Field('family_usernames'),
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('childcare'):
            if not cleaned_data.get('childcare_needs'):
                self.add_error('childcare_needs',
                               'Please provide us with your needs.')
            if not cleaned_data.get('childcare_details'):
                self.add_error(
                    'childcare_details',
                    "Please provide us with your children's details.")

        if not cleaned_data.get('accomm'):
            return cleaned_data

        if not cleaned_data.get('nights'):
            self.add_error(
                'accomm',
                'Please select the nights you require accommodation for.')

        return cleaned_data
