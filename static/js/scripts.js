// scripts.js
// (c) RiceApps 2017

///////////////////////////////////////////////////////////////////////////////
// Global variables

var socket = io.connect('http://' + document.domain + ':' + location.port);
var cases = {};

///////////////////////////////////////////////////////////////////////////////
// Map functions

function addMarker(coord) {
    var marker = new google.maps.Marker({
        position: coord,
        title: 'Text'
    });
    marker.setMap(gmap);
}

// Server calls

function resolve(case_id) {
    $.post('/api/bb_resolve', {
        case_id: case_id
    }).done(function() {
        // remove coordinates related to this message

    });
}

// Color

///////////////////////////////////////////////////////////////////////////////
// Onload

$(function() {

    $('.resolve-btn').on('click', function() {
        resolve(0);
    });

    // SocketIO Client Listeners
    socket.on('map message', function(msg) {
        console.log(msg);
        if (!(msg.case_id in cases))
            cases[msg.case_id] = [];

        var coord = new google.maps.LatLng(msg.latitude, msg.longitude);
        cases[msg.case_id].push(coord);
        addMarker(coord);
    });
});
