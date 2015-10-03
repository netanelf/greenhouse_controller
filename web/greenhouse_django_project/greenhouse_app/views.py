from django.shortcuts import render
from greenhouse_app.models import Sensor, Measure, Relay, TimeGovernor
import json
from django.http import HttpResponse



def index(request):
    """
    main view for home page
    """

    sensor_list = Sensor.objects.order_by()
    relay_list = Relay.objects.order_by()
    time_governors_list = TimeGovernor.objects.order_by()
    context_dict = {'sensors': sensor_list, 'relays': relay_list, 'governors': time_governors_list}
    # Render the response and send it back!
    return render(request, 'greenhouse_app/index.html', context_dict)


def measurements(request):
    return render(request, 'greenhouse_app/measurements.html')


def getSensorsData(request):
    measurement_list = Measure.objects.order_by('-time')[:20]
    context_dict = {'measurements': measurement_list}
    # Render the response and send it back!
    return render(request, 'greenhouse_app/sensorsData.html', context_dict)


def getLastSensorValues(request):
    print 'in getLastSensorValues'
    sensor_list = Sensor.objects.order_by()

    sensor_data = []
    for s in sensor_list:
        name = s.name

        measures = Measure.objects.filter(sensor=s)
        if len(measures) > 0:
            val = measures[len(measures)-1].val
            time = (measures[len(measures)-1].time).strftime('%d/%m/%y %H:%M:%S')
        else:
            val = 'unknown'
            time = 'unknown'
        sensor_data.append({'name': name, 'val': val, 'time': time})
    return HttpResponse(json.dumps(sensor_data))


def getRelaysState(request):
    relay_list = Relay.objects.order_by()

    relay_data = []
    for r in relay_list:
        relay_data.append({'name': r.name, 'state': r.state})

    return HttpResponse(json.dumps(relay_data))


# ajax callback
def setRelaysState(request):
    a = request.GET.viewkeys()

    for k in a:
        data = json.loads(k)
        for d in data:
            val = 1 if d['newState'] == True else 0
            r = Relay.objects.get(name=d['name'])
            r.wanted_state = val
            r.save()

    return HttpResponse(json.dumps({'NoData': None}))


def relays(request):
    relay_list = Relay.objects.order_by()
    context_dict = {'relays': relay_list}
    return render(request, 'greenhouse_app/relays.html', context_dict)
