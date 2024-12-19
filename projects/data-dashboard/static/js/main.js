// Function to update the dashboard
async function updateDashboard() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const category = document.getElementById('category').value;

    // Build query parameters
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (category) params.append('category', category);

    try {
        const response = await fetch(`/api/data?${params.toString()}`);
        const data = await response.json();

        // Update charts
        Plotly.newPlot('sales-over-time', data.charts.sales_over_time.data, data.charts.sales_over_time.layout);
        Plotly.newPlot('sales-by-category', data.charts.sales_by_category.data, data.charts.sales_by_category.layout);

        // Update summary statistics
        document.getElementById('total-sales').textContent = `$${data.summary.total_sales.toFixed(2)}`;
        document.getElementById('avg-sales').textContent = `$${data.summary.average_daily_sales.toFixed(2)}`;
        document.getElementById('top-category').textContent = data.summary.top_category;
    } catch (error) {
        console.error('Error updating dashboard:', error);
        alert('Error updating dashboard. Please try again.');
    }
}

// Function to handle file upload
async function uploadFile() {
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a file to upload');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert('File uploaded successfully');
            updateDashboard();
        } else {
            alert(result.error || 'Error uploading file');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error uploading file. Please try again.');
    }
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
});
