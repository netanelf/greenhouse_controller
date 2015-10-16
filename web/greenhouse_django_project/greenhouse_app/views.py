from django.shortcuts import render
from greenhouse_app.models import Sensor, Measure, Relay, TimeGovernor, Configurations
import json
from django.http import HttpResponse, FileResponse
from django.utils import timezone
import csv
import cStringIO as StringIO


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
    field_names.remove('id')
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
        t0 = timezone.now()
        try:
            measure = Measure.objects.filter(sensor=s).latest('time')
            val = measure.val
            val = '{:.2f}'.format(val)
            time = measure.time
            time = timezone.make_naive(time, timezone=timezone.get_current_timezone())
            time = time.strftime('%d/%m/%y %H:%M:%S')
        except Exception:
            val = 'unknown'
            time = 'unknown'
        t1 = timezone.now()
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
