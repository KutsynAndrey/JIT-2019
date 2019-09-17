mapboxgl.accessToken = 'pk.eyJ1Ijoib2xlemgiLCJhIjoiY2swZ3oxb2E3MDAzODNkdXY5NHN6NHl2biJ9.S64PvKhaqrlVk_7jVAOmdw';

var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/mapbox/satellite-v9', //hosted style id
    center: [-91.874, 42.760], // starting position
    zoom: 12 // starting zoom
});

var polygons = {};

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
 
function GetCoords(e) {
    let data = draw.getAll();
    let features = data.features;
    console.log(features);
    for(let i = 0; i < features.length; i++) {
        var polygon = features[i];
        polygons[polygon.id] = polygon.geometry.coordinates[0];
    }
    console.log(polygons);
}

map.addControl(new mapboxgl.NavigationControl());
map.addControl(draw);