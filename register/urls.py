from django.conf.urls import url
from django.views.generic.base import RedirectView

from register.views import STEPS
from register.views.core import ClosedView, UnRegisterView


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='step-0'), name='register'),
    url(r'^unregister$', UnRegisterView.as_view(), name='unregister'),
    url(r'^closed$', ClosedView.as_view(), name='register-closed'),
]

for i, step in enumerate(STEPS):
    urlpatterns.append(
        url(r'^step-{}$'.format(i), step.as_view(),
            name='register-step-{}'.format(i)))
