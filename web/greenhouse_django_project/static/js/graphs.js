
var series_data = [];
var min_data_date = null;
var graph_colors = ["#4D4D4D","#5DA5DA","#FAA43A","#60BD68","#F17CB0","#B2912F","#B276B2","#DECF3F","#F15854","#E6AFB9",
                    "#E07B91","#D33F6A","#11C638","#8DD593","#C6DEC7","#EAD3C6","#F0B98D","#EF9708","#0FCFC0","#9CDED6",
                    "#D5EAE7","#F3E1EB","#F6C4E1","#F79CD4"];


window.onload = function(){
    createEmptySeriesData();
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
        if(min_data_date == null){
            var date = new Date();
            min_data_date = date;
        }
        else{
            date = min_data_date;
        }
    }

    function onDataReceived(series){
        receivedAjaxCalls += 1;
        var s = {
            show: true,
            label: series.label,
            data: series.data
        };
        //series_data.push(s);
        addDataToSerie(series.label, series.data);
        setShow(series.label, true);
        if(receivedAjaxCalls == sentAjaxCalls){
            createFlot();
        }
    }

    // create list of selected sensors
    var selectedSensors = getSelectedSensors();
    setAllSeriesToNotShow();

    for(var i=0; i<selectedSensors.length; i++ ){
        var sensorId = selectedSensors[i];
        if(!hasData(sensorId, date)){ // we do not have the wanted data, make an ajax call to retrieve it
            sentAjaxCalls += 1;
            console.log('retrieving data for sensor: ' + sensorId  + 'time: ' + date);
            $.ajax({
                url: 'getGraphData/',
                type: 'GET',
                dataType: 'json',
                data: JSON.stringify([sensorId, date.toJSON()], null, 2),
                success: onDataReceived
            });
        }else{ // we already have the wanted data, only make it visable
            setShow(sensorId, true);
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
    // 1995, 11, 17, 3, 24, 0
    var min_date = new Date(min_data_date.getFullYear(), min_data_date.getMonth(), min_data_date.getDate() -1, min_data_date.getHours(), min_data_date.getMinutes());
    min_data_date = min_date;

    console.debug('in addData, requesting data for: ' + min_date);
    retrieveSensorData(null, min_date);
}


/*
* check if label 'sensorId' has data from the day part in date.
*/
function hasData(sensorId, date){
    for(var i=0; i<series_data.length; i++){
        var s = series_data[i];
        if (s.label == sensorId){
            for(var j=0; j<s.data.length; j++){
                try{
                    var d = Date(s.data[i][0]);
                    if(d.getFullYear() == date.getFullYear() & d.getMonth() == date.getMonth() & d.getDate == date.getDate()){
                        return true;
                    }
                }
                catch(e){
                    console.log('in hasData, got ec: ' + e);
                }
            }
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
            timeformat: '%d/%m %H:%M',
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
    var colors = [];
    for(var i=0; i<shownGraphs.length; i++){
        var serie = shownGraphs[i];
        var minMax = findMinMax(serie);
        var y = {
            min: minMax.min,
            max: minMax.max
        };
        yaxisOptions.push(y);
        serie.yaxis = i+1;
        colors.push(serie.color);
    }
    options.yaxes = yaxisOptions;
    options.colors = colors;
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

function createEmptySeriesData(){
    var names = [];
    var sensor_checkboxes = document.getElementById('sensor_checkboxes');
    for(var i=0; i<sensor_checkboxes.children.length; i++){
        if (sensor_checkboxes.children[i].nodeName == 'INPUT'){
            names.push(sensor_checkboxes.children[i].id);
        }
    }
    console.log('found names: ' + names);
    for(var i=0; i<names.length; i++){
        var serie = {};
        serie.label = names[i];
        serie.data = [];
        serie.show = false;
        serie.color = graph_colors[i];
        series_data.push(serie);
    }
}


function getSerie(label){
    for(var i=0; i<series_data.length;i++){
        if (series_data[i].label == label){
            return series_data[i];
        }
    }
}


function addDataToSerie(label, data){
    var s = getSerie(label);
    for(var i=0; i<data.length; i++){
        s.data.unshift(data[i]);
    }
}

function setShow(label, show){
    for(var i=0; i<series_data.length;i++){
        if (series_data[i].label == label){
            series_data[i].show = show;
        }
    }
}

