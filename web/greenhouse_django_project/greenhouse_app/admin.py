from builtins import object

from django.contrib import admin
from greenhouse_app.models import *
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
# Register your models here.


@admin.register(Relay)
class RelayAdmin(admin.ModelAdmin):
    list_display = ('name', 'pin', 'state', 'wanted_state', 'simulate',)


@admin.register(Sensor)
class SensorAdmin(PolymorphicParentModelAdmin):
    list_display = ('name', 'simulate')
    child_models = (Dht22TempSensor, Dht22HumiditySensor, Ds18b20Sensor, Tsl2561Sensor, DigitalInputSensor)


@admin.register(Dht22TempSensor)
class Dht22TempSensorAdmin(PolymorphicChildModelAdmin):
    list_display = ('name', 'simulate', 'pin')
    base_model = Dht22TempSensor


@admin.register(Dht22HumiditySensor)
class Dht22HumiditySensorAdmin(PolymorphicChildModelAdmin):
    list_display = ('name', 'simulate', 'pin')
    base_model = Dht22HumiditySensor


@admin.register(Ds18b20Sensor)
class Ds18b20SensorAdmin(PolymorphicChildModelAdmin):
    list_display = ('name', 'simulate', 'device_id')
    base_model = Ds18b20Sensor
    

@admin.register(Tsl2561Sensor)
class Tsl2561SensorAdmin(PolymorphicChildModelAdmin):
    list_display = ('name', 'simulate', 'device_id')
    base_model = Tsl2561Sensor
    

@admin.register(DigitalInputSensor)
class DigitalInputSensorAdmin(PolymorphicChildModelAdmin):
    list_display = ('name', 'simulate', 'pin')
    base_model = DigitalInputSensor


@admin.register(Configuration)
class ConfigurationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'explanation')


@admin.register(Action)
class ActionsAdmin(PolymorphicParentModelAdmin):
    list_display = ('name', )
    child_models = (ActionSaveSensorValToDB, ActionSetRelayState)


@admin.register(ActionSaveSensorValToDB)
class ActionSaveSensorValToDBAdmin(PolymorphicChildModelAdmin):
    list_display = ('name',)
    base_model = ActionSaveSensorValToDB


@admin.register(ActionSetRelayState)
class ActionSetRelayStateAdmin(PolymorphicChildModelAdmin):
    list_display = ('name',)
    base_model = ActionSetRelayState


@admin.register(Event)
class EventAdmin(PolymorphicParentModelAdmin):
    list_display = ('name', )

    # def event_type(self, object):
    #     print(type(object))
    #     if isinstance(object, EventAtTimeT):
    #         return 'EventAtTimeT'
    #     elif isinstance(object, EventEveryDT):
    #         return 'EventEveryDT'
    #     else:
    #         print(object.__repr__())
    child_models = (EventAtTimeT, EventEveryDT)
    list_filter = (PolymorphicChildModelFilter,)


@admin.register(EventAtTimeT)
class EventAtTimeTAdmin(PolymorphicChildModelAdmin):
    list_display = ('name',)
    base_model = EventAtTimeT


@admin.register(EventEveryDT)
class EventEveryDTAdmin(PolymorphicChildModelAdmin):
    list_display = ('name',)
    base_model = EventEveryDT


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ('name',)

