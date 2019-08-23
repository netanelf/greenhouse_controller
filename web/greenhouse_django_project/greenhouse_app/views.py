from django.shortcuts import render
from greenhouse_app.models import Sensor, Measure, Relay, TimeGovernor, Configuration, ControllerOBject, KeepAlive
import json
from django.http import HttpResponse, FileResponse
from django.utils import timezone
import csv
import cStringIO as StringIO
import time
from datetime import datetime
import logging
from functools import wraps


logger = logging.getLogger('django')


def timing_decorator(func):

    def wrapped(*args, **kwargs):
        t0 = time.time()
        ret_val = func(*args, **kwargs)
        t1 = time.time()
        logger.info('{} took {}[s]'.format(func.__name__, t1 - t0))
        return ret_val
    return wrapped


@timing_decorator
def index(request):
    """
    main view for home page
    """

    sensor_list = Sensor.objects.order_by()
    relay_list = Relay.objects.order_by()
    time_governors_list = TimeGovernor.objects.order_by()
    keep_alive_list = KeepAlive.objects.order_by()
    context_dict = {'sensors': sensor_list,
                    'relays': relay_list,
                    'governors': time_governors_list,
                    'keepalives': keep_alive_list}
    # Render the response and send it back!
    return render(request, 'greenhouse_app/index.html', context_dict)

@timing_decorator
def measurements(request):
    return render(request, 'greenhouse_app/measurements.html')

@timing_decorator
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

@timing_decorator
def getSensorsData(request):
    measurement_list = Measure.objects.order_by('-measure_time')[:20]
    context_dict = {'measurements': measurement_list}
    # Render the response and send it back!
    return render(request, 'greenhouse_app/sensorsData.html', context_dict)

@timing_decorator
def getLastSensorValues(request):
    sensor_list = Sensor.objects.order_by()

    sensor_data = []
    for s in sensor_list:
        name = s.name
        try:
            measure = Measure.objects.filter(sensor=s).latest('measure_time')
            val = measure.val
            val = '{:.2f}'.format(val)
            t = measure.measure_time
            t = timezone.make_naive(t, timezone=timezone.get_current_timezone())
            t = t.strftime('%d/%m/%Y %H:%M:%S')
        except Exception:
            val = 'unknown'
            t = 'unknown'
        sensor_data.append({'name': name, 'val': val, 'time': t})
    return HttpResponse(json.dumps(sensor_data))


@timing_decorator
def getKeepAliveValues(request):
    keep_alive_cursor = KeepAlive.objects.all()
    keep_alive_list = []
    for k in keep_alive_cursor:
        name = k.name
        timestamp = k.timestamp
        timestamp = timezone.make_naive(timestamp, timezone=timezone.get_current_timezone())
        timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
        alive = k.alive
        keep_alive_list.append({'name': name, 'timestamp': timestamp, 'alive': alive})
    return HttpResponse(json.dumps(keep_alive_list))


@timing_decorator
def getRelaysState(request):
    relay_list = Relay.objects.order_by()

    relay_data = []
    for r in relay_list:
        relay_data.append({'name': r.name, 'state': r.state})

    return HttpResponse(json.dumps(relay_data))


# ajax callback
@timing_decorator
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


@timing_decorator
def relays(request):
    relay_list = Relay.objects.order_by()
    manual_mode = Configuration.objects.get(name='manual_mode')
    context_dict = {'relays': relay_list, 'manual_mode': manual_mode.value}
    return render(request, 'greenhouse_app/relays.html', context_dict)


@timing_decorator
def graphs(request):
    #sensors = Sensor.objects.all()
    sensors = ControllerOBject.objects.all()
    sensors_names = []
    for s in sensors:
        sensors_names.append(s.name)
    context_dict = {'sensors': sensors_names}

    return render(request, 'greenhouse_app/graphs.html', context_dict)


@timing_decorator
def setConfiguration(request):
    """
    change some configuration in models.Configurations
    """
    a = request.GET.viewkeys()

    for k in a:
        data = json.loads(k)
        print 'data: {}'.format(data)
        val = int(data['value'])
        print 'val: {}'.format(val)
        r = Configuration.objects.get(name=data['name'])
        print r
        r.value = val
        r.save()

    return HttpResponse(json.dumps({'NoData': None}))


@timing_decorator
def getGraphData(request):
    """
    {
    "label": "Europe (EU27)",
    "data": [[1999, 3.0], [2000, 3.9], [2001, 2.0], [2002, 1.2], [2003, 1.3], [2004, 2.5], [2005, 2.0], [2006, 3.1], [2007, 2.9], [2008, 0.9]]
    }
    :param request:
    :return:
    """
    logger.debug('in getGraphData')
    t0 = time.time()
    k = list(request.GET.viewkeys())
    data = json.loads(k[0])
    wanted_sensor = data[0]
    start_time = data[1]  # "2016-01-17 00:00:01"
    end_time = data[2]

    print 'string start_time: {}'.format(start_time)
    print 'string end_time: {}'.format(end_time)
    d_start = datetime(year=int(start_time[:4]), month=int(start_time[5:7]), day=int(start_time[8:10]),
                       hour=int(start_time[11:13]), minute=int(start_time[14:16]), second=int(start_time[17:19]),
                       microsecond=0)
    d_start = timezone.make_aware(value=d_start, timezone=timezone.get_current_timezone())

    d_end = datetime(year=int(end_time[:4]), month=int(end_time[5:7]), day=int(end_time[8:10]),
                     hour=int(end_time[11:13]), minute=int(end_time[14:16]), second=int(end_time[17:19]),
                     microsecond=0)
    d_end = timezone.make_aware(value=d_end, timezone=timezone.get_current_timezone())

    print 'wanted time between {} and {}'.format(d_start, d_end)
    s = ControllerOBject.objects.get(name=wanted_sensor)
    t1 = time.time()

    data = []
    name = s.name
    measures = Measure.objects.filter(sensor=s, measure_time__range=(d_start, d_end))
    #measures = Measure.objects.all()
    t2 = time.time()
    logger.debug('data length: {}'.format(measures.count()))
    for measure in measures: # TODO: this formating takes more than 1 second per 2300 measures, we should try to make that a lot better
        #val = measure.val
        #val = '{:.2f}'.format(val)
        #t_python = measure.time
        #t_python = timezone.make_naive(t_python, timezone=timezone.get_current_timezone())
        #t = int(time.mktime(t_python.timetuple())*1000)
        #t = measure.ts
        data.append([measure.ts, measure.val])

    t3 = time.time()
    data.reverse()
    sensor_data = {'data': data, 'label': name}
    t4 = time.time()
    print 'getting sensor from DB took {} [S]'.format(t1-t0)
    print 'getting data from DB took {} [S]'.format(t2-t1)
    print 'data formating took {} [S]'.format(t3-t2)
    print 'data reversing took {} [S]'.format(t4-t3)
    print 'all in all {} [S]'.format(t4-t0)
    return HttpResponse(json.dumps(sensor_data))
