-- ============================================================
-- Supabase Database Setup for Small Business Sales & Profit Analyzer
-- Run this SQL in your Supabase project's SQL Editor
-- ============================================================

-- 1. Sales table
CREATE TABLE IF NOT EXISTS sales (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  item TEXT NOT NULL,
  category TEXT NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
  total NUMERIC(12,2) NOT NULL,
  region TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Expenses table
CREATE TABLE IF NOT EXISTS expenses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  category TEXT NOT NULL,
  amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
  description TEXT DEFAULT '',
  region TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Inventory table
CREATE TABLE IF NOT EXISTS inventory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  item TEXT NOT NULL,
  stock INTEGER NOT NULL DEFAULT 0,
  unit_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Login activity table (used by Admin Dashboard)
CREATE TABLE IF NOT EXISTS login_activity (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  email TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('success', 'failed')),
  details TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Session activity table (login/logout/admin dashboard time)
CREATE TABLE IF NOT EXISTS session_activity (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  email TEXT NOT NULL,
  login_at TIMESTAMPTZ NOT NULL,
  logout_at TIMESTAMPTZ NULL,
  admin_dashboard_seconds INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 7. Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_sales_user ON sales(user_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date);
CREATE INDEX IF NOT EXISTS idx_expenses_user ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_inventory_user ON inventory(user_id);
CREATE INDEX IF NOT EXISTS idx_login_activity_created_at ON login_activity(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_login_activity_email ON login_activity(email);
CREATE INDEX IF NOT EXISTS idx_session_activity_created_at ON session_activity(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_session_activity_email ON session_activity(email);

-- 8. Enable Row Level Security
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE login_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_activity ENABLE ROW LEVEL SECURITY;

-- 9. RLS Policies — users can only access their own data
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'sales' AND policyname = 'Users manage own sales'
  ) THEN
    CREATE POLICY "Users manage own sales" ON sales
      FOR ALL USING (auth.uid() = user_id);
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'session_activity' AND policyname = 'Admins manage session activity'
  ) THEN
    CREATE POLICY "Admins manage session activity" ON session_activity
      FOR ALL USING (auth.jwt() -> 'user_metadata' ->> 'role' = 'admin')
      WITH CHECK (auth.jwt() -> 'user_metadata' ->> 'role' = 'admin');
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'expenses' AND policyname = 'Users manage own expenses'
  ) THEN
    CREATE POLICY "Users manage own expenses" ON expenses
      FOR ALL USING (auth.uid() = user_id);
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'inventory' AND policyname = 'Users manage own inventory'
  ) THEN
    CREATE POLICY "Users manage own inventory" ON inventory
      FOR ALL USING (auth.uid() = user_id);
  END IF;
END $$;

-- Admin-only read/write for login activity based on JWT metadata role=admin
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'login_activity' AND policyname = 'Admins manage login activity'
  ) THEN
    CREATE POLICY "Admins manage login activity" ON login_activity
      FOR ALL USING (auth.jwt() -> 'user_metadata' ->> 'role' = 'admin')
      WITH CHECK (auth.jwt() -> 'user_metadata' ->> 'role' = 'admin');
  END IF;
END $$;
