from register.views.accommodation import AccommodationView
from register.views.attendee import ContactInformationView
from register.views.billing import BillingView
from register.views.bursary import BursaryView
from register.views.conference import ConferenceRegistrationView
from register.views.confirmation import ConfirmationView
from register.views.core import InstructionsView
from register.views.food import FoodView
from register.views.misc import MiscView
from register.views.personal import PersonalInformationView
from register.views.review import ReviewView


STEPS = [
    InstructionsView,
    ContactInformationView,
    ConferenceRegistrationView,
    PersonalInformationView,
    BursaryView,
    FoodView,
    AccommodationView,
    MiscView,
    ReviewView,
    BillingView,
    ConfirmationView,
]
