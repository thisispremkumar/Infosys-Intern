# Quick Start Guide

## Installation

1. Open Command Prompt or PowerShell in this directory
2. Run: `pip install streamlit pandas plotly numpy`

## Running the Application

Run one of these commands:

```bash
# Option 1 (Recommended)
python -m streamlit run app.py

# Option 2 (If streamlit is in PATH)
streamlit run app.py
```

## Access the App

The app will open automatically in your browser at: http://localhost:8501

## Login Credentials

- Username: `admin` | Password: `admin123`
- Username: `demo` | Password: `demo123`
- Username: `user` | Password: `user123`

## Features

✅ Secure login page with session management
✅ Interactive dashboard with KPIs
✅ Sales and profit trend charts
✅ Category and region analysis
✅ Data filtering (time, category, region)
✅ Export to CSV
✅ Responsive design

## Troubleshooting

If you get "ModuleNotFoundError", run:
```bash
pip install -r requirements.txt
```

If streamlit command doesn't work, use:
```bash
python -m streamlit run app.py
```
