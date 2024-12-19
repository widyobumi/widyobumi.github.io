# Data Analysis Dashboard

A web-based dashboard for visualizing and analyzing sales data, built with Python Flask and Plotly.

## Features

- Interactive data visualization with Plotly charts
- Real-time data filtering by date and category
- CSV file upload functionality
- Summary statistics display
- Responsive design for all devices

## Technologies Used

- Backend: Python, Flask
- Data Processing: Pandas, NumPy
- Visualization: Plotly.js
- Frontend: HTML5, CSS3, JavaScript
- Styling: Bootstrap 5

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open http://localhost:5000 in your browser

## Usage

1. View default sample data visualization
2. Upload your own CSV file (must include 'date', 'sales', and 'category' columns)
3. Use filters to analyze specific date ranges and categories
4. View updated charts and summary statistics in real-time

## Project Structure

```
data-dashboard/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css  # Custom styles
│   └── js/
│       └── main.js    # Frontend JavaScript
├── templates/
│   └── index.html     # Main dashboard template
└── README.md          # Project documentation
```

## Future Improvements

- Add more chart types and visualization options
- Implement data export functionality
- Add user authentication
- Add data caching for better performance
- Implement more advanced analytics features
