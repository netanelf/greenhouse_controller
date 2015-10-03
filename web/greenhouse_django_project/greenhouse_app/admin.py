from django.contrib import admin
from greenhouse_app.models import Sensor, SensorKind, Measure, Relay, TimeGovernor
# Register your models here.


admin.site.register(SensorKind)
admin.site.register(Sensor)
admin.site.register(Measure)
admin.site.register(Relay)
admin.site.register(TimeGovernor)
