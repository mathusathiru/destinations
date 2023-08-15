document.getElementById("search-form").addEventListener('submit', async function (event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const selectedRadius = document.querySelector('#radius-buttons input[name="radius"]:checked');;
    if (selectedRadius) {
        formData.append('radius', selectedRadius.value);

        document.getElementById('error-message').innerText = '';

        const mapContainer = document.getElementById('map');
        if (mapContainer) {
            mapContainer.remove();
        }

        const resultsContainer = document.getElementById('results-container');
        resultsContainer.innerHTML = '';

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();

            if (data.error) {
                document.getElementById('error-message').innerText = data.error;
            } else if (data.results) {
                const resultsContainer = document.getElementById('results-container');

                const newMapContainer = document.createElement('div');
                newMapContainer.id = 'map';
                newMapContainer.style.width = '96.5%';
                newMapContainer.style.height = '600px';
                resultsContainer.appendChild(newMapContainer);

                const map = L.map('map').setView([51.61794, -0.017785], 14);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);

                data.results.forEach(result => {
                    const customIcon = L.icon({
                        iconUrl: '/static/images/marker.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                    });
                
                    const marker = L.marker([result.geocodes.main.latitude, result.geocodes.main.longitude], { icon: customIcon }).addTo(map);
                    marker.bindPopup(`<b>${result.name}</b><br>${result.location.formatted_address}`);
                });
                         

            }
        } catch (error) {
            document.getElementById('error-message').innerText = 'An error occurred during the search.';
        }
    } else {
        document.getElementById('error-message').innerText = 'Please select a radius.';
    }
});
