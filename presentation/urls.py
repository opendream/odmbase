from django.conf.urls import url, patterns

urlpatterns = patterns('presentation.views',
    url(r'^$', 'home', name='home'),
    url(r'^\w+', 'home', name='home'),
)
