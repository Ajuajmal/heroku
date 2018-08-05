# -*- encoding: utf-8 -*-
from pathlib import Path

from django.urls import reverse_lazy

from wafer.settings import *

TIME_ZONE = 'Asia/Taipei'
USE_L10N = False
TIME_FORMAT = 'G:i'
SHORT_DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'
SHORT_DATETIME_FORMAT = 'Y-m-d H:i'

try:
    from localsettings import *
except ImportError:
    pass

root = Path(__file__).parent

ALLOWED_HOSTS = ['127.0.0.1']
INSTALLED_APPS = (
    'badges',
    'bursary',
    'dc18',
    'front_desk',
    'invoices',
    'news',
    'register',
    'django_countries',
    'paypal.standard.ipn',
) + INSTALLED_APPS

STATIC_ROOT = str(root / 'localstatic/')

STATICFILES_DIRS = (
    str(root / 'static'),
)

STATICFILES_STORAGE = (
    'whitenoise.django.GzipManifestStaticFilesStorage')

TEMPLATES[0]['DIRS'] = TEMPLATES[0]['DIRS'] + (
    str(root / 'templates'),
)


WAFER_MENUS += (
    {
        'menu': 'about',
        'label': 'About',
        'items': [
            {
                'menu': 'debconf',
                'label': 'About DebConf',
                'url': reverse_lazy('wafer_page', args=('about/debconf',))
            },
            {
                'menu': 'debian',
                'label': 'About Debian',
                'url': reverse_lazy('wafer_page', args=('about/debian',))
            },
            {
                'menu': 'registration_information',
                'label': 'Registration Information',
                'url': reverse_lazy('wafer_page', args=('about/registration',))
            },
            {
                'menu': 'bursaries',
                'label': 'Bursaries',
                'url': reverse_lazy('wafer_page', args=('about/bursaries',))
            },
            {
                'menu': 'visiting_hsinchu',
                'label': 'Visiting Hsinchu',
                'url': reverse_lazy(
                    'wafer_page', args=('about/visiting-hsinchu',))
            },
        ],
    },
    {
        'menu': 'sponsors_index',
        'label': 'Sponsors',
        'items': [
            {
                'menu': 'sponsors',
                'label': 'Our Sponsors',
                'url': reverse_lazy('wafer_sponsors')
            },
            {
                'menu': 'become_sponsor',
                'label': 'Become a Sponsor',
                'url': reverse_lazy('wafer_page', args=('sponsors/become-a-sponsor',))
            },
        ]
    },
    {
        'menu': 'schedule_index',
        'label': 'Schedule',
        'items': [
            {
                'menu': 'schedule',
                'label': 'Schedule',
                'url': reverse_lazy('wafer_full_schedule')
            },
            {
                'menu': 'mobile_schedule',
                'label': 'Mobile-Friendly Schedule',
                'url': reverse_lazy('wafer_page', args=('schedule/mobile',))
            },
            {
                'menu': 'important-dates',
                'label': 'Important Dates',
                'url': reverse_lazy('wafer_page', args=('schedule/important-dates',))
            },
            {
                'menu': 'cfp',
                'label': 'Call for Proposals',
                'url': reverse_lazy('wafer_page', args=('cfp',))
            },
            {
                'menu': 'confirmed_talks',
                'label': 'Confirmed Talks',
                'url': reverse_lazy('wafer_users_talks')
            },
        ]
    },
    {
        'menu': 'wiki_link',
        'label': 'Wiki',
        'url': 'https://wiki.debconf.org/wiki/DebConf18'
    },
    
    {
        'menu': 'contact',
        'label': 'Contact us',
        'url': reverse_lazy('wafer_page', args=('contact',))
    }

)

WAFER_DYNAMIC_MENUS = ()

ROOT_URLCONF = 'urls'

CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_FAIL_SILENTLY = not DEBUG

MARKITUP_FILTER = ('markdown.markdown', {
    'extensions': [
        'markdown.extensions.smarty',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'dc18.markdown',
    ],
    'output_format': 'html5',
    'safe_mode': False,
})
MARKITUP_SET = 'markitup/sets/markdown/'
JQUERY_URL = 'js/jquery.js'

DEFAULT_FROM_EMAIL = 'registration@debconf.org'
REGISTRATION_DEFAULT_FROM_EMAIL = 'noreply@debconf.org'

WAFER_REGISTRATION_MODE = 'custom'
WAFER_USER_IS_REGISTERED = 'register.models.user_is_registered'

#WAFER_TALK_FORM = 'dc16.talks.TalkForm'

WAFER_PUBLIC_ATTENDEE_LIST = False

PAGE_DIR = '%s/' % (root / 'pages')
NEWS_DIR = '%s/' % (root / 'news' / 'stories')
SPONSORS_DIR = '%s/' % (root / 'sponsors')
