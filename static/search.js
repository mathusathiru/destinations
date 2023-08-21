// script executed on the submit event of search.html pager form (id #search-form)
document.getElementById("search-form").addEventListener('submit', async function (event) {
    // prevent default form submission behavior
    event.preventDefault();
    // obtain form element triggering the event
    const form = event.target;
    // create FormData object from the form
    const formData = new FormData(form);

    // obtain selected radius from the radio buttons
    const selectedRadius = document.querySelector('#radius-buttons input[name="radius"]:checked');
    if (selectedRadius) {
        // append selected radius to FormData object
        formData.append('radius', selectedRadius.value);

        // clear error message from a previous search
        document.getElementById('error-message').innerText = '';

        // remove the map container if it already exists from a previous search
        const mapContainer = document.getElementById('map');
        if (mapContainer) {
            mapContainer.remove();
        }

        // clear the results container if it already exists from a previous search
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.innerHTML = '';

        try {
            // send a POST request to the form action URL with the FormData
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });
            // parse the response as JSON
            const data = await response.json();

            // display an error message if an error occurs with the response data
            if (data.error) {
                document.getElementById('error-message').innerText = data.error;
            } else if (data.results) {
                // if results are present from the response data, display them on a map
                const resultsContainer = document.getElementById('results-container');

                // create a new map container element and append it to results container
                const newMapContainer = document.createElement('div');
                newMapContainer.id = 'map';
                newMapContainer.style.width = '96.5%';
                newMapContainer.style.height = '600px';
                resultsContainer.appendChild(newMapContainer);

                // initialize a Leaflet map with a view centered on specific coordinates and zoom level
                const map = L.map("map").setView([51.61794, -0.017785], 14);

                // add a map tile layer using OpenStreetMap tiles and attribution
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);

                // iterate through results, adding a marker for each result
                data.results.forEach(result => {
                    // create a custom marker icon using a png file
                    const customIcon = L.icon({
                        iconUrl: '/static/images/marker.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                    });
                
                    // add marker to a coordinate utilising the custom icon
                    const marker = L.marker([result.geocodes.main.latitude, result.geocodes.main.longitude], { icon: customIcon }).addTo(map);
                    // attach a popup to the marker displaying results information (place name and address)
                    marker.bindPopup(`<b>${result.name}</b><br>${result.location.formatted_address}`);
                });
            }
        } catch (error) {
            // display an error message if unknown errors occur during the search API calls
            document.getElementById('error-message').innerText = 'An error occurred during the search.';
        }
    } else {
        // display an error message if no radius value is selected
        document.getElementById('error-message').innerText = 'Please select a radius.';
    }
});