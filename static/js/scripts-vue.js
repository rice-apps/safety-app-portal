/** 
*   SocketIO
*/
const socket = io('http://' + document.domain + ':' + location.port);
var cases = {};


socket.on('map message', function(msg) {
    console.log(msg);
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

var serverEndPoint = 'http://' + document.domain + ':' + location.port + '/api/bb_request';

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
});

