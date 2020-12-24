from django.conf.urls import url
from greenhouse_app import views
urlpatterns = [#url(''),
               url(r'^$', views.index, name='index'),
               url(r'^measurements/getSensorsData/', views.getSensorsData, name='getSensorsData'),
               url(r'^measurements/getLastSensorValues/', views.getLastSensorValues, name='getLastSensorValues'),
               url(r'^measurements/downloadMeasurements/', views.downloadMeasurements, name='downloadMeasurements'),
               url(r'^measurements/', views.measurements, name='measurements'),
               url(r'^relays/getRelaysState/', views.getRelaysState, name='getRelaysState'),
               url(r'^manualMode/reloadConfiguration/', views.reloadConfiguration, name='reloadConfiguration'),
               url(r'^manualMode/runAction/', views.runAction, name='runAction'),
               url(r'^manualMode/setManualMode/', views.setManualMode, name='setManualMode'),
               url(r'^manualMode/', views.manualMode, name='manualMode'),
               url(r'^graphs/getGraphData', views.getGraphData, name='getGraphData'),
               url(r'^graphs/', views.graphs, name='graphs'),
               url(r'^camera/savePicture/', views.savePicture, name='savePicture'),
               url(r'^camera/', views.camera, name='camera'),
               url(r'^setConfiguration/', views.setConfiguration, name='setConfiguration'),
               url(r'^getKeepAlive/', views.getKeepAliveValues, name='getKeepAlive'),
               ]




