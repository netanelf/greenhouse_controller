from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('greenhouse_app/', include('greenhouse_app.urls')),
]
