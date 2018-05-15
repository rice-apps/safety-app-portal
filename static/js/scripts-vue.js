// Request item to be displayed on
Vue.component('request-item', {
    data: function() {
        return {
            val: {
                request_id: 0,
                case_id: 0,
                device_id: 0,
                longitude: 0,
                latitude: 0,
                timestamp: Date.now()
            },
            test: 10
        };
    },
    template: `<li> request_id: {{ val.request_id }}, case_id: {{ val.case_id }}, 
        device_id: {{ val.device_id}}, {{ val.longitude }} {{ val.latitude}} {{ val.timestamp}} </li>`
});

// var requestListModel = {
//     a: [1, 2, 3]
// };

// var vm = new Vue({
//     el: '#panel',
//     data: {
//         status: "success",
//         requestList: requestListModel
//     }
// }); 