from django.shortcuts import render
from greenhouse_app.models import Sensor, Measure, Relay
import json
from django.http import HttpResponse


def index(request):
    """
    main view for home page
    """

    sensor_list = Sensor.objects.order_by()
    relay_list = Relay.objects.order_by()
    context_dict = {'sensors': sensor_list, 'relays': relay_list}
    print request.path
    # Render the response and send it back!
    return render(request, 'greenhouse_app/index.html', context_dict)


def measurements(request):
    return render(request, 'greenhouse_app/measurements.html')


def getSensorsData(request):
    measurement_list = Measure.objects.order_by('-time')[:20]
    context_dict = {'measurements': measurement_list}
    print 'in getdata'
    # Render the response and send it back!
    return render(request, 'greenhouse_app/sensorsData.html', context_dict)


def getRelaysState(request):
    print 'in getRelaysState'
    relay_list = Relay.objects.order_by()

    relay_data = []
    for r in relay_list:
        relay_data.append({'name': r.name, 'state': r.state})

    return HttpResponse(json.dumps(relay_data))


# ajax callback
def setRelaysState(request):
    print 'in setRelaysState'
    a = request.GET.viewkeys()

    for k in a:
        data = json.loads(k)
        print data
        for d in data:
            print d
            print 'name: {}, newState: {}'.format(d['name'], d['newState'])
            val = 1 if d['newState'] == True else 0
            print 'val : {}'.format(val)
            r = Relay.objects.get(name=d['name'])
            r.wanted_state = val
            r.save()

    return HttpResponse(json.dumps({'NoData': None}))


def relays(request):
    relay_list = Relay.objects.order_by()
    context_dict = {'relays': relay_list}
    return render(request, 'greenhouse_app/relays.html', context_dict)
