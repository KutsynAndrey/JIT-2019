mapboxgl.accessToken = 'pk.eyJ1Ijoib2xlemgiLCJhIjoiY2swZ3oxb2E3MDAzODNkdXY5NHN6NHl2biJ9.S64PvKhaqrlVk_7jVAOmdw';

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
"features": [
{
    "type": "Feature",
    "properties": {
        "title": "Lincoln Park",
        "description": "A northside park that is home to the Lincoln Park Zoo"
    },
    "geometry": {
        "coordinates": [
            -87.637596,
            41.940403
        ],
        "type": "Point"
    }
}
],
"type": "FeatureCollection"
};

function forwardGeocoder(query) {
var matchingFeatures = [];
for (var i = 0; i < customData.features.length; i++) {
    var feature = customData.features[i];
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
placeholder: "Enter search e.g. Lincoln Park",
mapboxgl: mapboxgl
}));

map.addControl(new mapboxgl.NavigationControl());
map.addControl(draw);