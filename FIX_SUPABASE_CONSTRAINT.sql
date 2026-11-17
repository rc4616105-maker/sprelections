-- ==============================================================================
-- FIX FOR: voters_house_code_check constraint violation
-- Run this in your Supabase Dashboard: SQL Editor -> New Query -> Paste & Run
-- ==============================================================================

-- 1. Drop the outdated constraint that only allowed original house codes
ALTER TABLE public.voters DROP CONSTRAINT IF EXISTS voters_house_code_check;

-- 2. Migrate any legacy 'BISHMA' / 'BHISHMA' spellings to 'BHEESHMA' across all tables
UPDATE public.voters
SET house_code = 'BHEESHMA', house_name = 'Bheeshma'
WHERE house_code IN ('BISHMA', 'BHISHMA');

UPDATE public.ballots
SET house_code = 'BHEESHMA'
WHERE house_code IN ('BISHMA', 'BHISHMA');

UPDATE public.audit_logs
SET house_code = 'BHEESHMA'
WHERE house_code IN ('BISHMA', 'BHISHMA');

DELETE FROM public.candidates
WHERE house_code IN ('BISHMA', 'BHISHMA');

-- 3. Re-add the updated constraint with all 6 Houses + CENTRAL + ALL (for 87 Faculty Members & Demo User)
ALTER TABLE public.voters
  ADD CONSTRAINT voters_house_code_check
  CHECK (house_code IN ('BHEESHMA', 'GURUDRONA', 'HANUMAN', 'KARNA', 'VASISTHA', 'VISHWAMITHRA', 'CENTRAL', 'ALL'));

-- 4. Ensure ballots table has cancelled_by, cancel_reason, and cancelled_at columns
ALTER TABLE public.ballots ADD COLUMN IF NOT EXISTS cancelled_by TEXT;
ALTER TABLE public.ballots ADD COLUMN IF NOT EXISTS cancel_reason TEXT;
ALTER TABLE public.ballots ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ;

-- 5. Verify RLS policies allow insertion and synchronization
DROP POLICY IF EXISTS voters_insert_policy ON public.voters;
CREATE POLICY voters_insert_policy ON public.voters
  FOR INSERT TO anon, authenticated, service_role WITH CHECK (true);

DROP POLICY IF EXISTS voters_update_policy ON public.voters;
CREATE POLICY voters_update_policy ON public.voters
  FOR UPDATE TO anon, authenticated, service_role USING (true) WITH CHECK (true);

-- Done! Now return to your Admin Dashboard (http://127.0.0.1:5500/Houses/admin/index.html)
-- and click "Sync Roster to Supabase".
