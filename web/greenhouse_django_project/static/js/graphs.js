
var series_data = [];
var min_data_date = null;

window.onload = function(){
    var show_graphs = document.getElementById('show_graphs');
    var add_data = document.getElementById('add_data');
    show_graphs.onclick = retrieveSensorData;
    add_data.onclick = addData;
}

function retrieveSensorData(event, date){
    console.debug('in showGraphs');
    var sentAjaxCalls = 0;
    var receivedAjaxCalls = 0;
    var add_data = document.getElementById('add_data');
    add_data.disabled = false;
    if(date == null){
        var date = new Date();
        min_data_date = date;
    }

    function onDataReceived(series){
        receivedAjaxCalls += 1;
        var s = {
            show: true,
            label: series.label,
            data: series.data
        };
        series_data.push(s);
        if(receivedAjaxCalls == sentAjaxCalls){
            createFlot();
        }
    }

    // create list of selected sensors
    var selectedSensors = getSelectedSensors();
    setAllSeriesToNotShow();

    for(var i=0; i<selectedSensors.length; i++ ){
        var sensorId = selectedSensors[i];
        if(!hasData(sensorId)){
            sentAjaxCalls += 1;
            console.log('retrieving data for sensor: ' + sensorId);
            $.ajax({
                url: 'getGraphData/',
                type: 'GET',
                dataType: 'json',
                data: JSON.stringify([sensorId, date.toJSON()], null, 2),
                success: onDataReceived
            });
        }else{
            setShow(sensorId);
        }
    }
    if(sentAjaxCalls == 0){
        createFlot();
    }
}

function getSelectedSensors(){
    var selectedSensors = [];
    var v = document.getElementById('sensor_checkboxes');
    for(var i=0; i<v.children.length; i++){
        var child = v.children[i];
        if(child.type == 'checkbox'){
            if(child.checked){
                selectedSensors.push(child.id);
            }
        }
    }
    console.debug('selected: ' + selectedSensors);
    return selectedSensors;
}

function addData(){
    console.debug('in addData');
    // 1995, 11, 17, 3, 24, 0
    var min_date = new Date(min_data_date.getFullYear(), min_data_date.getMonth(), min_data_date.getDate() -1, min_data_date.getHours(), min_data_date.getMinutes());
    min_data_date = min_date;
    retrieveSensorData(null, min_date);
}

function hasData(sensorId){
    for(var i=0; i<series_data.length; i++){
        var s = series_data[i];
        if (s.label == sensorId){
            return true
        }
    }
    return false;
}

function setAllSeriesToNotShow(){
    for(var i=0; i<series_data.length; i++){
        var s = series_data[i];
        s.show = false;
    }
}

function setShow(sensorId){
    for(var i=0; i<series_data.length; i++){
        var s = series_data[i];
        if(s.label == sensorId){
            s.show = true;
        }
    }
}

function createFlot(){
    console.debug('in createFlot');
    var options = {
        lines: {
            show: true
        },
        points: {
            show: true,
            symbol: 'diamond',
            radius: 2
        },
        xaxes: [{
            mode: 'time',
            timeformat: '%m/%y %H:%M',
            timezone: 'browser'
        }],
        crosshair: {
            mode: 'xy'
        },
        legend:{
            container:$('#legend-container'),
        },
        grid: {
            hoverable: true
        },
    };

    // Push the new data onto our existing data array
    var shownGraphs = [];
    for(var i=0; i<series_data.length; i++){
        var s = series_data[i];
        if(s.show){
            shownGraphs.push(s);
        }
    }
    updateOptions(options, shownGraphs);
    $.plot('#placeholder', shownGraphs, options);
}

function updateOptions(options, shownGraphs){
    var yaxisOptions = [];
    for(var i=0; i<shownGraphs.length; i++){
        var serie = shownGraphs[i];
        var minMax = findMinMax(serie);
        var y = {
            min: minMax.min,
            max: minMax.max
        };
        yaxisOptions.push(y);
        serie.yaxis = i+1;
    }
    options.yaxes = yaxisOptions;
}

function findMinMax(serie){
    var minVal = Number.MAX_VALUE;
    var maxVal = Number.MIN_VALUE;

    for(var i=0; i<serie.data.length; i++){
        var v = parseFloat(serie.data[i][1]);
        if(v > maxVal){
            maxVal = v;
        }
        if(v < minVal){
            minVal = v;
        }
    }
    var delta = maxVal-minVal;

    var minMax = {
        min: (minVal - delta/10),
        max: (maxVal + delta/10)
    };
    return minMax;
}

