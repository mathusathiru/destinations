document.getElementById('searchForm').addEventListener('submit', function (event) {
    event.preventDefault(); 
    const form = event.target;
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('hiddenParagraph').innerText = data.error;
        } else {
            if (data.results) {
                const resultsContainer = document.getElementById('resultsContainer');
                resultsContainer.innerHTML = '';

                const resultsList = document.createElement('ul');
                data.results.forEach(result => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `Place Name: ${result.name}\nAddress: ${result.location.formatted_address}`;
                    resultsList.appendChild(listItem);
                });

                resultsContainer.appendChild(resultsList);
            }
        }
    })
    .catch(error => {
        document.getElementById('hiddenParagraph').innerText = 'An error occurred during the search.';
    });
});
