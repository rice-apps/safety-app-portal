// Function for adding a marker to the page.
function addMarker(location) {
    marker = new google.maps.Marker({
        position: location
    });
}

/** 
*   SocketIO
*/
const socket = io('http://' + document.domain + ':' + location.port);
var cases = [];


socket.on('map message', function(msg) {
    
    console.log('Receive map message')
    if (!(msg.case_id in cases))
        cases[msg.case_id] = [];
    
    var coord = new google.maps.LatLng(msg.latitude, msg.longitude);
    cases[msg.case_id].push(coord);
    addMarker(coord);
});

socket.on('connect confirm', function(msg) {
    console.log(msg);
    // console.log(requestListModel);
});

/**
 * Server Request
 */
var requestListModel = [
    {
        case_id: 0,
        longitude: 0,
        latitude: 0,
        timestamp: 0
    }];

var serverEndPoint = 'http://' + document.domain + ':' + location.port + '/api/request';

var reqListPromise = $.get(serverEndPoint, function(response) {
        var data = JSON.parse(response).result;
        requestListModel = Array.from(data);
        console.log(requestListModel);
    }).promise();

/**
*   Vue Component 
*/
Vue.component('request-item', {
    props: ['val'],
    template: `<li> case_id: {{ val.case_id }}, long: {{ val.longitude }} lat: {{ val.latitude}} timestamp: {{ val.timestamp}} </li>`
});

/*
    Vue App
*/

panel = new Vue({
    el: '#panel',
    data: {
        status: "success",
        requestList: requestListModel
    }
});

reqListPromise.done(function( arg ) {
    panel.requestList = requestListModel;
    panel.status = "Done Promise";

    // Add marker to the map
    for (i = 0; i < requestListModel.length; i++) {
        console.log(requestListModel[i]);
        var case_id = requestListModel.case_id;
        var latitude = requestListModel.latitude;
        var longitude = requestListModel.longitude;
        
        if (!(case_id in cases)) {
            cases[case_id] = [];
        }
        
        var coord = new google.maps.LatLng(latitude, longitude);
        cases[case_id].push(coord);
        console.log(cases);
        addMarker(coord);
    }
});

