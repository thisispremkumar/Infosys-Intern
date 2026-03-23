---
title: Small Business Sales & Profit Analyzer
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

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
  - Reports & Email page

- `pdf_report.py` - PDF report generation using fpdf2
- `email_service.py` - SMTP email automation service
- `db.py` - Supabase database operations
- `supabase_client.py` - Supabase client configuration
- `requirements.txt` - Python dependencies

## Technologies Used

- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive charts and visualizations
- **NumPy** - Numerical computations
- **fpdf2** - PDF report generation
- **smtplib** - Email automation (built-in Python)
- **Supabase** - Cloud database backend

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

- Advanced analytics and forecasting
- Multi-user role management
- Real-time data updates

## Deployment / Hosting

### Streamlit Community Cloud (Recommended - Free)
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo and select `app.py`
4. Add `SUPABASE_URL` and `SUPABASE_KEY` in the **Secrets** section (TOML format):
   ```toml
   SUPABASE_URL = "your-url"
   SUPABASE_KEY = "your-key"
   ```
5. Click **Deploy**

### Docker
```bash
docker build -t business-analyzer .
docker run -p 8501:8501 --env-file .env business-analyzer
```

### Render / Railway / Heroku
The repo includes `Procfile` and `render.yaml` for one-click deployment on these platforms. Set the `SUPABASE_URL` and `SUPABASE_KEY` environment variables in the hosting dashboard.

## Notes

This application currently uses sample generated data for demonstration purposes. In a production environment, you would connect it to your actual business database or data sources.
