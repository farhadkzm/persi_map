let mapApp = angular.module('mapApp', ['ngMaterial', 'ngMessages']);

mapApp.controller('MapController', function MapController($scope, $http, $interpolate, $mdSidenav, $mdDialog) {
    $scope.markers = [];
    $scope.searchPoint = {};
    $scope.type = 'doctor';
    $scope.distance = '30km';
    $scope.home = undefined;

    //used for bi-direction highlighting between markers and table rows
    $scope.selectedIndex = null;
    $scope.selectedMarker = null;
    $scope.selectedSideTabIndex = 0;
    $scope.searchResult = [];
    for (let i = 0; i < 20; i++) {
        $scope.searchResult.push({
            name: 'Peter Johnson', detail: {occupation: 'dentist', gender: 'female'}
            , location: {address: '12 St Kilda Rd, St Kilda VIC 3182', phone: '4433214123'}
        })
    }

    function setMarkerOnMap(source) {

        let infoWindow = new google.maps.InfoWindow({
            content: $interpolate('<a href="{{src}}"><b>{{ name }}</b></a>' +
                '<p>{{location.clinic_name}}</p>' +
                '<p>{{location.address}}</p>' +
                '<p><a target="_blank" href="{{ location.location_url }}">View on Google Maps</a></p>'
            )(source)
        });

        let geoSet = source.location.geo_set;
        let latLng = new google.maps.LatLng(geoSet.lat, geoSet.lon);
        let marker = new google.maps.Marker({
            position: latLng,
            map: $scope.map,
            title: source.name
        });
        marker.infoWindow = infoWindow;
        let markerIndex = $scope.markers.push(marker) - 1;
        marker.addListener('click', function () {
            $scope.setActiveMarker(markerIndex);
        });


    }


    $scope.toggleSideBar = function () {
        $mdSidenav('left').toggle();
    };

    $scope.showSearchTab = function () {
        $scope.selectedSideTabIndex = 0;
        $scope.toggleSideBar();
    };
    $scope.showResultTab = function () {
        $scope.selectedSideTabIndex = 1;
        $scope.toggleSideBar();
    };
    $scope.setActiveMarker = function (index) {
        let marker = $scope.markers[index];
        //de-select the old one if exists
        if ($scope.selectedMarker) {
            $scope.selectedMarker.setIcon(null);
            $scope.selectedMarker.infoWindow.close();
        }
        //select the current marker and show the infowindow
        marker.setIcon('http://maps.google.com/mapfiles/ms/icons/blue-dot.png');
        marker.infoWindow.open($scope.map, marker);
        marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
        $scope.selectedMarker = marker;
        //clear all rows
        angular.element(document.querySelector('#result-table')).children().removeClass('bg-info');
        //select relevant row
        angular.element(document.querySelector('#result-table')).children().eq(index).addClass('bg-info');

    };

    $scope.dragendMap = function () {
        $scope.searchPoint = {lat: $scope.map.getCenter().lat(), lng: $scope.map.getCenter().lng()};

        $scope.search(false);
    };

    $scope.showTabDialog = function (ev) {
        $mdDialog.show({
            controller: MapController,
            templateUrl: 'tabDialog.tmpl.html',
            parent: angular.element(document.body),
            targetEvent: ev,
            clickOutsideToClose: true
        })
            .then(function (answer) {
                $scope.status = 'You said the information was "' + answer + '".';
            }, function () {
                $scope.status = 'You cancelled the dialog.';
            });
    };

    $scope.changeAddress = function (place) {

        $scope.searchPoint = {};
        if (!place.geometry) {
            window.alert("No details available for input: '" + place.name + "'");
            return;
        }
        let location = place.geometry.location;
        $scope.searchPoint = {lat: location.lat(), lng: location.lng()};
        //remove home
        if ($scope.home) {
            $scope.home.setMap(null);
        }
        //set new home
        let latlon = new google.maps.LatLng($scope.searchPoint.lat, $scope.searchPoint.lng);
        $scope.home = new google.maps.Marker({
            position: latlon,
            map: $scope.map,
            icon: {
                path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                scale: 5
            }
        });

        $scope.map.setCenter(new google.maps.LatLng(location.lat(), location.lng()));
    };


    $scope.search = function (manualSearch = true) {

        $http.get('/api/search', {
            params: {
                clinic: $scope.clinic,
                name: $scope.name,
                occupation: $scope.occupation,
                type: $scope.type,
                distance: $scope.distance,
                gender: $scope.gender,
                lat: $scope.searchPoint.lat,
                lng: $scope.searchPoint.lng
            }
        }).success(function (data, status, headers, config) {

            //remove all markers
            $scope.markers.forEach(mkr => mkr.setMap(null));
            $scope.markers = [];
            $scope.searchResult = [];
            if (data.hits && data.hits.hits) {
                let result = data.hits.hits;

                result.map(el => el._source).forEach(source => {

                    //setting google map url for the location
                    source.location.location_url = (source.location.clinic_name) ?
                        'https://www.google.com/maps/place/' +
                        source.location.clinic_name +
                        '/@' + source.location.geo_set.lat + ',' + source.location.geo_set.lon + '/'

                        : 'http://maps.google.com/maps?q=' + source.location.address;

                    setMarkerOnMap(source);
                    $scope.searchResult.push(source);
                });


                if (manualSearch) {
                    let bounds = new google.maps.LatLngBounds();
                    $scope.markers.map(marker => marker.getPosition()).forEach(pos => bounds.extend(pos));
                    $scope.map.fitBounds(bounds);
                }
            }

        }).error(function (data, status, headers, config) {
            console.error('failed!')
        });
    };
});

//will be called by Google map api loaded at the bottom of the page
function initMap() {
    $scope = angular.element(document.querySelector('[ng-controller="MapController"]')).scope();

    let map = new google.maps.Map(document.getElementById('map'), {
        zoom: 5,
        center: new google.maps.LatLng(-37.813852, 144.960995),//Melbourne position
        mapTypeId: 'terrain'
    });
    google.maps.event.addListener(map, 'dragend', function () {
        // get the center and run the search again
        $scope.dragendMap();

    });
    let input = document.getElementById('pac-input');

    let autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.setTypes(['address']);
    autocomplete.bindTo('bounds', map);

    autocomplete.addListener('place_changed', function () {


        let place = autocomplete.getPlace();
        $scope.changeAddress(place);

    });

    $scope.map = map;
}


