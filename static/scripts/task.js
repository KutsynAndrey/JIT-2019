mapboxgl.accessToken = 'pk.eyJ1Ijoib2xlemgiLCJhIjoiY2swZ3oxb2E3MDAzODNkdXY5NHN6NHl2biJ9.S64PvKhaqrlVk_7jVAOmdw';

var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/mapbox/satellite-v9', //hosted style id
    center: [-91.874, 42.760], // starting position
    zoom: 12 // starting zoom
});

map.addControl(new mapboxgl.NavigationControl());

map.on('load', ShowPolygon);

function ShowPolygon() {
    let polygons_latitude = document.getElementById('latitude-GC').value,
    	polygons_longitude = document.getElementById('longitude-GC').value;
    	// path_latitude = document.getElementById('ID').value,
    	// path_longitude = document.getElementById('ID').value;

    console.log(polygons_latitude);
    polygons_latitude = polygons_latitude.split('$'), polygons_longitude = polygons_longitude.split('$');
    console.log(polygons_latitude);
    for(let i = 0; i < polygons_longitude.length; i++) {
    	polygons_latitude[i] = polygons_latitude[i].split(' ')
    	polygons_longitude[i] = polygons_longitude[i].split(' ')
    }
    console.log(polygons_latitude);
    let polygons = [];
    for(let i = 0; i < polygons_longitude.length; i++) {
    	polygons.push([]);
    	for(let j = 0; j < polygons_longitude[i].length; j++) {
    		polygons[i].push([parseFloat(polygons_longitude[i][j]), parseFloat(polygons_latitude[i][j])])
    	}
    }

    // path_latitude = path_latitude.split(' '), path_longitude = path_longitude.split(' ');
    // let path = [];
    // for(let i = 0; i < path_latitude.length; i++) {
    // 	path.push([path_latitude[i], path_longitude[i]]);
    // }

    console.log(polygons);

	ChangeParameters(polygons[0]);
	DrawPolygon(polygons[0]);
	for(let i = 1; i < polygons.length; i++) {
		map.addLayer({
			'id': String(i),
			'type': 'fill',
			'source': {
				'type': 'geojson',
				'data': {
					'type': 'Feature',
					'geometry': {
						'type': 'Polygon',
						'coordinates': [polygons[i]]
					}
				}
			},
			'layout': {},
			'paint': {
				// 'fill-color': color,
				// 'fill-opacity': opacity
			}
		});
	}
}

function DrawPolygon(polygon) {
	map.addLayer({
		"id": "polygon",
		"type": "line",
		"source": {
			"type": "geojson",
			"data": {
				"type": "Feature",
				"properties": {},
				"geometry": {
					"type": "LineString",
					"coordinates": polygon
				}
			}
		},
		"layout": {
			"line-join": "round",
			"line-cap": "round"
		},
		"paint": {
			"line-color": "#888",
			"line-width": 3
		}
	});
}

function CenterPolygon(polygon) {
    let latitude = 0,
        longitude = 0;

    for(let i = 0; i < polygon.length - 1; i++) {
        latitude += parseFloat(polygon[i][0]);
        longitude += parseFloat(polygon[i][1]);
    }
    console.log('LATITUDE:', latitude);
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

    console.log(distanceLat, distanceLong, zoom, center);

    map.flyTo({center: center, zoom: zoom / 1.3});
}