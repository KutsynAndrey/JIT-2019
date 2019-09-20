var AddPointButton = document.getElementById('new-inputs'),
    ShowPolygonButton = document.getElementById('show-polygon'),
    PointInputs = "<div></div><div></div><div class='div'><label class='label'>Довгота</label><input class='input latitude' type='text' placeholder='Наприклад, -43.32'></div><div class='div'><label class='label'>Широта</label><input class='input longitude' type='text' placeholder='Наприклад, -43.32'></div>";

AddPointButton.onclick = AddPoint;
ShowPolygonButton.onclick = ShowPolygon;

mapboxgl.accessToken = 'pk.eyJ1Ijoib2xlemgiLCJhIjoiY2swZ3oxb2E3MDAzODNkdXY5NHN6NHl2biJ9.S64PvKhaqrlVk_7jVAOmdw';

var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/mapbox/satellite-v9', //hosted style id
    center: [-91.874, 42.760], // starting position
    zoom: 12 // starting zoom
});

var polygonsGC = {}, polygonsDMS = {};

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
 
function GetCoords(e) {
    let data = draw.getAll();
    let features = data.features;
    console.log(features);
    for(let i = 0; i < features.length; i++) {
        let polygon = features[i];
        polygonsGC[polygon.id] = polygon.geometry.coordinates[0];
        let coords = polygon.geometry.coordinates[0];
        polygonsDMS[polygon.id] = [];
        for(let j = 0; j < coords.length; j++) {
            polygonsDMS[polygon.id].push([DMS(coords[j][0]), DMS(coords[j][1])]);
        }
    }
    console.log(polygonsGC);
    console.log(polygonsDMS);
}

function DMS(coordinate) {
    let absolute = Math.abs(coordinate);
    let degrees = Math.floor(absolute);
    let minutesNotTruncated = (absolute - degrees) * 60;
    let minutes = Math.floor(minutesNotTruncated);
    let seconds = Math.floor((minutesNotTruncated - minutes) * 60);

    return [degrees, minutes, seconds];
}

function AddPoint() {
    $("#new-inputs").before(PointInputs);
}

function ShowPolygon() {
    let latitude = document.getElementsByClassName("latitude"),
        longitude = document.getElementsByClassName("longitude"),
        coords = [];

    let polygonId = RandomKey();
    console.log(latitude);
    for(let i = 0; i < latitude.length; i++) {
        coords.push([parseFloat(latitude[i].value), parseFloat(longitude[i].value)]);
    }
    coords.push([parseFloat(latitude[0].value), parseFloat(longitude[0].value)]);
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

    console.log(polygonsGC);
}

function RandomKey() { 
    let key = Math.random().toString(33) + Math.random().toString(33);
    return key;
}