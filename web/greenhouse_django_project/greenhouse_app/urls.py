from django.conf.urls import patterns, url
from greenhouse_app import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^measurements/getSensorsData/', views.getSensorsData, name='getSensorsData'),
                       url(r'^measurements/getLastSensorValues/', views.getLastSensorValues, name='getLastSensorValues'),
                       url(r'^measurements/downloadMeasurements/', views.downloadMeasurements, name='downloadMeasurements'),
                       url(r'^measurements/', views.measurements, name='measurements'),
                       url(r'^relays/getRelaysState/', views.getRelaysState, name='getRelaysState'),
                       url(r'^relays/setRelaysState/', views.setRelaysState, name='setRelaysState'),
                       url(r'^relays/', views.relays, name='relays'),
                       url(r'^graphs/getGraphData', views.getGraphData, name='getGraphData'),
                       url(r'^graphs/', views.graphs, name='graphs'),
                       url(r'^setConfiguration/', views.setConfiguration, name='setConfiguration'),
                       url(r'^getKeepAlive/', views.getKeepAliveValues, name='getKeepAlive'),
                       )


