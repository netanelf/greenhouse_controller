
var series_data = [];

window.onload = function(){
    var show_graphs = document.getElementById('show_graphs');
    show_graphs.onclick = retrieveSensorData;
}

function retrieveSensorData(){
    console.debug('in showGraphs');
    // create list of selected sensors
    series_data = [];
    var selectedSensors = getSelectedSensors();
    var numOfSensors = selectedSensors.length;
    for(var i=0; i<numOfSensors; i++ ){
        retrieveOneSensorData(selectedSensors[i], numOfSensors);
    }
}


function retrieveOneSensorData(sensorId, numOfSensors){
    console.debug('retrieving data for sensor: ' + sensorId);

    function onDataReceived(series) {
        series_data.push(series);
        if(series_data.length == numOfSensors){
            console.debug('retrieved data for all checked sensors');
            createFlot();
        }
    }

    $.ajax({
        url: 'getGraphData/',
        type: 'GET',
        dataType: 'json',
        data: sensorId,
        success: onDataReceived
    });
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

function createFlot(){
    console.debug('in createFlot');
    var options = {
        lines: {
            show: true
        },
        points: {
            show: true,
            symbol: 'diamond'
        },
        xaxis: {
            mode: 'time'
        },
        crosshair: {
            mode: 'xy'
        },
        legend:{
            container:$('#legend-container'),
        }
    };

    // Push the new data onto our existing data array
    $.plot('#placeholder', series_data, options);
}

/*
$(function() {

    var options = {
        lines: {
            show: true
        },
        points: {
            show: true,
            symbol: 'diamond'
        },
        xaxis: {
            timezone: 'browser',
            mode: 'time',
        },
        crosshair: {
            mode: 'xy'
        },
        legend:{
            container:$('#legend-container'),
        }
    };

    $('button.fetchSeries').click(function () {

        function onDataReceived(series) {

            // Push the new data onto our existing data array
            $.plot('#placeholder', series, options);
        }

        $.ajax({
            url: 'getGraphData/',
            type: 'GET',
            dataType: 'json',
            success: onDataReceived
        });
    });
});

*/

