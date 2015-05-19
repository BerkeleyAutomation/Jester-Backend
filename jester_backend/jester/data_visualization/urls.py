from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^rating_histogram/$', views.rating_histogram),
    url(r'^num_ratings_histogram/$', views.num_ratings_histogram),
    url(r'^num_ratings_over_time/$', views.num_ratings_over_time))