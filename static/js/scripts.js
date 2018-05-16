// scripts.js
// (c) RiceApps 2017

///////////////////////////////////////////////////////////////////////////////
// Global variables

// TODO: how to get document.domain / location.port?
var socket = io.connect('https://' + document.domain + ':' + location.port);
var cases = {};
var colors = {};

///////////////////////////////////////////////////////////////////////////////
// Map functions

function addMarker(case_id, coord) {
    // TODO: How to emphasize most recent lat-long
    var marker = new google.maps.Marker({
        position: coord,
        title: 'Text'
    });
    marker.setMap(gmap);
    cases[case_id].push(marker);
}

function getColor(case_id, lat, long) {
    // TODO: Generate unique, differentiable, color for each lat-long
}

function addRow(case_id, timestamp) {
    var text_el = "<tr class='request-" + case_id + "'>" + 
                    "<td><div class='request-dot'></div></td>" +
                    "<td>" + timestamp + "</td>" +
                    "<td><div class='resolve'>" + resolve + "</div></td>" +
                    "</tr>";

    $('#requests-table').append(text_el);
}

function removeRow(case_id) {
    $('.request-' + case_id).remove();
}

// Server calls
function resolve(case_id) {
    $.post('/api/bb_resolve', {
        case_id: case_id
    }).done(function() {
        // remove coordinates related to this message
        for (var marker of cases[case_id]) {
            marker.setMap(null);
        }
        // remove from list
        removeRow(case_id);
    });
}

// Color

///////////////////////////////////////////////////////////////////////////////
// Onload

$(function() {
    
    $('.resolve-btn').on('click', function() {
        resolve(0);
        // TODO: 
    });

    // TODO: Load existing active cases

    // SocketIO Client Listeners
    socket.on('map message', function(msg) {
        console.log(msg);
        // Add new case
        if (!(msg.case_id in cases)) {
            cases[msg.case_id] = [];
        
        var coord = new google.maps.LatLng(msg.latitude, msg.longitude);
        addMarker(msg.case_id, coord);


    });
});
