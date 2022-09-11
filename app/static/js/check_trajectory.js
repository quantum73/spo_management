function create_map_with_line() {
    var map = new maplibregl.Map({
        container: 'map',
        style:
            'https://api.maptiler.com/maps/streets/style.json?key=get_your_own_OpIi9ZULNHzrESv6T2vL',
        center: [38.821689922123085, 55.03458254373058],
        zoom: 14
    });

    // GeoJSON object to hold our measurement features
    var geojson = {
        'type': 'FeatureCollection',
        'features': []
    };

    // Used to draw a line between points
    var linestring = {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': []
        }
    };

    map.on('load', function () {
        map.addSource('geojson', {
            'type': 'geojson',
            'data': geojson
        });

        // Add styles to the map
        map.addLayer({
            id: 'measure-points',
            type: 'circle',
            source: 'geojson',
            paint: {
                'circle-radius': 5,
                'circle-color': '#000'
            },
            filter: ['in', '$type', 'Point']
        });
        map.addLayer({
            id: 'measure-lines',
            type: 'line',
            source: 'geojson',
            layout: {
                'line-cap': 'round',
                'line-join': 'round'
            },
            paint: {
                'line-color': '#000',
                'line-width': 1.5
            },
            filter: ['in', '$type', 'LineString']
        });

        map.on('click', function (e) {
            var features = map.queryRenderedFeatures(e.point, {
                layers: ['measure-points']
            });

            // Remove the linestring from the group
            // So we can redraw it based on the points collection
            if (geojson.features.length > 1) geojson.features.pop();

            // If a feature was clicked, remove it from the map
            if (features.length) {
                var id = features[0].properties.id;
                geojson.features = geojson.features.filter(function (point) {
                    return point.properties.id !== id;
                });
            } else {
                var point = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [e.lngLat.lng, e.lngLat.lat]
                    },
                    'properties': {
                        'id': String(new Date().getTime())
                    }
                };
                geojson.features.push(point);

                if (geojson.features.length === 1) {
                    $("#start_x_target").val(e.lngLat.lng);
                    $("#start_y_target").val(e.lngLat.lat);
                } else if (geojson.features.length === 2) {
                    $("#finish_x_target").val(e.lngLat.lng);
                    $("#finish_y_target").val(e.lngLat.lat);
                }
            }

            if (geojson.features.length > 1) {
                linestring.geometry.coordinates = geojson.features.map(
                    function (point) {
                        return point.geometry.coordinates;
                    }
                );

                geojson.features.push(linestring);
            }

            map.getSource('geojson').setData(geojson);
        });
    });

    map.on('mousemove', function (e) {
        var features = map.queryRenderedFeatures(e.point, {
            layers: ['measure-points']
        });
        // UI indicator for clicking/hovering a point on the map
        map.getCanvas().style.cursor = features.length
            ? 'pointer'
            : 'crosshair';
    });
}


function create_map_with_interest_point() {
    var map = new maplibregl.Map({
        container: 'map',
        style:
            'https://api.maptiler.com/maps/streets/style.json?key=get_your_own_OpIi9ZULNHzrESv6T2vL',
        center: [38.821689922123085, 55.03458254373058],
        zoom: 14
    });

    var marker = new maplibregl.Marker({
        draggable: true
    })
        .setLngLat([38.821689922123085, 55.03458254373058])
        .addTo(map);

    $("#x_target").val(38.821689922123085);
    $("#y_target").val(55.03458254373058);

    function onDragEnd() {
        var lngLat = marker.getLngLat();
        $("#x_target").val(lngLat.lng);
        $("#y_target").val(lngLat.lat);
    }

    marker.on('dragend', onDragEnd);
}

function check_trajectory_select(select_element) {
    let glyssade_block = $(".glyssade-block");
    let ellipse_block = $(".ellipse-block");

    if (select_element.value === "glissade") {
        glyssade_block.show();
        ellipse_block.hide();
        glyssade_block.find(':input').prop("required", true);
        ellipse_block.find(':input').prop("required", false);
        create_map_with_line();
    } else {
        ellipse_block.show();
        glyssade_block.hide();
        ellipse_block.find(':input').prop("required", true);
        glyssade_block.find(':input').prop("required", false);
        create_map_with_interest_point();
    }
}

let trajectory = $(".trajectory-select");
$(".glyssade-block").find(':input').prop("required", true);
create_map_with_line();
$(".ellipse-block").hide();

trajectory.change(function () {
    check_trajectory_select(this);
});