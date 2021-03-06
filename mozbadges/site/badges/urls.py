from django.conf.urls.defaults import patterns, url, include

from mozbadges.views import placeholder_view
import views


urlpatterns = patterns('',
    (r'^badges', include(patterns('',
        # /badges.json
        url(r'^\.json$', views.badge_list, name='json'),

        (r'^/', include(patterns('',
            # /badges/
            url(r'^$', views.badge_list, name='all'),

            (r'^(?P<slug>[\w-]+)', include(patterns('',
                # /badges/{badge}.json
                url(r'^\.json$', views.badge_detail, name='json'),

                (r'^/', include(patterns('',
                    # /badges/{badge}/
                    url(r'^$', views.badge_detail, name='detail'),

                    # /badges/{badge}/apply/
                    url(r'^apply/$', placeholder_view, name='apply'),
                    # /badges/{badge}/nominate/
                    url(r'^nominate/$', placeholder_view, name='nominate'),
                    # /badges/{badge}/award/
                    url(r'^award/$', placeholder_view, name='award'),

                    # /badges/{badge}/awards/
                    url(r'^awards/$', placeholder_view, name='awards'),

                    # /badges/{badge}/edit/
                    url(r'^edit/$', placeholder_view, name='edit'),
                    # /badges/{badge}/edit/design
                    url(r'^edit/design/$', placeholder_view, name='edit_design'),
                    # /badges/{badge}/delete/
                    url(r'^delete/$', placeholder_view, name='delete'),

                    # /badges/{badge}/favorite/
                    url(r'^favorite/$', placeholder_view, name='favorite'),
                    # /badges/{badge}/unfavorite/
                    url(r'^unfavorite/$', placeholder_view, name='unfavorite'),
                ))),
            ), namespace='badge', app_name='badge')),
        ))),
    ), namespace='badges', app_name='badge')),
)
