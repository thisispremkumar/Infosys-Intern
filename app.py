import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

from supabase_client import supabase
from db import (
    fetch_sales, insert_sale, delete_sale, bulk_insert_sales, delete_all_sales,
    fetch_expenses, insert_expense, delete_expense, bulk_insert_expenses, delete_all_expenses,
    fetch_inventory, insert_inventory_item, delete_inventory_item, bulk_insert_inventory, delete_all_inventory,
)

# Page configuration
st.set_page_config(
    page_title="Small Business Sales & Profit Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    [data-testid="stMetricLabel"] { color: #31333F !important; }
    [data-testid="stMetricLabel"] label, [data-testid="stMetricLabel"] p { color: #31333F !important; }
    [data-testid="stMetricValue"] { color: #0e1117 !important; }
    [data-testid="stMetricValue"] div { color: #0e1117 !important; }
    [data-testid="stMetricDelta"] { color: #31333F !important; }
    .stMarkdown, .stMarkdown p, .stMarkdown span { color: #31333F !important; }
    h1, h2, h3, h4, h5, h6 { color: #1f77b4 !important; }
    [data-testid="stSidebar"] .stMarkdown p { color: #31333F !important; }
    .login-container {
        max-width: 450px;
        margin: auto;
        padding: 2rem;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #145a8a; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=['id', 'Date', 'Item', 'Category', 'Quantity', 'Unit Price', 'Total', 'Region'])
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['id', 'Date', 'Category', 'Amount', 'Description', 'Region'])
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['id', 'Item', 'Stock', 'Unit Cost'])

EXPENSE_CATEGORIES = ["Rent", "Utilities", "Supplies", "Salaries", "Marketing", "Transport", "Maintenance", "Other"]
SALES_CATEGORIES = ["Electronics", "Clothing", "Food", "Books", "Home", "Services", "Other"]
REGIONS = ["North", "South", "East", "West"]


# ============================================================
# AUTHENTICATION PAGES
# ============================================================
def auth_page():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("📊 Small Business Sales & Profit Analyzer")
        st.markdown("---")

        # Toggle between Login and Register
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            login_form()

        with tab2:
            register_form()


def login_form():
    st.markdown("### Welcome Back!")
    st.markdown("Please login to continue")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email", key="login_email")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
                return
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                user = res.user
                st.session_state.logged_in = True
                st.session_state.user_id = user.id
                st.session_state.user_email = user.email
                st.session_state.user_name = user.user_metadata.get("name", user.email)
                # Load user data from Supabase
                st.session_state.sales = fetch_sales(user.id)
                st.session_state.expenses = fetch_expenses(user.id)
                st.session_state.inventory = fetch_inventory(user.id)
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")


def register_form():
    st.markdown("### Create an Account")
    st.markdown("Register to start tracking your business")

    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name", placeholder="Enter your full name", key="reg_name")
            new_email = st.text_input("Email", placeholder="Enter your email", key="reg_email")
        with col2:
            new_password = st.text_input("Password", type="password", placeholder="Choose a password", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="reg_confirm")

        submitted = st.form_submit_button("Register", use_container_width=True)

        if submitted:
            if not new_name or not new_email or not new_password:
                st.error("All fields are required.")
                return
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return
            if len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
                return

            try:
                supabase.auth.sign_up({
                    "email": new_email,
                    "password": new_password,
                    "options": {"data": {"name": new_name}}
                })
                st.success(f"Account created successfully! You can now login with **{new_email}**.")
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("## Navigation")

        page = st.radio(
            "Go to",
            ["Dashboard", "Sales Entry", "Expenses", "Inventory", "Upload Bulk", "Predictions", "Logout"],
            label_visibility="collapsed"
        )

        if page == "Logout":
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
            st.session_state.logged_in = False
            st.session_state.user_id = ""
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.session_state.sales = pd.DataFrame(columns=['id', 'Date', 'Item', 'Category', 'Quantity', 'Unit Price', 'Total', 'Region'])
            st.session_state.expenses = pd.DataFrame(columns=['id', 'Date', 'Category', 'Amount', 'Description', 'Region'])
            st.session_state.inventory = pd.DataFrame(columns=['id', 'Item', 'Stock', 'Unit Cost'])
            st.rerun()

        return page


# ============================================================
# DASHBOARD
# ============================================================
def dashboard_section():
    st.title("📊 Dashboard")

    sales_df = st.session_state.sales.copy()
    expenses_df = st.session_state.expenses.copy()
    inventory_df = st.session_state.inventory.copy()

    has_sales = not sales_df.empty
    has_expenses = not expenses_df.empty

    if not has_sales and not has_expenses:
        st.info("No data yet. Use **Sales Entry**, **Expenses**, **Inventory**, or **Upload Bulk** to add data, then come back here.")

        # Show sample dashboard
        st.markdown("---")
        st.markdown("### Sample Dashboard Preview")
        _show_sample_dashboard()
        return

    # KPI Metrics
    total_sales = sales_df['Total'].sum() if has_sales else 0
    total_expenses = expenses_df['Amount'].sum() if has_expenses else 0
    net_profit = total_sales - total_expenses
    profit_margin = (net_profit / total_sales * 100) if total_sales > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales", f"${total_sales:,.2f}")
    with col2:
        st.metric("Total Expenses", f"${total_expenses:,.2f}")
    with col3:
        st.metric("Net Profit", f"${net_profit:,.2f}")
    with col4:
        st.metric("Profit Margin", f"{profit_margin:.1f}%")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        if has_sales:
            st.markdown("### Sales Trend")
            sales_df['Date'] = pd.to_datetime(sales_df['Date'])
            daily_sales = sales_df.groupby('Date')['Total'].sum().reset_index()
            fig = px.line(daily_sales, x='Date', y='Total', markers=True)
            fig.update_layout(xaxis_title="Date", yaxis_title="Sales ($)", height=350,
                              paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#31333F'))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if has_expenses:
            st.markdown("### Expenses by Category")
            cat_exp = expenses_df.groupby('Category')['Amount'].sum().reset_index()
            fig = px.pie(cat_exp, values='Amount', names='Category', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=350, paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#31333F'))
            st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if has_sales:
            st.markdown("### Sales by Category")
            cat_sales = sales_df.groupby('Category')['Total'].sum().reset_index()
            fig = px.bar(cat_sales, x='Category', y='Total', color='Category',
                         color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(showlegend=False, height=350,
                              paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#31333F'))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Profit over time
        if has_sales:
            st.markdown("### Revenue vs Expenses")
            sales_df['Date'] = pd.to_datetime(sales_df['Date'])
            daily_sales_sum = sales_df.groupby('Date')['Total'].sum().reset_index().rename(columns={'Total': 'Sales'})

            if has_expenses:
                expenses_df['Date'] = pd.to_datetime(expenses_df['Date'])
                daily_exp_sum = expenses_df.groupby('Date')['Amount'].sum().reset_index().rename(columns={'Amount': 'Expenses'})
                combined = pd.merge(daily_sales_sum, daily_exp_sum, on='Date', how='outer').fillna(0).sort_values('Date')
            else:
                combined = daily_sales_sum.copy()
                combined['Expenses'] = 0

            combined['Profit'] = combined['Sales'] - combined['Expenses']

            fig = go.Figure()
            fig.add_trace(go.Bar(x=combined['Date'], y=combined['Sales'], name='Sales', marker_color='#2ca02c'))
            fig.add_trace(go.Bar(x=combined['Date'], y=combined['Expenses'], name='Expenses', marker_color='#d62728'))
            fig.add_trace(go.Scatter(x=combined['Date'], y=combined['Profit'], name='Profit',
                                     line=dict(color='#1f77b4', width=2), mode='lines+markers'))
            fig.update_layout(barmode='group', height=350,
                              paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#31333F'))
            st.plotly_chart(fig, use_container_width=True)

    # Inventory summary
    if not inventory_df.empty:
        st.markdown("---")
        st.markdown("### Inventory Summary")
        inventory_df['Total Value'] = inventory_df['Stock'] * inventory_df['Unit Cost']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", len(inventory_df))
        with col2:
            st.metric("Total Stock Units", int(inventory_df['Stock'].sum()))
        with col3:
            st.metric("Inventory Value", f"${inventory_df['Total Value'].sum():,.2f}")

    # Download report
    st.markdown("---")
    if has_sales or has_expenses:
        report_data = {
            'Metric': ['Total Sales', 'Total Expenses', 'Net Profit', 'Profit Margin'],
            'Value': [f"${total_sales:,.2f}", f"${total_expenses:,.2f}", f"${net_profit:,.2f}", f"{profit_margin:.1f}%"]
        }
        report_df = pd.DataFrame(report_data)
        csv = report_df.to_csv(index=False)
        st.download_button("Download Report (CSV)", data=csv,
                           file_name=f"report_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")


def _show_sample_dashboard():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    sample_sales = np.random.randint(500, 5000, size=30).astype(float)
    sample_expenses = np.random.randint(200, 2000, size=30).astype(float)
    sample_profit = sample_sales - sample_expenses

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales", f"${sample_sales.sum():,.2f}")
    with col2:
        st.metric("Total Expenses", f"${sample_expenses.sum():,.2f}")
    with col3:
        st.metric("Net Profit", f"${sample_profit.sum():,.2f}")
    with col4:
        margin = sample_profit.sum() / sample_sales.sum() * 100
        st.metric("Profit Margin", f"{margin:.1f}%")

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=sample_sales, mode='lines+markers', name='Sales',
                                 line=dict(color='#1f77b4', width=2)))
        fig.update_layout(title="Sales Trend (Sample)", height=350,
                          paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#31333F'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home']
        values = np.random.randint(1000, 10000, size=5)
        fig = px.pie(names=categories, values=values, hole=0.4, title="Sales by Category (Sample)",
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=350, paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#31333F'))
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# SALES ENTRY
# ============================================================
def sales_entry_section():
    st.title("Sales Entry")

    with st.form("sales_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sale_date = st.date_input("Date", value=datetime.now().date())
            item_name = st.text_input("Item Name", placeholder="e.g., Laptop, T-Shirt")
            category = st.selectbox("Category", SALES_CATEGORIES)
        with col2:
            quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
            unit_price = st.number_input("Unit Price", min_value=0.01, step=0.01, format="%.2f")
            region = st.selectbox("Region", REGIONS)

        submitted = st.form_submit_button("Add Sale", use_container_width=True)

        if submitted:
            if not item_name:
                st.error("Item name is required.")
            else:
                total = quantity * unit_price
                sale_dict = {
                    'Date': str(sale_date),
                    'Item': item_name,
                    'Category': category,
                    'Quantity': quantity,
                    'Unit Price': float(unit_price),
                    'Total': float(total),
                    'Region': region
                }
                try:
                    insert_sale(st.session_state.user_id, sale_dict)
                    st.session_state.sales = fetch_sales(st.session_state.user_id)
                    st.success(f"Sale added: {item_name} x{quantity} = ${total:,.2f}")
                except Exception as e:
                    st.error(f"Failed to add sale: {str(e)}")

    # Display sales table
    st.markdown("---")
    if not st.session_state.sales.empty:
        st.markdown("### Sales Records")

        display_df = st.session_state.sales.drop(columns=['id'], errors='ignore').copy()
        display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, use_container_width=True)

        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue", f"${st.session_state.sales['Total'].sum():,.2f}")
        with col2:
            st.metric("Total Items Sold", int(st.session_state.sales['Quantity'].sum()))
        with col3:
            st.metric("Number of Sales", len(st.session_state.sales))

        # Delete
        st.markdown("---")
        sales_df = st.session_state.sales
        sale_labels = [f"{i} - {r['Item']} ({r['Date']})" for i, r in sales_df.iterrows()]
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_sale = st.selectbox("Select sale to delete", options=range(len(sales_df)),
                                          format_func=lambda i: sale_labels[i], key="del_sale_sel")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Delete Sale", key="del_sale_btn"):
                try:
                    sale_id = sales_df.iloc[selected_sale]['id']
                    delete_sale(sale_id)
                    st.session_state.sales = fetch_sales(st.session_state.user_id)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {str(e)}")
    else:
        st.info("No sales recorded yet. Add your first sale above.")


# ============================================================
# EXPENSES
# ============================================================
def expenses_section():
    st.title("Expenses")

    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            exp_date = st.date_input("Date", value=datetime.now().date())
            category = st.selectbox("Category", EXPENSE_CATEGORIES)
        with col2:
            amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
            region = st.selectbox("Region", REGIONS)

        description = st.text_input("Description", placeholder="Brief description of the expense")

        submitted = st.form_submit_button("Add Expense", use_container_width=True)

        if submitted:
            expense_dict = {
                'Date': str(exp_date),
                'Category': category,
                'Amount': float(amount),
                'Description': description,
                'Region': region
            }
            try:
                insert_expense(st.session_state.user_id, expense_dict)
                st.session_state.expenses = fetch_expenses(st.session_state.user_id)
                st.success(f"Expense added: {category} - ${amount:,.2f}")
            except Exception as e:
                st.error(f"Failed to add expense: {str(e)}")

    # Display expenses table
    st.markdown("---")
    if not st.session_state.expenses.empty:
        st.markdown("### Expense Records")

        display_df = st.session_state.expenses.drop(columns=['id'], errors='ignore').copy()
        display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, use_container_width=True)

        # Summary
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Expenses", f"${st.session_state.expenses['Amount'].sum():,.2f}")
        with col2:
            st.metric("Number of Expenses", len(st.session_state.expenses))

        # Delete
        st.markdown("---")
        exp_df = st.session_state.expenses
        exp_labels = [f"{i} - {r['Category']} ${r['Amount']:.2f} ({r['Date']})" for i, r in exp_df.iterrows()]
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_exp = st.selectbox("Select expense to delete", options=range(len(exp_df)),
                                         format_func=lambda i: exp_labels[i], key="del_exp_sel")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Delete Expense", key="del_exp_btn"):
                try:
                    exp_id = exp_df.iloc[selected_exp]['id']
                    delete_expense(exp_id)
                    st.session_state.expenses = fetch_expenses(st.session_state.user_id)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {str(e)}")
    else:
        st.info("No expenses recorded yet. Add your first expense above.")


# ============================================================
# INVENTORY MANAGEMENT
# ============================================================
def inventory_section():
    st.title("Inventory Management")

    # Add inventory item
    item_name = st.text_input("Item Name", placeholder="e.g., clothes, electronics", key="inv_item")
    stock = st.number_input("Stock", min_value=0, step=1, value=0, key="inv_stock")
    unit_cost = st.number_input("Unit Cost", min_value=0.00, step=0.01, format="%.2f", key="inv_cost")

    if st.button("Add Inventory", key="add_inv_btn"):
        if not item_name:
            st.error("Item name is required.")
        else:
            item_dict = {
                'Item': item_name,
                'Stock': int(stock),
                'Unit Cost': float(unit_cost)
            }
            try:
                insert_inventory_item(st.session_state.user_id, item_dict)
                st.session_state.inventory = fetch_inventory(st.session_state.user_id)
                st.success(f"Added: {item_name} (Stock: {stock}, Unit Cost: ${unit_cost:.2f})")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to add item: {str(e)}")

    # Display inventory table
    st.markdown("---")
    if not st.session_state.inventory.empty:
        display_df = st.session_state.inventory.drop(columns=['id'], errors='ignore')
        st.dataframe(display_df, use_container_width=True)

        # Low stock alerts
        low_stock = st.session_state.inventory[st.session_state.inventory['Stock'] < 10]
        if not low_stock.empty:
            st.warning(f"Low stock alert: {', '.join(low_stock['Item'].tolist())} (< 10 units)")

        # Total inventory value
        inv = st.session_state.inventory.copy()
        inv['Total Value'] = inv['Stock'] * inv['Unit Cost']
        st.metric("Total Inventory Value", f"${inv['Total Value'].sum():,.2f}")

        # Delete inventory item
        st.markdown("---")
        inv_df = st.session_state.inventory
        inv_labels = [f"{i} - {r['Item']} (Stock: {r['Stock']})" for i, r in inv_df.iterrows()]
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_inv = st.selectbox("Select item to delete", options=range(len(inv_df)),
                                         format_func=lambda i: inv_labels[i], key="del_inv_sel")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Delete Item", key="del_inv_btn"):
                try:
                    inv_id = inv_df.iloc[selected_inv]['id']
                    delete_inventory_item(inv_id)
                    st.session_state.inventory = fetch_inventory(st.session_state.user_id)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {str(e)}")
    else:
        st.info("No inventory items yet. Add your first item above.")


# ============================================================
# UPLOAD BULK CSV & VISUALIZATIONS
# ============================================================
def detect_column_types(df):
    """Auto-detect date, numeric, and categorical columns."""
    date_cols = []
    numeric_cols = []
    categorical_cols = []

    for col in df.columns:
        if df[col].dtype in ['datetime64[ns]', 'datetime64']:
            date_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        else:
            # Try parsing as date
            try:
                parsed = pd.to_datetime(df[col], errors='coerce')
                if parsed.notna().sum() > len(df) * 0.5:
                    date_cols.append(col)
                else:
                    nunique = df[col].nunique()
                    if nunique <= 50 and nunique < len(df) * 0.5:
                        categorical_cols.append(col)
            except Exception:
                nunique = df[col].nunique()
                if nunique <= 50 and nunique < len(df) * 0.5:
                    categorical_cols.append(col)

    return date_cols, numeric_cols, categorical_cols


def render_upload_visualizations(df):
    """Generate automatic visualizations based on uploaded CSV columns."""
    date_cols, numeric_cols, categorical_cols = detect_column_types(df)

    # Convert detected date columns
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    st.markdown("---")
    st.markdown("## Dataset Visualizations")

    # --- KPI Metrics ---
    if numeric_cols:
        st.markdown("### Key Metrics")
        # Pick most meaningful numeric columns for KPIs
        kpi_cols = numeric_cols[:6]
        cols = st.columns(len(kpi_cols))
        for i, col_name in enumerate(kpi_cols):
            with cols[i]:
                total = df[col_name].sum()
                avg = df[col_name].mean()
                if total > 1_000_000:
                    display_val = f"${total:,.0f}" if any(
                        k in col_name.lower() for k in ['sales', 'profit', 'revenue', 'price', 'cost', 'amount']
                    ) else f"{total:,.0f}"
                else:
                    display_val = f"${total:,.2f}" if any(
                        k in col_name.lower() for k in ['sales', 'profit', 'revenue', 'price', 'cost', 'amount']
                    ) else f"{total:,.2f}"
                st.metric(col_name, display_val, f"Avg: {avg:,.2f}")

    # --- Profit Margin KPI (special case) ---
    sales_col = next((c for c in df.columns if c.lower() in ['sales', 'revenue', 'total sales', 'total']), None)
    profit_col = next((c for c in df.columns if c.lower() in ['profit', 'net profit']), None)
    if sales_col and profit_col:
        total_sales = df[sales_col].sum()
        total_profit = df[profit_col].sum()
        margin = (total_profit / total_sales * 100) if total_sales != 0 else 0
        st.markdown("### Profitability Overview")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Sales", f"${total_sales:,.2f}")
        m2.metric("Total Profit", f"${total_profit:,.2f}")
        m3.metric("Profit Margin", f"{margin:.1f}%")
        m4.metric("Total Records", f"{len(df):,}")

    # --- Time Series Charts ---
    if date_cols and numeric_cols:
        st.markdown("### Trends Over Time")
        date_col = date_cols[0]
        df_sorted = df.sort_values(date_col).dropna(subset=[date_col])

        # Pick up to 3 numeric columns for trend
        trend_cols = numeric_cols[:3]

        # Monthly aggregation
        df_sorted['_month'] = df_sorted[date_col].dt.to_period('M').astype(str)
        monthly = df_sorted.groupby('_month')[trend_cols].sum().reset_index()

        fig_trend = go.Figure()
        colors = ['#636EFA', '#EF553B', '#00CC96']
        for idx, tc in enumerate(trend_cols):
            fig_trend.add_trace(go.Scatter(
                x=monthly['_month'], y=monthly[tc],
                mode='lines+markers', name=tc,
                line=dict(color=colors[idx % len(colors)], width=2)
            ))
        fig_trend.update_layout(
            title=f"Monthly Trends ({', '.join(trend_cols)})",
            xaxis_title="Month", yaxis_title="Value",
            template="plotly_white", hovermode="x unified"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        df_sorted.drop(columns=['_month'], inplace=True)

    # --- Category Breakdown Charts ---
    if categorical_cols and numeric_cols:
        st.markdown("### Category Analysis")

        for cat_col in categorical_cols[:2]:
            value_cols = numeric_cols[:2]
            cat_agg = df.groupby(cat_col)[value_cols].sum().reset_index()

            col1, col2 = st.columns(2)

            with col1:
                fig_bar = px.bar(
                    cat_agg, x=cat_col, y=value_cols[0],
                    color=cat_col, title=f"{value_cols[0]} by {cat_col}",
                    template="plotly_white"
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                fig_pie = px.pie(
                    cat_agg, values=value_cols[0], names=cat_col,
                    title=f"{value_cols[0]} Distribution by {cat_col}",
                    template="plotly_white", hole=0.4
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # Second numeric column bar if available
            if len(value_cols) > 1:
                c1, c2 = st.columns(2)
                with c1:
                    fig_bar2 = px.bar(
                        cat_agg, x=cat_col, y=value_cols[1],
                        color=cat_col, title=f"{value_cols[1]} by {cat_col}",
                        template="plotly_white"
                    )
                    fig_bar2.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar2, use_container_width=True)
                with c2:
                    fig_pie2 = px.pie(
                        cat_agg, values=value_cols[1], names=cat_col,
                        title=f"{value_cols[1]} Distribution by {cat_col}",
                        template="plotly_white", hole=0.4
                    )
                    st.plotly_chart(fig_pie2, use_container_width=True)

    # --- Top Items Analysis ---
    # Find a "name/item/product" column
    name_col = next((c for c in df.columns if any(
        k in c.lower() for k in ['product', 'item', 'name']
    )), None)
    if name_col and numeric_cols:
        st.markdown("### Top Items Analysis")
        value_col_for_top = numeric_cols[0]
        top_n = df.groupby(name_col)[value_col_for_top].sum().reset_index()
        top_n = top_n.sort_values(value_col_for_top, ascending=False).head(10)

        fig_top = px.bar(
            top_n, x=value_col_for_top, y=name_col,
            orientation='h', title=f"Top 10 {name_col} by {value_col_for_top}",
            template="plotly_white", color=value_col_for_top,
            color_continuous_scale="Blues"
        )
        fig_top.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_top, use_container_width=True)

    # --- Profit vs Sales Scatter (if both exist) ---
    if sales_col and profit_col:
        st.markdown("### Profit vs Sales Analysis")
        scatter_color = categorical_cols[0] if categorical_cols else None
        fig_scatter = px.scatter(
            df, x=sales_col, y=profit_col, color=scatter_color,
            title=f"{profit_col} vs {sales_col}",
            template="plotly_white", opacity=0.6
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Correlation Heatmap ---
    if len(numeric_cols) >= 2:
        st.markdown("### Correlation Matrix")
        corr = df[numeric_cols].corr()
        fig_corr = px.imshow(
            corr, text_auto=".2f", color_continuous_scale="RdBu_r",
            title="Numeric Columns Correlation",
            template="plotly_white"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # --- Distribution of Numeric Columns ---
    if numeric_cols:
        st.markdown("### Data Distributions")
        dist_cols = st.columns(min(len(numeric_cols), 3))
        for i, nc in enumerate(numeric_cols[:3]):
            with dist_cols[i]:
                fig_hist = px.histogram(
                    df, x=nc, nbins=30, title=f"Distribution of {nc}",
                    template="plotly_white", color_discrete_sequence=['#636EFA']
                )
                st.plotly_chart(fig_hist, use_container_width=True)


def upload_bulk_section():
    st.title("Upload & Analyze Data")
    st.markdown("Upload a CSV or Excel file to instantly visualize your data and optionally import it into the app.")
    st.markdown("---")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                raw_df = pd.read_csv(uploaded_file)
            else:
                raw_df = pd.read_excel(uploaded_file)

            # --- Data Preview ---
            st.markdown("### Data Preview")
            st.dataframe(raw_df.head(20), use_container_width=True)
            st.markdown(f"**Rows:** {len(raw_df)} | **Columns:** {', '.join(raw_df.columns.tolist())}")

            # --- Auto Visualizations ---
            render_upload_visualizations(raw_df.copy())

            # --- Import Section ---
            st.markdown("---")
            st.markdown("## Import Into App")
            st.markdown("Optionally import this data into one of the app's data stores.")

            data_type = st.selectbox("Import as:", ["Sales", "Expenses", "Inventory", "Don't import"])

            if data_type != "Don't import":
                import_mode = st.radio("Import Mode",
                                       ["Append to existing data", "Replace all existing data"],
                                       horizontal=True)

                if st.button("Import Data", use_container_width=True, type="primary"):
                    user_id = st.session_state.user_id
                    try:
                        if data_type == "Sales":
                            required = ['Date', 'Item', 'Category', 'Quantity', 'Unit Price', 'Total', 'Region']
                            missing = [c for c in required if c not in raw_df.columns]
                            if missing:
                                st.error(f"Missing columns: {', '.join(missing)}")
                                return
                            raw_df['Date'] = pd.to_datetime(raw_df['Date'], errors='coerce')
                            raw_df = raw_df.dropna(subset=['Date'])
                            raw_df['Date'] = raw_df['Date'].dt.strftime('%Y-%m-%d')
                            if import_mode == "Replace all existing data":
                                delete_all_sales(user_id)
                            bulk_insert_sales(user_id, raw_df[required])
                            st.session_state.sales = fetch_sales(user_id)

                        elif data_type == "Expenses":
                            required = ['Date', 'Category', 'Amount', 'Description', 'Region']
                            missing = [c for c in required if c not in raw_df.columns]
                            if missing:
                                st.error(f"Missing columns: {', '.join(missing)}")
                                return
                            raw_df['Date'] = pd.to_datetime(raw_df['Date'], errors='coerce')
                            raw_df = raw_df.dropna(subset=['Date'])
                            raw_df['Date'] = raw_df['Date'].dt.strftime('%Y-%m-%d')
                            if import_mode == "Replace all existing data":
                                delete_all_expenses(user_id)
                            bulk_insert_expenses(user_id, raw_df[required])
                            st.session_state.expenses = fetch_expenses(user_id)

                        else:  # Inventory
                            required = ['Item', 'Stock', 'Unit Cost']
                            missing = [c for c in required if c not in raw_df.columns]
                            if missing:
                                st.error(f"Missing columns: {', '.join(missing)}")
                                return
                            if import_mode == "Replace all existing data":
                                delete_all_inventory(user_id)
                            bulk_insert_inventory(user_id, raw_df[required])
                            st.session_state.inventory = fetch_inventory(user_id)

                        st.success(f"Successfully imported {len(raw_df)} {data_type.lower()} records!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Import failed: {str(e)}")

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    else:
        st.info("Upload a CSV file above to see instant visualizations and analysis.")


# ============================================================
# PREDICTIONS / FORECASTING
# ============================================================
def predictions_section():
    st.title("🔮 Sales & Profit Predictions")
    st.markdown("Forecast future sales and profit using historical data trends.")
    
    sales_df = st.session_state.sales.copy()
    
    # Check if user has sales data
    if sales_df.empty:
        st.warning("No sales data available. Please add sales records or upload data first.")
        st.info("Go to **Sales Entry** or **Upload Bulk** to add data, then return here for predictions.")
        
        # Show sample prediction demo
        st.markdown("---")
        st.markdown("### Sample Prediction Preview")
        _show_sample_predictions()
        return
    
    # Prepare data
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    daily_data = sales_df.groupby('Date').agg({'Total': 'sum'}).reset_index()
    daily_data = daily_data.sort_values('Date')
    
    if len(daily_data) < 3:
        st.warning("Need at least 3 data points for prediction. Please add more sales records.")
        return
    
    # Prediction settings
    st.markdown("---")
    st.markdown("### Prediction Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        forecast_periods = st.slider("Days to Forecast", min_value=7, max_value=90, value=30, step=7)
    with col2:
        confidence_level = st.selectbox("Confidence Interval", ["80%", "90%", "95%"], index=1)
    
    confidence_map = {"80%": 1.28, "90%": 1.645, "95%": 1.96}
    z_score = confidence_map[confidence_level]
    
    # Perform predictions
    st.markdown("---")
    st.markdown("### Sales Forecast")
    
    # Prepare numeric X and y
    daily_data['DayNum'] = (daily_data['Date'] - daily_data['Date'].min()).dt.days
    X = daily_data['DayNum'].values
    y = daily_data['Total'].values
    
    # Fit polynomial regression (degree 2 for trend)
    degree = 2 if len(X) > 10 else 1
    coeffs = np.polyfit(X, y, degree)
    poly = np.poly1d(coeffs)
    
    # Calculate residuals for confidence interval
    y_pred_train = poly(X)
    residuals = y - y_pred_train
    std_error = np.std(residuals)
    
    # Generate future dates
    last_date = daily_data['Date'].max()
    last_day_num = daily_data['DayNum'].max()
    future_days = np.arange(last_day_num + 1, last_day_num + forecast_periods + 1)
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_periods, freq='D')
    
    # Predict future values
    future_pred = poly(future_days)
    future_pred = np.maximum(future_pred, 0)  # Ensure non-negative
    
    upper_bound = future_pred + z_score * std_error
    lower_bound = np.maximum(future_pred - z_score * std_error, 0)
    
    # Create prediction dataframe
    pred_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted Sales': future_pred,
        'Lower Bound': lower_bound,
        'Upper Bound': upper_bound
    })
    
    # Plot historical and predicted
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=daily_data['Date'], y=daily_data['Total'],
        mode='lines+markers', name='Historical Sales',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Fitted trend line on historical data
    fig.add_trace(go.Scatter(
        x=daily_data['Date'], y=y_pred_train,
        mode='lines', name='Trend Line',
        line=dict(color='#ff7f0e', width=2, dash='dash')
    ))
    
    # Predicted values
    fig.add_trace(go.Scatter(
        x=pred_df['Date'], y=pred_df['Predicted Sales'],
        mode='lines+markers', name='Predicted Sales',
        line=dict(color='#2ca02c', width=2)
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=pd.concat([pred_df['Date'], pred_df['Date'][::-1]]),
        y=pd.concat([pred_df['Upper Bound'], pred_df['Lower Bound'][::-1]]),
        fill='toself', fillcolor='rgba(44, 160, 44, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip', showlegend=True,
        name=f'{confidence_level} Confidence Interval'
    ))
    
    fig.update_layout(
        title=f"Sales Forecast for Next {forecast_periods} Days",
        xaxis_title="Date", yaxis_title="Sales ($)",
        height=450, hovermode='x unified',
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(color='#31333F')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast Summary KPIs
    st.markdown("### Forecast Summary")
    
    total_predicted_sales = pred_df['Predicted Sales'].sum()
    avg_daily_predicted = pred_df['Predicted Sales'].mean()
    historical_avg = daily_data['Total'].mean()
    growth_rate = ((avg_daily_predicted - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Predicted Sales", f"${total_predicted_sales:,.2f}")
    with col2:
        st.metric("Avg Daily Forecast", f"${avg_daily_predicted:,.2f}")
    with col3:
        st.metric("Historical Avg", f"${historical_avg:,.2f}")
    with col4:
        delta_color = "normal" if growth_rate >= 0 else "inverse"
        st.metric("Trend", f"{growth_rate:+.1f}%", delta=f"{growth_rate:+.1f}%", delta_color=delta_color)
    
    # Profit Projection (if expenses exist)
    expenses_df = st.session_state.expenses.copy()
    
    st.markdown("---")
    st.markdown("### Profit Projection")
    
    if not expenses_df.empty:
        expenses_df['Date'] = pd.to_datetime(expenses_df['Date'])
        daily_expenses = expenses_df.groupby('Date')['Amount'].sum().mean()
    else:
        st.info("No expense data. Enter an estimated daily expense for profit projection.")
        daily_expenses = st.number_input("Estimated Daily Expenses ($)", min_value=0.0, value=100.0, step=10.0)
    
    projected_expenses = daily_expenses * forecast_periods
    projected_profit = total_predicted_sales - projected_expenses
    profit_margin = (projected_profit / total_predicted_sales * 100) if total_predicted_sales > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Projected Revenue", f"${total_predicted_sales:,.2f}")
    with col2:
        st.metric("Projected Expenses", f"${projected_expenses:,.2f}")
    with col3:
        profit_color = "#2ca02c" if projected_profit >= 0 else "#d62728"
        st.metric("Projected Profit", f"${projected_profit:,.2f}")
    
    # Profit visualization
    fig_profit = go.Figure()
    
    # Create profit projection over time
    cumulative_sales = pred_df['Predicted Sales'].cumsum()
    cumulative_expenses = np.arange(1, forecast_periods + 1) * daily_expenses
    cumulative_profit = cumulative_sales - cumulative_expenses
    
    fig_profit.add_trace(go.Scatter(
        x=pred_df['Date'], y=cumulative_sales,
        mode='lines', name='Cumulative Revenue',
        line=dict(color='#2ca02c', width=2)
    ))
    fig_profit.add_trace(go.Scatter(
        x=pred_df['Date'], y=cumulative_expenses,
        mode='lines', name='Cumulative Expenses',
        line=dict(color='#d62728', width=2)
    ))
    fig_profit.add_trace(go.Scatter(
        x=pred_df['Date'], y=cumulative_profit,
        mode='lines', name='Cumulative Profit',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig_profit.update_layout(
        title="Projected Cumulative Revenue, Expenses & Profit",
        xaxis_title="Date", yaxis_title="Amount ($)",
        height=400, hovermode='x unified',
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(color='#31333F')
    )
    st.plotly_chart(fig_profit, use_container_width=True)
    
    # Download predictions
    st.markdown("---")
    pred_export = pred_df.copy()
    pred_export['Projected Daily Expenses'] = daily_expenses
    pred_export['Projected Daily Profit'] = pred_export['Predicted Sales'] - daily_expenses
    pred_export['Date'] = pred_export['Date'].dt.strftime('%Y-%m-%d')
    csv = pred_export.to_csv(index=False)
    st.download_button(
        "Download Forecast (CSV)", data=csv,
        file_name=f"sales_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


def _show_sample_predictions():
    """Show sample predictions when user has no data."""
    np.random.seed(42)
    
    # Generate sample historical data
    dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
    base_sales = 1000
    trend = np.linspace(0, 500, 60)
    noise = np.random.normal(0, 100, 60)
    sales = base_sales + trend + noise
    sales = np.maximum(sales, 100)
    
    sample_df = pd.DataFrame({'Date': dates, 'Sales': sales})
    
    # Generate future predictions
    future_dates = pd.date_range(start=dates[-1] + pd.Timedelta(days=1), periods=30, freq='D')
    future_trend = np.linspace(trend[-1], trend[-1] + 250, 30)
    future_sales = base_sales + future_trend
    
    pred_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted': future_sales,
        'Upper': future_sales + 150,
        'Lower': np.maximum(future_sales - 150, 0)
    })
    
    # Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sample_df['Date'], y=sample_df['Sales'],
                             mode='lines+markers', name='Historical (Sample)',
                             line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=pred_df['Date'], y=pred_df['Predicted'],
                             mode='lines+markers', name='Forecast (Sample)',
                             line=dict(color='#2ca02c', width=2)))
    fig.add_trace(go.Scatter(
        x=pd.concat([pred_df['Date'], pred_df['Date'][::-1]]),
        y=pd.concat([pred_df['Upper'], pred_df['Lower'][::-1]]),
        fill='toself', fillcolor='rgba(44, 160, 44, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip', showlegend=True, name='Confidence Interval'
    ))
    fig.update_layout(title="Sample Sales Forecast", height=400,
                      paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#31333F'))
    st.plotly_chart(fig, use_container_width=True)
    
    # Sample KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Predicted 30-Day Sales", f"${pred_df['Predicted'].sum():,.2f}")
    with col2:
        st.metric("Avg Daily Forecast", f"${pred_df['Predicted'].mean():,.2f}")
    with col3:
        st.metric("Growth Trend", "+12.5%")


# ============================================================
# MAIN APP
# ============================================================
def main():
    if not st.session_state.logged_in:
        auth_page()
    else:
        page = render_sidebar()

        if page == "Dashboard":
            dashboard_section()
        elif page == "Sales Entry":
            sales_entry_section()
        elif page == "Expenses":
            expenses_section()
        elif page == "Inventory":
            inventory_section()
        elif page == "Upload Bulk":
            upload_bulk_section()
        elif page == "Predictions":
            predictions_section()


if __name__ == "__main__":
    main()
