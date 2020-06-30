from builtins import object

from django.contrib import admin
from greenhouse_app.models import *
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
# Register your models here.


@admin.register(Relay)
class RelayAdmin(admin.ModelAdmin):
    list_display = ('name', 'pin', 'simulate',)


@admin.register(Sensor)
class SensorAdmin(PolymorphicParentModelAdmin):
    polymorphic_list = True
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
class ConfigurationAdmin(PolymorphicParentModelAdmin):
    polymorphic_list = True
    list_display = ('__str__',)
    child_models = (ConfigurationInt, ConfigurationStr)


@admin.register(ConfigurationInt)
class ConfigurationIntAdmin(PolymorphicChildModelAdmin):
    base_model = ConfigurationInt


@admin.register(ConfigurationStr)
class ConfigurationStrAdmin(PolymorphicChildModelAdmin):
    base_model = ConfigurationStr


@admin.register(Action)
class ActionsAdmin(PolymorphicParentModelAdmin):
    polymorphic_list = True
    list_display = ('__str__',)
    child_models = (ActionSaveSensorValToDB, ActionSetRelayState, ActionSendEmail, ActionCaptureImageAndSave)


@admin.register(ActionSaveSensorValToDB)
class ActionSaveSensorValToDBAdmin(PolymorphicChildModelAdmin):
    base_model = ActionSaveSensorValToDB


@admin.register(ActionSetRelayState)
class ActionSetRelayStateAdmin(PolymorphicChildModelAdmin):
    base_model = ActionSetRelayState


@admin.register(ActionSendEmail)
class ActionSendEmailAdmin(PolymorphicChildModelAdmin):
    base_model = ActionSendEmail


@admin.register(ActionCaptureImageAndSave)
class ActionCaptureImageAndSaveAdmin(PolymorphicChildModelAdmin):
    base_model = ActionCaptureImageAndSave


@admin.register(Event)
class EventAdmin(PolymorphicParentModelAdmin):
    polymorphic_list = True
    list_display = ('__str__',)
    child_models = (EventAtTimeT, EventEveryDT)
    list_filter = (PolymorphicChildModelFilter,)


@admin.register(EventAtTimeT)
class EventAtTimeTAdmin(PolymorphicChildModelAdmin):
    base_model = EventAtTimeT


@admin.register(EventEveryDT)
class EventEveryDTAdmin(PolymorphicChildModelAdmin):
    base_model = EventEveryDT


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ('name',)

