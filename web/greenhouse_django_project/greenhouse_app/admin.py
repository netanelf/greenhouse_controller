from django.contrib import admin
from greenhouse_app.models import Sensor, Relay, TimeGovernor, Configuration, Action, Event, EventAtTimeT, EventEveryDT, Flow, ActionSaveSensorValToDB
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
# Register your models here.


@admin.register(Relay)
class RelayAdmin(admin.ModelAdmin):
    list_display = ('name', 'pin', 'state', 'wanted_state', 'simulate', 'time_governor')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'simulate', 'pin', 'i2c', 'device_id')


@admin.register(TimeGovernor)
class TimeGovernorAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'state')


@admin.register(Configuration)
class ConfigurationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'explanation')


@admin.register(Action)
class ActionsAdmin(PolymorphicParentModelAdmin):
    list_display = ('name', )
    child_models = (ActionSaveSensorValToDB, )


@admin.register(ActionSaveSensorValToDB)
class ActionSaveSensorValToDBAdmin(PolymorphicChildModelAdmin):
    list_display = ('name',)
    base_model = ActionSaveSensorValToDB


@admin.register(Event)
class EventAdmin(PolymorphicParentModelAdmin):
    list_display = ('name',)
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

