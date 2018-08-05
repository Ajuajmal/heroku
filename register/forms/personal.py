import re

from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout
from django_countries import Countries
from django_countries.fields import LazyTypedChoiceField
from django_countries.widgets import CountrySelectWidget

from register.models.attendee import Attendee


T_SHIRT_CUTS = Attendee.T_SHIRT_CUTS.copy()
T_SHIRT_CUTS[''] = "I don't want a T-shirt"
T_SHIRT_CHART_LINK = (
    '<a href="https://wiki.debconf.org/wiki/DebConf18/TshirtSizes" '
    'target="blank">t-shirt sizes chart</a>')


class OptionalCountries(Countries):
    first = ('__',)
    override = {'__': 'Decline to state'}


class PersonalInformationForm(forms.Form):
    t_shirt_cut = forms.ChoiceField(
        label='My t-shirt cut',
        choices=T_SHIRT_CUTS.items(),
        required=False,
    )
    t_shirt_size = forms.ChoiceField(
        label='My t-shirt size',
        choices=Attendee.T_SHIRT_SIZES.items(),
        help_text='Refer to the ' + T_SHIRT_CHART_LINK + '.',
        required=False,
    )
    gender = forms.ChoiceField(
        label='My gender',
        choices=Attendee.GENDERS.items(),
        help_text='For diversity statistics.',
        required=False,
    )
    country = LazyTypedChoiceField(
        label='The country I call home',
        help_text='For diversity statistics.',
        choices=OptionalCountries(),
        required=False,
        widget=CountrySelectWidget(),
    )
    languages = forms.CharField(
        label='The languages I speak',
        help_text='We will list these on your name-tag.',
        initial='en',
        max_length=50,
        required=False,
    )
    pgp_fingerprints = forms.CharField(
        label='My PGP key fingerprints for keysigning',
        help_text='Optional. One fingerprint per line, if you want to take '
                  'part in <a href="https://wiki.debconf.org/wiki/DebConf18/'
                  'Keysigning">the continuous keysigning party</a>. '
                  'Will appear on nametags and a keysigning notesheet, with '
                  'no verification done by the conference organisers.<br>'
                  'Just provide the fingerprints, e.g. <code>1234 5678 90AB '
                  'CDEF 0000  1111 2222 3333 4444 5555</code>',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
        self.helper.layout = Layout(
            Fieldset(
                'T-shirt',
                Field('t_shirt_cut', id='tshirt-cut'),
                Field('t_shirt_size', id='tshirt-size'),
            ),
            Field('gender'),
            Field('country'),
            Field('languages'),
            Field('pgp_fingerprints'),
        )

    def clean_t_shirt_size(self):
        if not self.cleaned_data.get('t_shirt_cut'):
            return ''
        return self.cleaned_data.get('t_shirt_size')

    def clean_pgp_fingerprints(self):
        fingerprints = self.cleaned_data.get('pgp_fingerprints').strip()
        if not fingerprints:
            return ''
        if '-----BEGIN' in fingerprints:
            raise ValidationError('Only fingerprints, not keys, please')
        cleaned = []
        for line in fingerprints.splitlines():
            fp = line.strip().upper().replace(' ', '')
            if fp.startswith('0x'):
                fp = fp[2:]
            if not re.match(r'^[0-9A-F]{40}$', fp):
                raise ValidationError(
                    '{} is not a PGP fingerprint'.format(line))
            cleaned.append('{} {} {} {} {}  {} {} {} {} {}'.format(
                *[fp[i:i + 4] for i in range(0, 40, 4)]))
        return '\n'.join(cleaned)

    def clean(self):
        cleaned_data = super().clean()
        t_shirt_cut = cleaned_data.get('t_shirt_cut')
        t_shirt_size = cleaned_data.get('t_shirt_size')
        if t_shirt_cut and not t_shirt_size:
            self.add_error('t_shirt_size', "Select a size, please")
