var gmap;

function initMap() {
    
    gmap = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 29.717394, lng: -95.402931},
        zoom: 16
    });
    console.log('Finish init map');
}

// Function for adding a marker to the page.
function addMarker(case_id, latitude, longitude) {
    var latLong = new google.maps.LatLng(latitude, longitude);

    var marker = new google.maps.Marker({
        position: latLong,
        title: "Hello, World!"
    });

    cases[case_id].push(marker);
    
    marker.setMap(gmap);
}

/** 
*   SocketIO
*/
const socket = io('http://' + document.domain + ':' + location.port);
var cases = {};


socket.on('map message', function(msg) {
    
    // console.log('Receive map message')
    if (!(msg.case_id in cases))
        cases[msg.case_id] = [];
    
    var coord = new google.maps.LatLng(msg.latitude, msg.longitude);
    cases[msg.case_id].push(coord);
    addMarker(coord);
});

socket.on('connect confirm', function(msg) {
    // console.log(msg);
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
        // console.log(requestListModel);
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
       
        var case_id = requestListModel[i].case_id;
        var latitude = requestListModel[i].latitude;
        var longitude = requestListModel[i].longitude;
        
        if (!cases[case_id]) {
            cases[case_id] = [];
        }

        console.log(latitude);
        console.log(longitude);

        addMarker(case_id, latitude, longitude);
    }
});

