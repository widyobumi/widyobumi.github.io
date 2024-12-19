from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import plotly.utils
import json
import os
from datetime import datetime

app = Flask(__name__)

# Sample data (we'll replace this with file upload functionality later)
def generate_sample_data():
    print("Generating sample data...")
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    sales = pd.Series(range(len(dates))) * 10 + pd.Series(range(len(dates))).apply(lambda x: x % 50)
    df = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'category': ['Electronics' if i % 3 == 0 else 'Clothing' if i % 3 == 1 else 'Books' for i in range(len(dates))]
    })
    print(f"Generated {len(df)} rows of sample data")
    return df

# Global variable to store our data
DATA = generate_sample_data()

@app.route('/')
def index():
    print("Serving index page...")
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    print("Received data request with params:", request.args)
    try:
        # Get query parameters
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        category = request.args.get('category', None)
        
        # Filter data based on parameters
        filtered_data = DATA.copy()
        print(f"Initial data shape: {filtered_data.shape}")
        
        if start_date:
            filtered_data = filtered_data[filtered_data['date'] >= start_date]
        if end_date:
            filtered_data = filtered_data[filtered_data['date'] <= end_date]
        if category:
            filtered_data = filtered_data[filtered_data['category'] == category]
        
        print(f"Filtered data shape: {filtered_data.shape}")
        
        # Check if we have any data after filtering
        if filtered_data.empty:
            print("No data found after filtering")
            return jsonify({
                'error': 'No data found for the selected filters',
                'charts': {
                    'sales_over_time': {},
                    'sales_by_category': {}
                },
                'summary': {
                    'total_sales': 0,
                    'average_daily_sales': 0,
                    'top_category': 'N/A'
                }
            })

        # Create visualizations
        print("Creating visualizations...")
        sales_over_time = px.line(filtered_data, 
                                x='date', 
                                y='sales',
                                title='Sales Over Time')
        
        category_data = filtered_data.groupby('category')['sales'].sum().reset_index()
        print("Category summary:", category_data)
        
        sales_by_category = px.pie(category_data,
                                values='sales',
                                names='category',
                                title='Sales by Category')
        
        # Convert plots to JSON
        charts = {
            'sales_over_time': json.loads(sales_over_time.to_json()),
            'sales_by_category': json.loads(sales_by_category.to_json())
        }
        
        # Calculate summary statistics
        summary = {
            'total_sales': float(filtered_data['sales'].sum()),
            'average_daily_sales': float(filtered_data['sales'].mean()),
            'top_category': filtered_data.groupby('category')['sales'].sum().idxmax()
        }
        
        print("Summary statistics:", summary)
        
        return jsonify({
            'charts': charts,
            'summary': summary
        })
    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'An error occurred while processing the data',
            'details': str(e)
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Received file upload request")
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            global DATA
            DATA = pd.read_csv(file)
            if 'date' in DATA.columns:
                DATA['date'] = pd.to_datetime(DATA['date'])
            print(f"Successfully loaded CSV with shape: {DATA.shape}")
            return jsonify({'message': 'File uploaded successfully'})
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Invalid file format. Please upload a CSV file'}), 400

if __name__ == '__main__':
    print("Starting Flask application...")
    print("Sample data shape:", DATA.shape)
    print("Access the dashboard at http://localhost:5000")
    app.run(debug=True, port=5000)
