from django.conf.urls import patterns, url
from recommender import views

urlpatterns = patterns('',
    url(r'^new_user/$', views.new_user),
    url(r'^request_joke/(?P<user_id>\d+)/$', views.request_joke)
)