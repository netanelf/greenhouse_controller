#from django.conf.urls import include, url
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    #url(r'^admin/', include(admin.site.urls)),
    path('admin/', admin.site.urls),
    #url(r'^greenhouse_app/', include('greenhouse_app.urls')),
    path('greenhouse_app/', include('greenhouse_app.urls')),
]
