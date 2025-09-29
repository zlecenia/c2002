document.addEventListener('DOMContentLoaded', function() {
    const apiTestButton = document.getElementById('api-test');
    const apiResult = document.getElementById('api-result');

    apiTestButton.addEventListener('click', async function() {
        try {
            apiResult.style.display = 'block';
            apiResult.className = 'api-result';
            apiResult.innerHTML = 'Testing API...';

            const response = await fetch('/api/hello');
            const data = await response.json();

            if (response.ok) {
                apiResult.className = 'api-result success';
                apiResult.innerHTML = `<strong>Success!</strong> API Response: ${data.message}`;
            } else {
                throw new Error('API request failed');
            }
        } catch (error) {
            apiResult.className = 'api-result error';
            apiResult.innerHTML = `<strong>Error!</strong> ${error.message}`;
        }
    });
});