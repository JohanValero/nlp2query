function sendPrompt() {
    const prompt = document.getElementById('promptInput').value;
    document.getElementById('results').innerHTML = "";
    fetch(`/api/v0/generate_sql?prompt=${encodeURIComponent(prompt)}`)
        .then(response => response.json())
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            document.getElementById('results').innerHTML = '<h3>Error al procesar la solicitud.</h3><p>' + error + '</p>';
        });
}

function displayResults(data) {
    let resultsHtml = '<h2>Resultados:</h2>';

    // Mostrar pasos de steps_info
    resultsHtml += '<h3>Pasos de procesamiento:</h3>';
    for (const [key, value] of Object.entries(data.steps_info)) {
        resultsHtml += `<p><strong>${key}:</strong> ${value}</p>`;
    }

    // Mostrar SQL generado
    resultsHtml += `<h3>SQL Generado:</h3><p>${data.sql}</p>`;

    // Crear tabla de registros
    if (data.records && data.records.length > 0) {
        resultsHtml += '<h3>Registros:</h3>';
        resultsHtml += '<table><tr>';
        for (const key in data.records[0]) {
            resultsHtml += `<th>${key}</th>`;
        }
        resultsHtml += '</tr>';
        data.records.forEach(record => {
            resultsHtml += '<tr>';
            for (const value of Object.values(record)) {
                resultsHtml += `<td>${value}</td>`;
            }
            resultsHtml += '</tr>';
        });
        resultsHtml += '</table>';
    } else {
        resultsHtml += '<p>No se encontraron registros.</p>';
    }

    document.getElementById('results').innerHTML = resultsHtml;
}