from django.conf.urls import url, patterns

urlpatterns = patterns('odmbase.presentation.views',
    url(r'^$', 'home', name='home'),
    url(r'^\w+', 'home', name='home'),
)
