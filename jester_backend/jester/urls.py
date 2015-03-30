from django.conf.urls import patterns, url
from jester import views

urlpatterns = patterns('',
    url(r'^logout/$', views.logout_user),
    url(r'^request_joke/$', views.request_joke),
    url(r'^rate_joke/(?P<joke_id>\d+)/(?P<rating>\S+)/$', views.rate_joke),
    url(r'^register_user/$', views.register_user),
    url(r'^log_slider/(?P<old_rating>\S+)/(?P<new_rating>\S+)/$', views.log_slider),
    url(r'^join_mailing_list/$', views.join_mailing_list)
)
