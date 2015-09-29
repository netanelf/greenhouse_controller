from django.shortcuts import render
from greenhouse_app.models import Sensor, Measure


def index(request):
    """
    main view for home page
    """

    sensor_list = Sensor.objects.order_by()
    context_dict = {'sensors': sensor_list}

    # Render the response and send it back!
    return render(request, 'greenhouse_app/index.html', context_dict)


def measurements(request):
    measurement_list = Measure.objects.order_by('-time')[:20]
    context_dict = {'measurements': measurement_list}

    # Render the response and send it back!
    return render(request, 'greenhouse_app/measurements.html', context_dict)