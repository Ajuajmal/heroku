from django.conf.urls import url

from django.views.generic.base import RedirectView

from dc18.views import (
    AttendeeAccommExport, AttendeeBadgeExport, DebConfScheduleView, RobotsView,
    StatisticsView, TalksExport, FoodExport,
)


urlpatterns = [
    url(r'^attendees/admin/export/accomm/$', AttendeeAccommExport.as_view(),
        name='attendee_admin_export_accomm'),
    url(r'^attendees/admin/export/badges/$', AttendeeBadgeExport.as_view(),
        name='attendee_admin_export_badges'),
    url(r'^attendees/admin/export/food/$', FoodExport.as_view()),
    url(r'^statistics/$', StatisticsView.as_view()),
    url(r'^schedule/open-day/$', RedirectView.as_view(
        url='/schedule/?day=2017-08-05', permanent=True),
        name='jump_open_day'),
    url(r'^schedule/$', DebConfScheduleView.as_view(),
        name='wafer_full_schedule'),
    url(r'^talks/admin/export/$', TalksExport.as_view(),
        name='talks_admin_export'),
    url(r'^robots.txt$', RobotsView.as_view()),
]
