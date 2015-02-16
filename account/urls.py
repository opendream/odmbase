from django.conf.urls import patterns, url


urlpatterns = patterns('odmbase.account.views',
    url(r'^register_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'account_register_confirm', name='account_register_confirm'),
)
