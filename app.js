document.getElementById('addStockForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const response = await fetch('/add_stock', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    const responseDiv = document.getElementById('response');
    if (result.message) {
        responseDiv.innerHTML = `<p style="color: green;">${result.message}</p>`;
    } else {
        responseDiv.innerHTML = `<p style="color: red;">${result.error}</p>`;
    }

    e.target.reset();
});
