from django.conf.urls import patterns, url
from greenhouse_app import views
urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^measurements/getSensorsData/', views.getSensorsData, name='getSensorsData'),
                       url(r'^measurements/', views.measurements, name='measurements'),
                       url(r'^relays/getRelaysState/', views.getRelaysState, name='getRelaysState'),
                       url(r'^relays/setRelaysState/', views.setRelaysState, name='setRelaysState'),
                       url(r'^relays/', views.relays, name='relays'),
                       )


