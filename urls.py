from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.http import HttpResponse

urlpatterns = patterns('',
    url(r'', include('conf.urls')),
    url(r'^api/', include('odmbase.api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('odmbase.account.urls')),
    url(r'', include('social_auth.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")),
        url(r'^404$', TemplateView.as_view(template_name='404.html')),
        url(r'^500$', TemplateView.as_view(template_name='500.html')),
    )


else:
    urlpatterns += patterns('',
        url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    )

urlpatterns += patterns('',
    url(r'', include('odmbase.presentation.urls')),
)
