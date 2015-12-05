from django.contrib import admin
from greenhouse_app.models import Sensor, SensorKind, Measure, Relay, TimeGovernor, Configurations
# Register your models here.

class RelayAdmin(admin.ModelAdmin):
    list_display = ('name', 'pin', 'state', 'wanted_state', 'simulate', 'time_governor')


class SensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'simulate', 'pin', 'i2c', 'device_id')


class TimeGovernorAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'state')


class ConfigurationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'explanation')


admin.site.register(SensorKind)
admin.site.register(Sensor, SensorAdmin)
admin.site.register(Measure)
admin.site.register(Relay, RelayAdmin)
admin.site.register(TimeGovernor, TimeGovernorAdmin)
admin.site.register(Configurations, ConfigurationsAdmin)
