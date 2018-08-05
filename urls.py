from django.conf.urls import include, url


urlpatterns = [
    url(r'^badges/', include('badges.urls')),
    url(r'^bursary/', include('bursary.urls')),
    url(r'^front_desk/', include('front_desk.urls')),
    url(r'^invoices/', include('invoices.urls')),
    url(r'^news/', include('news.urls')),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^register/', include('register.urls')),
    url(r'', include('dc18.urls')),
    url(r'', include('wafer.urls')),
]
