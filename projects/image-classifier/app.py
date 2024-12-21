import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image
import numpy as np
import cv2
import io
import time
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store both current and previous analysis
current_analysis = None
previous_analysis = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def get_unique_filename(filename):
    # Get the file extension
    ext = os.path.splitext(filename)[1]
    # Create a unique filename using timestamp and a random component
    unique_filename = f"image_{int(time.time())}_{secure_filename(filename)}"
    return unique_filename

def analyze_image(img_path):
    # Read image with OpenCV
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize image for consistent processing
    img_resized = cv2.resize(img, (224, 224))
    
    # Convert to different color spaces
    img_gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    img_hsv = cv2.cvtColor(img_resized, cv2.COLOR_RGB2HSV)
    
    # Calculate basic image statistics
    brightness = np.mean(img_gray)
    contrast = np.std(img_gray)
    
    # Calculate color statistics
    color_stats = {
        'red': float(np.mean(img_resized[:,:,0])),
        'green': float(np.mean(img_resized[:,:,1])),
        'blue': float(np.mean(img_resized[:,:,2])),
        'saturation': float(np.mean(img_hsv[:,:,1])),
        'value': float(np.mean(img_hsv[:,:,2]))
    }
    
    # Edge detection
    edges = cv2.Canny(img_gray, 100, 200)
    edge_density = float(np.count_nonzero(edges)) / (edges.shape[0] * edges.shape[1])
    
    # Initialize predictions list
    predictions = []
    
    # Analyze brightness
    if brightness > 180:
        predictions.append({
            'label': 'Bright Image',
            'confidence': min((brightness / 255.0) * 100, 100)
        })
    elif brightness < 70:
        predictions.append({
            'label': 'Dark Image',
            'confidence': min((1 - brightness / 255.0) * 100, 100)
        })
    
    # Analyze contrast
    if contrast > 50:
        predictions.append({
            'label': 'High Contrast',
            'confidence': min((contrast / 128.0) * 100, 100)
        })
    
    # Analyze color dominance
    max_color = max(color_stats.items(), key=lambda x: x[1] if x[0] not in ['saturation', 'value'] else 0)
    if max_color[0] not in ['saturation', 'value']:
        predictions.append({
            'label': f'{max_color[0].title()} Dominant',
            'confidence': min((max_color[1] / 255.0) * 100, 100)
        })
    
    # Analyze edge density (complexity)
    if edge_density > 0.1:
        predictions.append({
            'label': 'Complex Image',
            'confidence': min(edge_density * 500, 100)
        })
    else:
        predictions.append({
            'label': 'Simple Image',
            'confidence': min((1 - edge_density) * 100, 100)
        })
    
    # Analyze saturation
    if color_stats['saturation'] > 128:
        predictions.append({
            'label': 'Vibrant Colors',
            'confidence': min((color_stats['saturation'] / 255.0) * 100, 100)
        })
    else:
        predictions.append({
            'label': 'Muted Colors',
            'confidence': min((1 - color_stats['saturation'] / 255.0) * 100, 100)
        })
    
    return predictions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_analysis, previous_analysis
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Create unique filename
        unique_filename = get_unique_filename(file.filename)
        filename = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file
        file.save(filename)
        
        # Process the image and get predictions
        predictions = analyze_image(filename)
        
        # Update analysis storage
        if current_analysis:
            previous_analysis = current_analysis.copy()
        
        current_analysis = {
            'predictions': predictions,
            'image_url': f'/static/uploads/{os.path.basename(filename)}'
        }
        
        # Prepare response with both current and previous analysis
        response = {
            'success': True,
            'predictions': predictions,
            'image_url': current_analysis['image_url'],
            'previous_analysis': previous_analysis
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sample')
def sample():
    # Process a sample image for demonstration
    sample_image = os.path.join(app.config['UPLOAD_FOLDER'], 'sample.jpg')
    if os.path.exists(sample_image):
        predictions = analyze_image(sample_image)
        return jsonify({
            'success': True,
            'predictions': predictions,
            'image_url': f'/static/uploads/sample.jpg'
        })
    return jsonify({'error': 'Sample image not found'}), 404

@app.route('/static/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("Starting Image Classifier application...")
    print("Access the application at http://localhost:5000")
    app.run(debug=True, port=5000)
