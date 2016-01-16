from django.shortcuts import render
from greenhouse_app.models import Sensor, Measure, Relay, TimeGovernor, Configurations, ControllerOBject
import json
from django.http import HttpResponse, FileResponse
from django.utils import timezone
import csv
import cStringIO as StringIO
import time
from datetime import datetime


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


def downloadMeasurements(request):
    """
    send all measurements as .csv file
    """
    CHUNK = 128
    measures = Measure.objects.all()
    fields = Measure._meta.fields
    field_names = [f.name for f in fields]

    csvfile = StringIO.StringIO()
    csvwriter = csv.writer(csvfile)

    def read_and_flush():
        csvfile.seek(0)
        data = csvfile.read()
        csvfile.seek(0)
        csvfile.truncate()
        return data

    def data():
        csvwriter.writerow(field_names)
        i = 0
        for m in measures:
            i += 1
            row = []
            for field_name in field_names:
                if field_name == 'time':
                    t = getattr(m, field_name)
                    t = timezone.make_naive(t, timezone=timezone.get_current_timezone())
                    t = t.strftime('%d/%m/%y %H:%M:%S.%f')
                    row.append(t)
                else:
                    row.append(getattr(m, field_name))
            csvwriter.writerow(row)
            if i > CHUNK:
                data = read_and_flush()
                yield data
                i = 0

    response = FileResponse(data(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="measurements.csv"'
    return response


def getSensorsData(request):
    measurement_list = Measure.objects.order_by('-time')[:20]
    context_dict = {'measurements': measurement_list}
    # Render the response and send it back!
    return render(request, 'greenhouse_app/sensorsData.html', context_dict)


def getLastSensorValues(request):
    sensor_list = Sensor.objects.order_by()

    sensor_data = []
    for s in sensor_list:
        name = s.name
        try:
            measure = Measure.objects.filter(sensor=s).latest('time')
            val = measure.val
            val = '{:.2f}'.format(val)
            t = measure.time
            t = timezone.make_naive(t, timezone=timezone.get_current_timezone())
            t = t.strftime('%d/%m/%y %H:%M:%S')
        except Exception:
            val = 'unknown'
            t = 'unknown'
        sensor_data.append({'name': name, 'val': val, 'time': t})
    return HttpResponse(json.dumps(sensor_data))


def getRelaysState(request):
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
        for d in data:
            val = 1 if d['newState'] == True else 0
            r = Relay.objects.get(name=d['name'])
            r.wanted_state = val
            r.save()

    return HttpResponse(json.dumps({'NoData': None}))


def relays(request):
    relay_list = Relay.objects.order_by()
    manual_mode = Configurations.objects.get(name='manual_mode')
    context_dict = {'relays': relay_list, 'manual_mode': manual_mode.value}
    return render(request, 'greenhouse_app/relays.html', context_dict)


def graphs(request):
    #sensors = Sensor.objects.all()
    sensors = ControllerOBject.objects.all()
    sensors_names = []
    for s in sensors:
        sensors_names.append(s.name)
    context_dict = {'sensors': sensors_names}

    print context_dict
    return render(request, 'greenhouse_app/graphs.html', context_dict)


def setConfiguration(request):
    """
    change some configuration in models.Configurations
    """
    print 'in setConfiguration'
    a = request.GET.viewkeys()

    for k in a:
        data = json.loads(k)
        print 'data: {}'.format(data)
        val = int(data['value'])
        print 'val: {}'.format(val)
        r = Configurations.objects.get(name=data['name'])
        print r
        r.value = val
        r.save()

    return HttpResponse(json.dumps({'NoData': None}))


def getGraphData(request):
    """
    {
    "label": "Europe (EU27)",
    "data": [[1999, 3.0], [2000, 3.9], [2001, 2.0], [2002, 1.2], [2003, 1.3], [2004, 2.5], [2005, 2.0], [2006, 3.1], [2007, 2.9], [2008, 0.9]]
    }
    :param request:
    :return:
    """
    print 'in getGraphData'
    k = list(request.GET.viewkeys())
    data = json.loads(k[0])
    wanted_sensor = data[0]
    wanted_time = data[1]

    d_start = datetime(year=int(wanted_time[:4]), month=int(wanted_time[5:7]), day=int(wanted_time[8:10]), hour=0, minute=0, second=0, microsecond=0)
    d_start = timezone.make_aware(value=d_start, timezone=timezone.get_current_timezone())
    d_end = datetime(year=int(wanted_time[:4]), month=int(wanted_time[5:7]), day=int(wanted_time[8:10]), hour=23, minute=59, second=59, microsecond=0)
    d_end = timezone.make_aware(value=d_end, timezone=timezone.get_current_timezone())

    print 'wanted time between {} and {}'.format(d_start, d_end)
    #s = Sensor.objects.get(name=wanted_sensor)
    s = ControllerOBject.objects.get(name=wanted_sensor)
    #last_measure = Measure.objects.filter(sensor=s).latest('time')
    #day_start = (last_measure.time).replace(hour=0, minute=0, second=0, microsecond=0)

    data = []
    name = s.name
    measures = Measure.objects.filter(sensor=s, time__gt=d_start, time__lt=d_end)
    for measure in measures:
        val = measure.val
        val = '{:.2f}'.format(val)
        t_python = measure.time
        t_python = timezone.make_naive(t_python, timezone=timezone.get_current_timezone())
        t = int(time.mktime(t_python.timetuple())*1000)
        data.append([t, val])

    data.reverse()
    sensor_data = {'data': data, 'label': name}

    return HttpResponse(json.dumps(sensor_data))

