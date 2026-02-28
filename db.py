import pandas as pd
from supabase_client import supabase


# ============================================================
# Column mapping: DB snake_case <-> App PascalCase
# ============================================================
SALES_DB_TO_APP = {
    "id": "id",
    "date": "Date",
    "item": "Item",
    "category": "Category",
    "quantity": "Quantity",
    "unit_price": "Unit Price",
    "total": "Total",
    "region": "Region",
}

SALES_APP_TO_DB = {v: k for k, v in SALES_DB_TO_APP.items() if v != "id"}

EXPENSES_DB_TO_APP = {
    "id": "id",
    "date": "Date",
    "category": "Category",
    "amount": "Amount",
    "description": "Description",
    "region": "Region",
}

EXPENSES_APP_TO_DB = {v: k for k, v in EXPENSES_DB_TO_APP.items() if v != "id"}

INVENTORY_DB_TO_APP = {
    "id": "id",
    "item": "Item",
    "stock": "Stock",
    "unit_cost": "Unit Cost",
}

INVENTORY_APP_TO_DB = {v: k for k, v in INVENTORY_DB_TO_APP.items() if v != "id"}


def _rows_to_df(rows, col_map):
    """Convert Supabase rows to a DataFrame with app-facing column names."""
    if not rows:
        return pd.DataFrame(columns=list(col_map.values()))
    df = pd.DataFrame(rows)
    # Keep only mapped columns that exist
    keep = [k for k in col_map if k in df.columns]
    df = df[keep].rename(columns=col_map)
    return df


def _app_dict_to_db(app_dict, col_map):
    """Convert an app-facing dict to DB column names."""
    return {col_map[k]: v for k, v in app_dict.items() if k in col_map}


# ============================================================
# SALES
# ============================================================
def fetch_sales(user_id):
    res = supabase.table("sales").select("*").eq("user_id", user_id).order("date", desc=True).execute()
    return _rows_to_df(res.data, SALES_DB_TO_APP)


def insert_sale(user_id, sale_dict):
    row = _app_dict_to_db(sale_dict, SALES_APP_TO_DB)
    row["user_id"] = user_id
    supabase.table("sales").insert(row).execute()


def delete_sale(sale_id):
    supabase.table("sales").delete().eq("id", sale_id).execute()


def bulk_insert_sales(user_id, df):
    records = []
    for _, r in df.iterrows():
        row = _app_dict_to_db(r.to_dict(), SALES_APP_TO_DB)
        row["user_id"] = user_id
        records.append(row)
    if records:
        supabase.table("sales").insert(records).execute()


def delete_all_sales(user_id):
    supabase.table("sales").delete().eq("user_id", user_id).execute()


# ============================================================
# EXPENSES
# ============================================================
def fetch_expenses(user_id):
    res = supabase.table("expenses").select("*").eq("user_id", user_id).order("date", desc=True).execute()
    return _rows_to_df(res.data, EXPENSES_DB_TO_APP)


def insert_expense(user_id, expense_dict):
    row = _app_dict_to_db(expense_dict, EXPENSES_APP_TO_DB)
    row["user_id"] = user_id
    supabase.table("expenses").insert(row).execute()


def delete_expense(expense_id):
    supabase.table("expenses").delete().eq("id", expense_id).execute()


def bulk_insert_expenses(user_id, df):
    records = []
    for _, r in df.iterrows():
        row = _app_dict_to_db(r.to_dict(), EXPENSES_APP_TO_DB)
        row["user_id"] = user_id
        records.append(row)
    if records:
        supabase.table("expenses").insert(records).execute()


def delete_all_expenses(user_id):
    supabase.table("expenses").delete().eq("user_id", user_id).execute()


# ============================================================
# INVENTORY
# ============================================================
def fetch_inventory(user_id):
    res = supabase.table("inventory").select("*").eq("user_id", user_id).order("item").execute()
    return _rows_to_df(res.data, INVENTORY_DB_TO_APP)


def insert_inventory_item(user_id, item_dict):
    row = _app_dict_to_db(item_dict, INVENTORY_APP_TO_DB)
    row["user_id"] = user_id
    supabase.table("inventory").insert(row).execute()


def delete_inventory_item(item_id):
    supabase.table("inventory").delete().eq("id", item_id).execute()


def bulk_insert_inventory(user_id, df):
    records = []
    for _, r in df.iterrows():
        row = _app_dict_to_db(r.to_dict(), INVENTORY_APP_TO_DB)
        row["user_id"] = user_id
        records.append(row)
    if records:
        supabase.table("inventory").insert(records).execute()


def delete_all_inventory(user_id):
    supabase.table("inventory").delete().eq("user_id", user_id).execute()
