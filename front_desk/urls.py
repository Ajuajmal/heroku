from django.conf.urls import url

from front_desk.views import (
    CashInvoicePayment, ChangeFoodView, ChangeShirtView, CheckInView,
    CheckOutView, Dashboard, RegisterOnSite)


urlpatterns = [
    url(r'^$', Dashboard.as_view(), name='front_desk'),
    url(r'^check_in/(?P<username>[\w.@+-]+)/$', CheckInView.as_view(),
        name='front_desk.check_in'),
    url(r'^check_in/(?P<username>[\w.@+-]+)/change_shirt/$',
        ChangeShirtView.as_view(), name='front_desk.change_shirt'),
    url(r'^check_in/(?P<username>[\w.@+-]+)/change_food/$',
        ChangeFoodView.as_view(), name='front_desk.change_food'),
    url(r'^register/$', RegisterOnSite.as_view(), name='front_desk.register'),
    url(r'^cash_payment/invoice/(?P<ref>[^/]+)/$',
        CashInvoicePayment.as_view(), name='front_desk.cash_invoice_payment'),
    url(r'^check_out/(?P<username>[\w.@+-]+)/$', CheckOutView.as_view(),
        name='front_desk.check_out'),
]
