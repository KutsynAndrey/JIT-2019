mapboxgl.accessToken = 'pk.eyJ1Ijoib2xlemgiLCJhIjoiY2swZ3oxb2E3MDAzODNkdXY5NHN6NHl2biJ9.S64PvKhaqrlVk_7jVAOmdw';

// ShowPolygonButton.onclick = ShowPolygon;

var polygonsGC = {}, polygonsDMS = {}, polygonsId = [];

var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/mapbox/satellite-v9', //hosted style id
    center: [-91.874, 42.760], // starting position
    zoom: 12 // starting zoom
});

var draw = new MapboxDraw({
    displayControlsDefault: false,
    controls: {
        polygon: true,
        trash: true
    }
});

var customData = {
    "features": [],
    "type": "FeatureCollection"
};

function forwardGeocoder(query) {
    let matchingFeatures = [];
    for (let i = 0; i < customData.features.length; i++) {
        let feature = customData.features[i];
        // handle queries with different capitalization than the source data by calling toLowerCase()
        if (feature.properties.title.toLowerCase().search(query.toLowerCase()) !== -1) {
            // add a tree emoji as a prefix for custom data results
            // using carmen geojson format: https://github.com/mapbox/carmen/blob/master/carmen-geojson.md
            feature['place_name'] = '🌲 ' + feature.properties.title;
            feature['center'] = feature.geometry.coordinates;
            feature['place_type'] = ['park'];
            matchingFeatures.push(feature);
        }
    }
    return matchingFeatures;
}

map.addControl(new MapboxGeocoder({
    accessToken: mapboxgl.accessToken,
    localGeocoder: forwardGeocoder,
    zoom: 14,
    placeholder: "Enter search",
    mapboxgl: mapboxgl
}));

map.on('draw.create', GetCoords);
map.on('draw.delete', GetCoords);
map.on('draw.update', GetCoords);

map.addControl(new mapboxgl.NavigationControl());
map.addControl(draw);

var marker = new mapboxgl.Marker({
    draggable: true
});

marker.on('dragend', onDragEnd);
 
function onDragEnd() {
    let lngLat = marker.getLngLat();
    SaveMarkerCoordinates(lngLat);
}

function SaveMarkerCoordinates(coords) {
    let StartPont = document.getElementById('start-point');
    StartPont.value = String(coords.lat) + ' ' + String(coords.lng);
    console.log("StartPont:", StartPont.value);
    console.log(coords);
}

function GetCoords(e) {
    let data = draw.getAll(),
        features = data.features;
    console.log(features);
    polygonsId = [], polygonsGC = {}, polygonsDMS = {};
    for(let i = 0; i < features.length; i++) {
        let polygon = features[i];
        polygonsId.push(polygon.id);
        polygonsGC[polygon.id] = polygon.geometry.coordinates[0];
        let coords = polygon.geometry.coordinates[0];
        polygonsDMS[polygon.id] = [];
        for(let j = 0; j < coords.length; j++) {
            polygonsDMS[polygon.id].push([DMS(coords[j][0]), DMS(coords[j][1])]);
        }
    }
    console.log(polygonsGC);
    console.log(polygonsDMS);
    if(polygonsId.length != 0) {
        let polygon = polygonsGC[polygonsId[0]];
        marker.setLngLat(polygon[0]).addTo(map);
        onDragEnd();
    } else {
        marker.remove();
    }
    SaveCoords();
}

function DMS(coordinate) {
    let absolute = Math.abs(coordinate);
    let degrees = Math.floor(absolute);
    let minutesNotTruncated = (absolute - degrees) * 60;
    let minutes = Math.floor(minutesNotTruncated);
    let seconds = Math.floor((minutesNotTruncated - minutes) * 60);

    return [degrees, minutes, seconds];
}

function ShowPolygon() {
    read()
    let latitude = document.getElementsByClassName("latitude"),
        longitude = document.getElementsByClassName("longitude"),
        polygonId = RandomKey(),
        coords = [];

    console.log(latitude);
    for(let i = 0; i < latitude.length; i++) {
        coords.push([parseFloat(latitude[i].value), parseFloat(longitude[i].value)]);
    }
    coords.push([parseFloat(latitude[0].value), parseFloat(longitude[0].value)]);
    polygonsId.push(polygonId);
    polygonsDMS[polygonId] = [];
    for(let j = 0; j < coords.length; j++) {
        polygonsGC[polygonId] = coords;
        polygonsDMS[polygonId].push([DMS(coords[j][0]), DMS(coords[j][1])]);
    }

    draw.add({
        'id': polygonId,
        'type': 'Polygon',
        'coordinates': [coords]
    });

    SaveCoords();
    ChangeParameters(coords);

    console.log(polygonsGC);
}

function RandomKey() { 
    let key = Math.random().toString(33) + Math.random().toString(33);
    return key;
}

function SaveCoords() {
    let LatitudeGC = document.getElementById('latitude-GC'),
        LongitudeGC = document.getElementById('longitude-GC'),
        LatitudeDMS = document.getElementById('latitude-DMS'),
        LongitudeDMS = document.getElementById('longitude-DMS');

    LatitudeGC.value = "", LongitudeGC.value = "",
    LatitudeDMS.value = "", LongitudeDMS.value = "";
    console.log(polygonsGC)
    for(let id = 0; id < polygonsId.length; id++) {
        for(let point = 0; point < polygonsGC[polygonsId[id]].length; point++) {
            LatitudeGC.value += polygonsGC[polygonsId[id]][point][0];
            LongitudeGC.value += polygonsGC[polygonsId[id]][point][1];

            LatitudeDMS.value += polygonsDMS[polygonsId[id]][point][0];
            LongitudeDMS.value += polygonsDMS[polygonsId[id]][point][1];
            if(point != polygonsGC[polygonsId[id]].length - 1) {
                LatitudeGC.value += ' ';
                LongitudeGC.value += ' ';

                LatitudeDMS.value += ' ';
                LongitudeDMS.value += ' ';
            } else if(id != polygonsId.length - 1){
                LatitudeGC.value += '$';
                LongitudeGC.value += '$';

                LatitudeDMS.value += '$';
                LongitudeDMS.value += '$';
            }
        }
    }

    console.log(LatitudeGC.value);
    console.log(LongitudeGC.value);
    console.log(LatitudeDMS.value);
    console.log(LongitudeDMS.value);
}

function CenterPolygon(polygon) {
    let latitude = 0,
        longitude = 0;

    for(let i = 0; i < polygon.length - 1; i++) {
        latitude += polygon[i][0];
        longitude += polygon[i][1];
    }

    latitude /= (polygon.length - 1);
    longitude /= (polygon.length - 1);

    return [latitude, longitude];
}


function MapZoom(max) {
    if(max < 100) return 22;
    if(max < 250) return 21;
    if(max < 500) return 20;
    if(max < 750) return 19;
    if(max < 1500) return 18;
    if(max < 2500) return 17;
    if(max < 5000) return 16;
    if(max < 12500) return 15;
    if(max < 25000) return 14;
    if(max < 50000) return 13;
    if(max < 100000) return 12;
    if(max < 200000) return 11;
    if(max < 400000) return 10;
    if(max < 750000) return 9;
    if(max < 1500000) return 8;
    if(max < 3000000) return 7;
    if(max < 6500000) return 6;
    if(max < 12500000) return 5;
    if(max < 25000000) return 4;
    if(max < 50000000) return 3;
    if(max < 200000000) return 2;
    if(max < 500000000) return 1;
    if(max < 1000000000) return 0;
}


function ChangeParameters(polygon) {
    let center = CenterPolygon(polygon),
        MaxLat = [-10000000, 0],
        MinLat = [10000000, 0],
        MaxLong = [0, -1000000],
        MinLong = [0, 1000000];

    for(let i = 0; i < polygon.length - 1; i++) {
        MaxLat = [Math.max(MaxLat[0], polygon[i][0]), 0];
        MinLat = [Math.min(MinLat[0], polygon[i][0]), 0];
        MaxLong = [0, Math.max(MaxLong[1], polygon[i][1])];
        MinLong = [0, Math.min(MinLong[1], polygon[i][1])];
    }

    MaxLat = turf.point(MaxLat);
    MinLat = turf.point(MinLat);
    MaxLong = turf.point(MaxLong);
    MinLong = turf.point(MinLong);

    let distanceLat = turf.distance(MaxLat, MinLat) * 1000,
        distanceLong = turf.distance(MaxLong, MinLong) * 1000,
        max = Math.max(distanceLat, distanceLong),
        zoom = MapZoom(max);

    console.log(distanceLat, distanceLong, zoom);

    map.flyTo({center: center, zoom: zoom / 2});
}

function read(){
    console.log("reading.....");
    var fileUpload=document.getElementById("csvFile").files[0];
    var reader = new FileReader();
    reader.readAsText(fileUpload/*, "UTF-8"*/);
    console.log(fileUpload)
    console.log(reader)
}