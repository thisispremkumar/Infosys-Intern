"""
PDF Report Generator for Small Business Sales & Profit Analyzer.
Generates a formatted PDF report with KPIs, tables, and summary.
"""

import io
from datetime import datetime
from fpdf import FPDF
import pandas as pd


class BusinessReport(FPDF):
    """Custom PDF class with header/footer branding."""

    def __init__(self, business_name="Small Business Sales & Profit Analyzer"):
        super().__init__()
        self.business_name = business_name

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.business_name, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, f"Report generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    # ----- helpers -----
    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(30, 119, 180)
        self.set_text_color(255, 255, 255)
        self.cell(0, 9, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def kpi_row(self, metrics: dict):
        """Print a row of KPI boxes. metrics = {label: value_str}."""
        col_w = (self.w - 20) / len(metrics)
        self.set_font("Helvetica", "", 9)
        for label, value in metrics.items():
            x = self.get_x()
            y = self.get_y()
            self.set_fill_color(240, 242, 246)
            self.rect(x, y, col_w - 2, 18, "F")
            self.set_xy(x, y + 2)
            self.set_font("Helvetica", "", 8)
            self.cell(col_w - 2, 5, label, align="C", new_x="LEFT", new_y="NEXT")
            self.set_x(x)
            self.set_font("Helvetica", "B", 11)
            self.cell(col_w - 2, 7, value, align="C")
            self.set_xy(x + col_w, y)
        self.ln(22)

    def add_table(self, df: pd.DataFrame, max_rows=50):
        """Render a DataFrame as a table in the PDF."""
        if df.empty:
            self.set_font("Helvetica", "I", 9)
            self.cell(0, 8, "No data available.", new_x="LMARGIN", new_y="NEXT")
            return

        display = df.head(max_rows).copy()
        cols = list(display.columns)
        col_w = (self.w - 20) / len(cols)

        # Header
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(30, 119, 180)
        self.set_text_color(255, 255, 255)
        for c in cols:
            self.cell(col_w, 7, str(c)[:18], border=1, fill=True, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)

        # Rows
        self.set_font("Helvetica", "", 7)
        for _, row in display.iterrows():
            if self.get_y() > 265:
                self.add_page()
                # Re-print header row on new page
                self.set_font("Helvetica", "B", 8)
                self.set_fill_color(30, 119, 180)
                self.set_text_color(255, 255, 255)
                for c in cols:
                    self.cell(col_w, 7, str(c)[:18], border=1, fill=True, align="C")
                self.ln()
                self.set_text_color(0, 0, 0)
                self.set_font("Helvetica", "", 7)
            for c in cols:
                val = str(row[c])[:22]
                self.cell(col_w, 6, val, border=1, align="C")
            self.ln()

        if len(df) > max_rows:
            self.set_font("Helvetica", "I", 8)
            self.cell(0, 6, f"... showing {max_rows} of {len(df)} rows", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)


def generate_report(sales_df: pd.DataFrame, expenses_df: pd.DataFrame,
                    inventory_df: pd.DataFrame, user_name: str = "") -> bytes:
    """Build a full business report and return PDF bytes."""

    pdf = BusinessReport()
    pdf.alias_nb_pages()
    pdf.add_page()

    if user_name:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Prepared for: {user_name}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    has_sales = not sales_df.empty
    has_expenses = not expenses_df.empty

    total_sales = sales_df["Total"].sum() if has_sales else 0
    total_expenses = expenses_df["Amount"].sum() if has_expenses else 0
    net_profit = total_sales - total_expenses
    margin = (net_profit / total_sales * 100) if total_sales else 0

    # ---- KPIs ----
    pdf.section_title("Key Performance Indicators")
    pdf.kpi_row({
        "Total Sales": f"${total_sales:,.2f}",
        "Total Expenses": f"${total_expenses:,.2f}",
        "Net Profit": f"${net_profit:,.2f}",
        "Profit Margin": f"{margin:.1f}%",
    })

    # ---- Sales ----
    pdf.section_title("Sales Records")
    if has_sales:
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"Total records: {len(sales_df)}  |  Total revenue: ${total_sales:,.2f}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        display_sales = sales_df.drop(columns=["id"], errors="ignore")
        pdf.add_table(display_sales)
    else:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 8, "No sales data.", new_x="LMARGIN", new_y="NEXT")

    # ---- Expenses ----
    pdf.section_title("Expense Records")
    if has_expenses:
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"Total records: {len(expenses_df)}  |  Total expenses: ${total_expenses:,.2f}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        display_exp = expenses_df.drop(columns=["id"], errors="ignore")
        pdf.add_table(display_exp)
    else:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 8, "No expense data.", new_x="LMARGIN", new_y="NEXT")

    # ---- Inventory ----
    pdf.section_title("Inventory Summary")
    if not inventory_df.empty:
        inv = inventory_df.copy()
        inv["Total Value"] = inv["Stock"] * inv["Unit Cost"]
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6,
                 f"Items: {len(inv)}  |  Total stock: {int(inv['Stock'].sum())}  |  "
                 f"Inventory value: ${inv['Total Value'].sum():,.2f}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        display_inv = inv.drop(columns=["id"], errors="ignore")
        pdf.add_table(display_inv)
    else:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 8, "No inventory data.", new_x="LMARGIN", new_y="NEXT")

    # ---- Summary ----
    pdf.section_title("Summary")
    pdf.set_font("Helvetica", "", 10)
    lines = [
        f"Reporting period: {sales_df['Date'].min()} to {sales_df['Date'].max()}" if has_sales else "No sales period",
        f"Total Revenue: ${total_sales:,.2f}",
        f"Total Expenses: ${total_expenses:,.2f}",
        f"Net Profit: ${net_profit:,.2f}  ({margin:.1f}% margin)",
    ]
    for line in lines:
        pdf.cell(0, 7, line, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
