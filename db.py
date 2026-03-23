import pandas as pd
import json
import os
import uuid
import streamlit as st
from supabase_client import supabase, SUPABASE_AVAILABLE

# ============================================================
# Local JSON storage directory (fallback when Supabase is down)
# ============================================================
LOCAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "local_data")
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)

BATCH_SIZE = 500  # Max rows per Supabase insert to avoid payload limits


def _use_supabase():
    """Always use Supabase when it's available (auth is Supabase-only)."""
    return SUPABASE_AVAILABLE and supabase is not None


def _local_path(user_id, table):
    return os.path.join(LOCAL_DATA_DIR, f"{user_id}_{table}.json")


def _load_local(user_id, table):
    path = _local_path(user_id, table)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_local(user_id, table, rows):
    path = _local_path(user_id, table)
    with open(path, "w") as f:
        json.dump(rows, f, indent=2)


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
    """Convert an app-facing dict to DB column names, ensuring JSON-safe types."""
    row = {}
    for k, v in app_dict.items():
        if k in col_map:
            # Convert numpy / pandas types to native Python for JSON serialization
            if hasattr(v, 'item'):  # numpy scalar
                v = v.item()
            elif pd.isna(v):
                v = None
            row[col_map[k]] = v
    return row


# ============================================================
# SALES
# ============================================================
def fetch_sales(user_id):
    if _use_supabase():
        res = supabase.table("sales").select("*").eq("user_id", user_id).order("date", desc=True).execute()
        return _rows_to_df(res.data, SALES_DB_TO_APP)
    rows = _load_local(user_id, "sales")
    if not rows:
        return pd.DataFrame(columns=list(SALES_DB_TO_APP.values()))
    df = pd.DataFrame(rows)
    return df.sort_values("Date", ascending=False).reset_index(drop=True)


def insert_sale(user_id, sale_dict):
    if _use_supabase():
        row = _app_dict_to_db(sale_dict, SALES_APP_TO_DB)
        row["user_id"] = user_id
        supabase.table("sales").insert(row).execute()
    else:
        rows = _load_local(user_id, "sales")
        entry = dict(sale_dict)
        entry["id"] = str(uuid.uuid4())
        rows.append(entry)
        _save_local(user_id, "sales", rows)


def delete_sale(sale_id, user_id=None):
    if _use_supabase():
        supabase.table("sales").delete().eq("id", sale_id).execute()
    elif user_id:
        rows = [r for r in _load_local(user_id, "sales") if r.get("id") != sale_id]
        _save_local(user_id, "sales", rows)


def bulk_insert_sales(user_id, df):
    if _use_supabase():
        records = []
        for _, r in df.iterrows():
            row = _app_dict_to_db(r.to_dict(), SALES_APP_TO_DB)
            row["user_id"] = user_id
            records.append(row)
        for i in range(0, len(records), BATCH_SIZE):
            supabase.table("sales").insert(records[i:i + BATCH_SIZE]).execute()
    else:
        rows = _load_local(user_id, "sales")
        for _, r in df.iterrows():
            entry = r.to_dict()
            entry["id"] = str(uuid.uuid4())
            rows.append(entry)
        _save_local(user_id, "sales", rows)


def delete_all_sales(user_id):
    if _use_supabase():
        supabase.table("sales").delete().eq("user_id", user_id).execute()
    else:
        _save_local(user_id, "sales", [])


# ============================================================
# EXPENSES
# ============================================================
def fetch_expenses(user_id):
    if _use_supabase():
        res = supabase.table("expenses").select("*").eq("user_id", user_id).order("date", desc=True).execute()
        return _rows_to_df(res.data, EXPENSES_DB_TO_APP)
    rows = _load_local(user_id, "expenses")
    if not rows:
        return pd.DataFrame(columns=list(EXPENSES_DB_TO_APP.values()))
    df = pd.DataFrame(rows)
    return df.sort_values("Date", ascending=False).reset_index(drop=True) if "Date" in df.columns else df


def insert_expense(user_id, expense_dict):
    if _use_supabase():
        row = _app_dict_to_db(expense_dict, EXPENSES_APP_TO_DB)
        row["user_id"] = user_id
        supabase.table("expenses").insert(row).execute()
    else:
        rows = _load_local(user_id, "expenses")
        entry = dict(expense_dict)
        entry["id"] = str(uuid.uuid4())
        rows.append(entry)
        _save_local(user_id, "expenses", rows)


def delete_expense(expense_id, user_id=None):
    if _use_supabase():
        supabase.table("expenses").delete().eq("id", expense_id).execute()
    elif user_id:
        rows = [r for r in _load_local(user_id, "expenses") if r.get("id") != expense_id]
        _save_local(user_id, "expenses", rows)


def bulk_insert_expenses(user_id, df):
    if _use_supabase():
        records = []
        for _, r in df.iterrows():
            row = _app_dict_to_db(r.to_dict(), EXPENSES_APP_TO_DB)
            row["user_id"] = user_id
            records.append(row)
        for i in range(0, len(records), BATCH_SIZE):
            supabase.table("expenses").insert(records[i:i + BATCH_SIZE]).execute()
    else:
        rows = _load_local(user_id, "expenses")
        for _, r in df.iterrows():
            entry = r.to_dict()
            entry["id"] = str(uuid.uuid4())
            rows.append(entry)
        _save_local(user_id, "expenses", rows)


def delete_all_expenses(user_id):
    if _use_supabase():
        supabase.table("expenses").delete().eq("user_id", user_id).execute()
    else:
        _save_local(user_id, "expenses", [])


# ============================================================
# INVENTORY
# ============================================================
def fetch_inventory(user_id):
    if _use_supabase():
        res = supabase.table("inventory").select("*").eq("user_id", user_id).order("item").execute()
        return _rows_to_df(res.data, INVENTORY_DB_TO_APP)
    rows = _load_local(user_id, "inventory")
    if not rows:
        return pd.DataFrame(columns=list(INVENTORY_DB_TO_APP.values()))
    return pd.DataFrame(rows)


def insert_inventory_item(user_id, item_dict):
    if _use_supabase():
        row = _app_dict_to_db(item_dict, INVENTORY_APP_TO_DB)
        row["user_id"] = user_id
        supabase.table("inventory").insert(row).execute()
    else:
        rows = _load_local(user_id, "inventory")
        entry = dict(item_dict)
        entry["id"] = str(uuid.uuid4())
        rows.append(entry)
        _save_local(user_id, "inventory", rows)


def delete_inventory_item(item_id, user_id=None):
    if _use_supabase():
        supabase.table("inventory").delete().eq("id", item_id).execute()
    elif user_id:
        rows = [r for r in _load_local(user_id, "inventory") if r.get("id") != item_id]
        _save_local(user_id, "inventory", rows)


def bulk_insert_inventory(user_id, df):
    if _use_supabase():
        records = []
        for _, r in df.iterrows():
            row = _app_dict_to_db(r.to_dict(), INVENTORY_APP_TO_DB)
            row["user_id"] = user_id
            records.append(row)
        for i in range(0, len(records), BATCH_SIZE):
            supabase.table("inventory").insert(records[i:i + BATCH_SIZE]).execute()
    else:
        rows = _load_local(user_id, "inventory")
        for _, r in df.iterrows():
            entry = r.to_dict()
            entry["id"] = str(uuid.uuid4())
            rows.append(entry)
        _save_local(user_id, "inventory", rows)


def delete_all_inventory(user_id):
    if _use_supabase():
        supabase.table("inventory").delete().eq("user_id", user_id).execute()
    else:
        _save_local(user_id, "inventory", [])
