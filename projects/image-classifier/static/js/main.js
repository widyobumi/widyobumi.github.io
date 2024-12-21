document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const sampleBtn = document.getElementById('sample-btn');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const results = document.getElementById('results');
    const predictionsList = document.getElementById('predictions-list');
    const loading = document.getElementById('loading');

    // Drag and drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && isImageFile(file)) {
            handleFile(file);
        }
    });

    // Click to upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            handleFile(file);
        }
    });

    // Upload button handler
    uploadBtn.addEventListener('click', () => {
        const file = fileInput.files[0];
        if (file) {
            uploadImage(file);
        } else {
            alert('Please select an image first');
        }
    });

    // Sample button handler
    sampleBtn.addEventListener('click', () => {
        showLoading();
        fetch('/sample')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayResults(data);
                } else {
                    showError(data.error);
                }
            })
            .catch(error => {
                showError('Error loading sample image');
                console.error('Error:', error);
            })
            .finally(() => {
                hideLoading();
            });
    });

    function handleFile(file) {
        if (isImageFile(file)) {
            previewImage.src = URL.createObjectURL(file);
            previewContainer.classList.remove('d-none');
            results.classList.add('d-none');
        } else {
            alert('Please upload an image file (JPG, JPEG, PNG, or GIF)');
        }
    }

    function isImageFile(file) {
        const acceptedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        return acceptedTypes.includes(file.type);
    }

    function uploadImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        showLoading();

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayResults(data);
            } else {
                showError(data.error);
            }
        })
        .catch(error => {
            showError('Error uploading image');
            console.error('Error:', error);
        })
        .finally(() => {
            hideLoading();
        });
    }

    function displayResults(data) {
        console.log('Received data:', data); // Debug log
        
        // Update current image preview
        previewImage.src = data.image_url;
        previewContainer.classList.remove('d-none');
        results.classList.remove('d-none');
        predictionsList.innerHTML = '';

        // Create main container
        const mainContainer = document.createElement('div');
        mainContainer.className = 'container-fluid mt-4';
        
        // Current Image Analysis
        const currentAnalysis = document.createElement('div');
        currentAnalysis.innerHTML = '<h3>Current Image Analysis:</h3>';
        data.predictions.forEach(prediction => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `${prediction.label}: <span class="badge bg-primary">${prediction.confidence.toFixed(1)}%</span>`;
            currentAnalysis.appendChild(li);
        });
        mainContainer.appendChild(currentAnalysis);

        // Display previous image comparison if available
        if (data.previous_analysis) {
            console.log('Previous analysis available:', data.previous_analysis);
            
            // Images comparison section
            const imagesSection = document.createElement('div');
            imagesSection.className = 'row mt-4';
            imagesSection.innerHTML = `
                <h3>Image Comparison:</h3>
                <div class="col-md-6 text-center">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Current Image</h5>
                            <img src="${data.image_url}" class="img-fluid" alt="Current image" 
                                 style="max-height: 300px; width: auto; object-fit: contain;">
                        </div>
                    </div>
                </div>
                <div class="col-md-6 text-center">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Previous Image</h5>
                            <img src="${data.previous_analysis.image_url}" class="img-fluid" alt="Previous image" 
                                 style="max-height: 300px; width: auto; object-fit: contain;">
                        </div>
                    </div>
                </div>
            `;
            mainContainer.appendChild(imagesSection);

            // Comparison table
            const tableSection = document.createElement('div');
            tableSection.className = 'mt-4';
            tableSection.innerHTML = '<h3>Detailed Comparison:</h3>';
            
            const table = document.createElement('table');
            table.className = 'table table-striped mt-3';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Characteristic</th>
                        <th>Current Image</th>
                        <th>Previous Image</th>
                        <th>Difference</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            `;
            
            // Map predictions by label
            const currentPredictions = Object.fromEntries(
                data.predictions.map(p => [p.label, p.confidence])
            );
            const previousPredictions = Object.fromEntries(
                data.previous_analysis.predictions.map(p => [p.label, p.confidence])
            );
            
            // Add all unique labels to comparison
            const allLabels = [...new Set([
                ...Object.keys(currentPredictions),
                ...Object.keys(previousPredictions)
            ])].sort();
            
            allLabels.forEach(label => {
                const current = currentPredictions[label] || 0;
                const previous = previousPredictions[label] || 0;
                const difference = (current - previous).toFixed(1);
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${label}</td>
                    <td>${current.toFixed(1)}%</td>
                    <td>${previous.toFixed(1)}%</td>
                    <td class="${difference > 0 ? 'text-success' : difference < 0 ? 'text-danger' : ''}">
                        ${difference > 0 ? '+' : ''}${difference}%
                    </td>
                `;
                table.querySelector('tbody').appendChild(row);
            });
            
            tableSection.appendChild(table);
            mainContainer.appendChild(tableSection);
        }
        
        predictionsList.appendChild(mainContainer);
    }

    function showLoading() {
        loading.classList.remove('d-none');
        results.classList.add('d-none');
    }

    function hideLoading() {
        loading.classList.add('d-none');
    }

    function showError(message) {
        alert(message);
    }
});
