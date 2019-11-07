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
        polygons_longitude = document.getElementById('longitude-GC').value,
        path_latitude = document.getElementById('path-lat').value,
        path_longitude = document.getElementById('path-lon').value,
        flag = document.getElementById("query-status").value;;

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
            polygons[i].push([parseFloat(polygons_latitude[i][j]), parseFloat(polygons_longitude[i][j])])
        }
    }
    // polygons = [[[42.7804, -91.8737], [42.7545, -91.891], [42.7547, -91.8285], [42.7804, -91.8737]]];
    // console.log(polygons[0][0]);
    // for(let i = 0; i < polygons[0].length; i++) {
    //     let t = polygons[0][i][0];
    //     polygons[0][i][0] = polygons[0][i][1];
    //     polygons[0][i][1] = t;
    // }
    console.log(polygons[0]);

    ChangeParameters(polygons[0]);
    DrawPolygon(polygons[0]);
    for(let i = 1; i < polygons.length; i++) {
        console.log(polygons[i]);
        map.addLayer({
            'id': 'hole ' + String(i),
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
                'fill-color': 'red',
                'fill-opacity': 0.4
            }
        });
    }
    console.log('FLAG:', flag);
    if(flag == 0) {
        let path = [];
        path_latitude = path_latitude.split(' '), path_longitude = path_longitude.split(' ');
        console.log(path_latitude);
        for(let i = 0; i < path_latitude.length; i++) {
            path.push([parseFloat(path_latitude[i]), parseFloat(path_longitude[i])]);
        }
        // path = [[42.7804, -91.8737], [42.75633210810811, -91.88978378378378], [42.759980756756754, -91.88735135135136], [42.75633210810811, -91.88735135135136], [42.75633989189189, -91.88491891891891], [42.75998854054054, -91.88491891891891], [42.76363718918919, -91.88491891891891], [42.767293621621626, -91.88248648648648], [42.763644972972976, -91.88248648648648], [42.75999632432433, -91.88248648648648], [42.75634767567568, -91.88248648648648], [42.75635545945946, -91.88005405405406], [42.76000410810811, -91.88005405405406], [42.763652756756755, -91.88005405405406], [42.767301405405405, -91.88005405405406], [42.770950054054055, -91.88005405405406], [42.77460648648649, -91.87762162162163], [42.77095783783784, -91.87762162162163], [42.76730918918919, -91.87762162162163], [42.76366054054054, -91.87762162162163], [42.76001189189189, -91.87762162162163], [42.75636324324324, -91.87762162162163], [42.75637102702703, -91.87518918918919], [42.76001967567568, -91.87518918918919], [42.76366832432433, -91.87518918918919], [42.76731697297298, -91.87518918918919], [42.77096562162163, -91.87518918918919], [42.77461427027028, -91.87518918918919], [42.77826291891892, -91.87518918918919], [42.778270702702706, -91.87275675675676], [42.774622054054056, -91.87275675675676], [42.77097340540541, -91.87275675675676], [42.76732475675676, -91.87275675675676], [42.763676108108115, -91.87275675675676], [42.760027459459465, -91.87275675675676], [42.756378810810816, -91.87275675675676], [42.7563865945946, -91.87032432432433], [42.760035243243244, -91.87032432432433], [42.763683891891894, -91.87032432432433], [42.767332540540544, -91.87032432432433], [42.77098118918919, -91.87032432432433], [42.77462983783784, -91.87032432432433], [42.77827848648649, -91.87032432432433], [42.774637621621615, -91.86789189189189], [42.77098897297297, -91.86789189189189], [42.76734032432432, -91.86789189189189], [42.76369167567567, -91.86789189189189], [42.760043027027024, -91.86789189189189], [42.756394378378374, -91.86789189189189], [42.75640216216216, -91.86545945945946], [42.76005081081081, -91.86545945945946], [42.76369945945946, -91.86545945945946], [42.7673481081081, -91.86545945945946], [42.77099675675675, -91.86545945945946], [42.7746454054054, -91.86545945945946], [42.77465318918919, -91.86302702702703], [42.77100454054054, -91.86302702702703], [42.76735589189189, -91.86302702702703], [42.76370724324324, -91.86302702702703], [42.76005859459459, -91.86302702702703], [42.75640994594594, -91.86302702702703], [42.756417729729726, -91.86059459459459], [42.760066378378376, -91.86059459459459], [42.763715027027025, -91.86059459459459], [42.767363675675675, -91.86059459459459], [42.771012324324325, -91.86059459459459], [42.771020108108104, -91.85816216216216], [42.76737145945946, -91.85816216216216], [42.76372281081081, -91.85816216216216], [42.76007416216216, -91.85816216216216], [42.75642551351351, -91.85816216216216], [42.7564332972973, -91.85572972972973], [42.76008194594594, -91.85572972972973], [42.76373059459459, -91.85572972972973], [42.76737924324324, -91.85572972972973], [42.76738702702703, -91.8532972972973], [42.76373837837838, -91.8532972972973], [42.76008972972973, -91.8532972972973], [42.75644108108108, -91.8532972972973], [42.756448864864865, -91.85086486486486], [42.760097513513514, -91.85086486486486], [42.763746162162164, -91.85086486486486], [42.76739481081081, -91.85086486486486], [42.76375394594594, -91.84843243243243], [42.7601052972973, -91.84843243243243], [42.75645664864865, -91.84843243243243], [42.75646443243243, -91.846], [42.76011308108108, -91.846], [42.76376172972973, -91.846], [42.763769513513516, -91.84356756756756], [42.76012086486487, -91.84356756756756], [42.75647221621622, -91.84356756756756], [42.75648, -91.84113513513513], [42.76012864864865, -91.84113513513513], [42.76013643243243, -91.8387027027027], [42.75648778378379, -91.8387027027027], [42.75649556756757, -91.83627027027028], [42.756503351351355, -91.83383783783783], [42.75651113513514, -91.8314054054054], [42.7804, -91.8737]];
        // for(let i = 0; i < path.length; i++) {
        //     let t = path[i][0];
        //     path[i][0] = path[i][1];
        //     path[i][1] = t;
        // }    
        path[0] = [path[0][1], path[0][0]];
        path[path.length - 1] = [path[path.length - 1][1], path[path.length - 1][0]];
        console.log(polygons[0][0]);
        console.log(path);

        var marker = new mapboxgl.Marker();
        marker.setLngLat(path[0]).addTo(map);

        var route = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": path
                }
            }]
        };
        
        map.addLayer({
            "id": "route",
            "type": "line",
            "source": {
                "type": "geojson",
                "data": {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                    "type": "LineString",
                    "coordinates": path
                    }
                }
            },
            "layout": {
                "line-join": "round",
                "line-cap": "round"
            },
            "paint": {
                "line-color": "yellow",
                "line-width": 3
            }
        });

        var point = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Point",
                    "coordinates": path[0]
                }
            }]
        };

        // Calculate the distance in kilometers between route start/end point.
        var lineDistance = turf.lineDistance(route.features[0], 'kilometers');
        var arc = [];
         
        // Number of steps to use in the arc and animation, more steps means
        // a smoother arc and animation, but too many steps will result in a
        // low frame rate
        var steps = 10000;
         
        // Draw an arc between the `origin` & `destination` of the two points
        for (var i = 0; i < lineDistance; i += lineDistance / steps) {
            var segment = turf.along(route.features[0], i, 'kilometers');
            arc.push(segment.geometry.coordinates);
        }
         
        // Update the route with calculated arc coordinates
        route.features[0].geometry.coordinates = arc;
        // Used to increment the value of the point measurement against the route.
        var counter = 0;
        
        map.addSource('point', {
            "type": "geojson",
            "data": point
        });
         
        map.addLayer({
            "id": "point",
            "source": "point",
            "type": "symbol",
            "layout": {
                "icon-image": "airport-15",
                "icon-rotate": ["get", "bearing"],
                "icon-rotation-alignment": "map",
                "icon-allow-overlap": true,
                "icon-ignore-placement": true
            }
        });
        console.log("POINT:", route.features[0].geometry.coordinates[0]);

        function animate() {
            point.features[0].geometry.coordinates = route.features[0].geometry.coordinates[counter];

            console.log(steps);
            if(counter >= steps) {
                console.log(steps);
                point.features[0].geometry.coordinates = route.features[0].geometry.coordinates[0];
            } else {
                point.features[0].properties.bearing = turf.bearing(
                    turf.point(route.features[0].geometry.coordinates[counter >= steps ? counter - 1 : counter]),
                    turf.point(route.features[0].geometry.coordinates[counter >= steps ? counter : counter + 1])
                );
            }
            
            map.getSource('point').setData(point);
            
            if (counter < steps) {
                requestAnimationFrame(animate);
            } else if(counter == steps) {
                let RouteLength = route.features[0].geometry.coordinates.length;
                point.features[0].geometry.coordinates = route.features[0].geometry.coordinates[RouteLength - 1];
            }
            counter = counter + 1;
        }

        document.getElementById('replay').addEventListener('click', function() {
            point.features[0].geometry.coordinates = origin;
            
            map.getSource('point').setData(point);
            
            counter = 0;
            
            animate(counter);
        });
        
        animate(counter);

        DrawPhotos(path);
    }
}

function DrawPhotos(path) {
    // draw photos //
    // let path_ = path;
    let widthCamera = document.getElementById('photo-width').value,
        heightCamera = document.getElementById('photo-height').value,
        H = document.getElementById('height').value,
        F = document.getElementById('focus').value,
        radian = document.getElementById('radian').value;

    for(let i = 1; i < path.length - 1; i++) {
        let size = size_photo(widthCamera, heightCamera, H, F);
        console.log('WIDTH:', size[0], 'HEIGHT:', size[1]);
        console.log('RADIAN:', radian, "DEGREES:", radian);
        console.log(path[i]);
        let p = path[i];
        path[i] = ConvertPoint(path[i]);
        console.log(path[i]);
        let leftUP = [path[i][0] - size[0] / 2, path[i][1] + size[1] / 2],
            rightUP = [path[i][0] + size[0] / 2, path[i][1] + size[1] / 2],
            leftDown = [path[i][0] - size[0] / 2, path[i][1] - size[1] / 2],
            rightDown = [path[i][0] + size[0] / 2, path[i][1] - size[1] / 2];
        console.log(leftUP, rightUP, rightDown, leftDown);
        let rect = [leftUP, rightUP, rightDown, leftDown];
        path[i] = UnConvertPoint(path[i]);
        for(let j = 0; j < rect.length; j++) {
            rect[j] = UnConvertPoint(rect[j]);
            console.log('RECT:', rect[j]);
            // rect[j][0] -= path[i][0];
            // rect[j][1] -= path[i][1];
            // console.log('RECT:', rect[j]);
            // rect[j] = turn_dot(rect[j], -radian);
            // console.log('RECT:', rect[j]);
            // rect[j][0] += path[i][0];
            // rect[j][1] += path[i][1];
            // console.log('RECT:', rect[j]);
        }
        console.log(p);
        console.log(rect);

        map.addLayer({
            'id': 'photo ' + String(i),
            'type': 'fill',
            'source': {
                'type': 'geojson',
                'data': {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [rect]
                    }
                }
            },
            'layout': {},
            'paint': {
                'fill-color': 'green',
                'fill-opacity': 0.4,
                'fill-outline-color': 'rgba(0, 255, 0, 1)'
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
			"line-color": "blue",
			"line-width": 4
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

function size_photo(widthCamera, heightCamera, H, F) {
    console.log(widthCamera, heightCamera, H, F);
    width = widthCamera * (H / F);
    height = heightCamera * (H / F);
    return [width, height];
}

function UnConvertPoint(point) {
    point[0] /= (111 * 1000);
    point[1] /= (111 * 1000);

    return point;
}

function ConvertPoint(point) {
    point[0] *= 111 * 1000;
    point[1] *= 111 * 1000;

    return point;
}

function turn_dot(point, radian) {
    sin = Math.sin(radian)
    cos = Math.cos(radian)
    point[0] = point[0] * cos - point[1] * sin
    point[1] = point[0] * sin + point[1] * cos

    console.log(point);
    return point;
}