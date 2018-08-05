from django.forms import Form
from django.urls import reverse

from register.models.attendee import Attendee
from register.views.core import RegisterStep


class ConfirmationView(RegisterStep):
    title = 'Confirmation'
    form_class = Form
    template_name = 'register/page/confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['attendee'] = self.request.user.attendee
        except Attendee.DoesNotExist:
            pass

        return context

    def get_success_url(self):
        return reverse('wafer_user_profile',
                       kwargs={'username': self.request.user.username})
