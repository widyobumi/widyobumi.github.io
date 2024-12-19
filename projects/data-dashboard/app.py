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
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    sales = pd.Series(range(len(dates))) * 10 + pd.Series(range(len(dates))).apply(lambda x: x % 50)
    df = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'category': ['Electronics' if i % 3 == 0 else 'Clothing' if i % 3 == 1 else 'Books' for i in range(len(dates))]
    })
    return df

# Global variable to store our data
DATA = generate_sample_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    # Get query parameters
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    category = request.args.get('category', None)
    
    # Filter data based on parameters
    filtered_data = DATA.copy()
    
    if start_date:
        filtered_data = filtered_data[filtered_data['date'] >= start_date]
    if end_date:
        filtered_data = filtered_data[filtered_data['date'] <= end_date]
    if category:
        filtered_data = filtered_data[filtered_data['category'] == category]
    
    # Create visualizations
    sales_over_time = px.line(filtered_data, 
                             x='date', 
                             y='sales',
                             title='Sales Over Time')
    
    sales_by_category = px.pie(filtered_data.groupby('category')['sales'].sum().reset_index(),
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
        'total_sales': filtered_data['sales'].sum(),
        'average_daily_sales': filtered_data['sales'].mean(),
        'top_category': filtered_data.groupby('category')['sales'].sum().idxmax()
    }
    
    return jsonify({
        'charts': charts,
        'summary': summary
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            global DATA
            DATA = pd.read_csv(file)
            return jsonify({'message': 'File uploaded successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Invalid file format. Please upload a CSV file'}), 400

if __name__ == '__main__':
    app.run(debug=True)
