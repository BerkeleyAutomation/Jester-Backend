from django.conf.urls import patterns, url
from jester import views

urlpatterns = patterns('',
    url(r'^request_joke/$', views.request_joke),
    url(r'^rate_joke/(?P<joke_id>\d+)/(?P<rating>\S+)/$', views.rate_joke),
    url(r'^register_user/', views.register_user),
)
