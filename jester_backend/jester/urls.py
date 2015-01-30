from django.conf.urls import patterns, url
from jester import views

urlpatterns = patterns('',
    url(r'^new_user/$', views.new_user),
    url(r'^request_joke/(?P<user_id>\d+)/$', views.request_joke),
    url(r'^rate_joke/(?P<user_id>\d+)/(?P<joke_id>\d+)/(?P<rating>\S+)/$', views.rate_joke),
    url(r'^register_user/(?P<email>\S+)/(?P<password>\S+)', views.register_user),
)