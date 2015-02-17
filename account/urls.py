from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns('odmbase.account.views',
    url(r'^register_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'account_register_confirm', name='account_register_confirm'),

    # Social Auth
    url(r'^login/facebook/$', 'login_facebook', name='login_facebook'),
    url(r'^redirect/$', 'login_facebook_redirect', name='login_facebook_redirect'),
    (r'^error/', TemplateView.as_view(template_name="account/login_error.html")),
)
