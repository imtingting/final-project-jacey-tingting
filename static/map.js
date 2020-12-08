	// TO MAKE THE MAP APPEAR YOU MUST
	// ADD YOUR ACCESS TOKEN FROM
	// https://account.mapbox.com
	mapboxgl.accessToken = '{{ mapbox_token }}';
    var places = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'grocery'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ center_lng }}, {{ center_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'convenience',
                    'description':
                         "<strong>Seersucker Bike Ride and Social</strong><p>Feeling dandy? Get fancy, grab your bike, and take part in this year's Seersucker Social bike ride from Dandies and Quaintrelles. After the ride enjoy a lawn party at Hillwood with jazz, cocktails, paper hat-making, and more. 11:00-7:00 p.m.</p>"
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ market1_lng }}, {{ market1_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'convenience'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ market2_lng }}, {{ market2_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'convenience'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ market3_lng }}, {{ market3_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'convenience'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ market4_lng }}, {{ market4_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'convenience'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ market5_lng }}, {{ market5_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'fast-food'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ fast_food1_lng }}, {{ fast_food1_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'fast-food'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ fast_food2_lng }}, {{ fast_food2_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'fast-food'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ fast_food3_lng }}, {{ fast_food3_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'fast-food'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ fast_food4_lng }}, {{ fast_food4_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'fast-food'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ fast_food5_lng }}, {{ fast_food5_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'grocery',
                    'description':
                         "<strong>Seersucker Bike Ride and Social</strong><p>Feeling dandy? Get fancy, grab your bike, and take part in this year's Seersucker Social bike ride from Dandies and Quaintrelles. After the ride enjoy a lawn party at Hillwood with jazz, cocktails, paper hat-making, and more. 11:00-7:00 p.m.</p>"
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ supermarket1_lng }}, {{ supermarket1_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'grocery'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ supermarket2_lng }}, {{ supermarket2_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'grocery'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ supermarket3_lng }}, {{ supermarket3_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'grocery'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ supermarket4_lng }}, {{ supermarket4_lat }}]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'icon': 'grocery'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [{{ supermarket5_lng }}, {{ supermarket5_lat }}]
                }
            }           
        ]
    };

    var filterGroup = document.getElementById('filter-group');
    var map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/light-v10',
        center: [{{ center_lng }}, {{ center_lat }}],
        zoom: 15
    });

    map.on('load', function () {
        // Add a GeoJSON source containing place coordinates and information.
        map.addSource('places', {
            'type': 'geojson',
            'data': places
        });

        places.features.forEach(function (feature) {
            var symbol = feature.properties['icon'];
            var layerID = 'poi-' + symbol;

            // Add a layer for this symbol type if it hasn't been added already.
            if (!map.getLayer(layerID)) {
                map.addLayer({
                    'id': layerID,
                    'type': 'symbol',
                    'source': 'places',
                    'layout': {
                        'icon-image': symbol + '-15',
                        'icon-size': 2,
                        'icon-allow-overlap': true
                    },
                    'filter': ['==', 'icon', symbol]
                });

                // Add checkbox and label elements for the layer.
                var input = document.createElement('input');
                input.type = 'checkbox';
                input.id = layerID;
                input.checked = true;
                filterGroup.appendChild(input);

                var label = document.createElement('label');
                label.setAttribute('for', layerID);
                label.textContent = symbol;
                filterGroup.appendChild(label);

                // When the checkbox changes, update the visibility of the layer.
                input.addEventListener('change', function (e) {
                    map.setLayoutProperty(
                        layerID,
                        'visibility',
                        e.target.checked ? 'visible' : 'none'
                    );
                });
            }
        });
        // // Add a marker to the input address
        // map.loadImage(
        //     'https://docs.mapbox.com/mapbox-gl-js/assets/custom_marker.png',
        //     // Add an image to use as a custom marker
        //     function (error, image) {
        //         if (error) throw error;
        //         map.addImage('custom-marker', image);
        //         map.addSource('point', {
        //             'type': 'geojson',
        //             'data': {
        //                 'type': 'FeatureCollection',
        //                 'features': [
        //                     {'type': 'Feature',
        //                     'geometry': {
        //                         'type': 'Point',
        //                         'coordinates': [{{ center_lng }}, {{ center_lat }}]
        //                         }
        //                         }]
        //                         }});
        //         map.addLayer({
        //             'id': 'places',
        //             'type': 'symbol',
        //             'source': 'places',
        //             'layout': {
        //                 'icon-image': 'custom-marker',
        //                 'icon-allow-overlap': true
        //                 }}
        //                 )});
        // Create a popup, but don't add it to the map yet.
        var popup = new mapboxgl.Popup({
            closeButton: false,
            closeOnClick: false
        });

        places.features.forEach(function (feature) {
            var symbol = feature.properties['icon'];
            var layerID = 'poi-' + symbol;

        map.on('mouseenter', layerID, function (e) {

            console.log("inside mouseenter");
            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = 'pointer';

            var coordinates = e.features[0].geometry.coordinates.slice();
            var description = e.features[0].properties.description;

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }

            // Populate the popup and set its coordinates
            // based on the feature found.
            popup.setLngLat(coordinates).setHTML(description).addTo(map);
        });



        map.on('mouseleave',layerID, function () {
            map.getCanvas().style.cursor = '';
            popup.remove();
        });

        })
    });