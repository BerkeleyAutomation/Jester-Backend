from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^rating_histogram/$', views.rating_histogram))