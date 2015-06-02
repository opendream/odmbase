from django.conf.urls import url, patterns

urlpatterns = patterns('odmbase.presentation.views',
    url(r'social_count/gplus/$', 'social_count_gplus', name='social_count_gplus'),
    url(r'crawl_index/$', 'crawl_index', name='crawl_index'),
    url(r'proxy/$', 'proxy', name='proxy'),
    url(r'^$', 'home', name='home'),
    url(r'^\w+', 'home', name='home')
)

