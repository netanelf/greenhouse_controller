from django.conf.urls import patterns, url
from greenhouse_app import views
urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^measurements/getData/', views.getdata, name='getdata'),
                       url(r'^measurements/', views.measurements, name='measurements'),
                       url(r'^relays/', views.relays, name='relays'),
                       )


