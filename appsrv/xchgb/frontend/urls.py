from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.views.generic.simple import redirect_to

urlpatterns = patterns('frontend.views',
    url(r'^$', 'welcome'),
    url(r'^login/$', 'login'),
    url(r'^setup/$', 'finish_registration'),
    url(r'^dashboard/$', 'dashboard'),
    url(r'^market/$', 'market_data'),
    url(r'^buy/$', 'buy_order'),
    url(r'^sell/$', 'sell_order'),
    url(r'^deposit/$', 'deposit_funds'),
    url(r'^withdraw/$', 'withdraw_funds'),
    url(r'^history/$', 'account_history'),
    url(r'^help/$', 'help'),
    url(r'^status/$', 'network_status'),
    url(r'^api/$', 'api_help'),
    url(r'^bitcoin/$', 'about_bitcoin'),
    url(r'^legal/$', 'legal'),
    url(r'^contact/$', 'contact'),
)

urlpatterns += patterns('',
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )