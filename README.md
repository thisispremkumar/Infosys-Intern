# Small Business Sales & Profit Analyzer

A comprehensive Streamlit-based web application for analyzing sales and profit data for small businesses.

## Features

### 🔐 Login Page
- Secure authentication system
- Demo credentials provided for testing
- Clean and modern UI design

### 📊 Dashboard
- **Key Performance Indicators (KPIs)**
  - Total Sales
  - Total Profit
  - Average Profit Margin
  - Total Orders

- **Interactive Charts**
  - Sales trend over time (line chart)
  - Profit trend over time (area chart)
  - Sales by category (pie chart)
  - Sales by region (bar chart)
  - Profit margin analysis by category

- **Data Filtering**
  - Time period selection (Last 7/30/90 days, Last Year, All Time)
  - Category filtering
  - Region filtering

- **Data Table**
  - Recent transactions view
  - Top 10 sales days
  - Export data to CSV

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Run the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Demo Credentials

Use any of these credentials to login:
- Username: `admin` | Password: `admin123`
- Username: `demo` | Password: `demo123`
- Username: `user` | Password: `user123`

## Application Structure

- `app.py` - Main application file containing:
  - Login page implementation
  - Dashboard with analytics
  - Data generation and filtering
  - Interactive visualizations

- `requirements.txt` - Python dependencies

## Technologies Used

- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive charts and visualizations
- **NumPy** - Numerical computations

## Features in Detail

### Login System
- Session state management
- Secure password handling
- User-friendly interface

### Dashboard Analytics
- Real-time data visualization
- Multiple chart types for comprehensive analysis
- Responsive design that works on different screen sizes
- Color-coded metrics with trend indicators

### Data Management
- Sample data generation for demonstration
- CSV export functionality
- Customizable date ranges and filters

## Future Enhancements

- Database integration for persistent data storage
- User registration and profile management
- Advanced analytics and forecasting
- Email reports and notifications
- Multi-user role management
- Real-time data updates

## Notes

This application currently uses sample generated data for demonstration purposes. In a production environment, you would connect it to your actual business database or data sources.
