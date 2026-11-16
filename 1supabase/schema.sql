-- School House Elections 2026 — Supabase Postgres Schema (4 House Leadership Roles + Storage + RLS)
-- Roles: Boys Captain (Vote_10_Boy), Girls Captain (Vote_10_Girl), Boys Vice Captain (Vote_9_Boy), Girls Vice Captain (Vote_9_Girl)
-- Run in Supabase Dashboard -> SQL Editor (idempotent; safe to re-run to upgrade existing tables)

-- 1. Core tables (lowercase snake_case per PostgreSQL best practices)
create table if not exists public.voters (
  admission_no text primary key,
  full_name text not null,
  class_name text not null default '',
  section text not null default '',
  house_code text not null,
  house_name text not null,
  final_status text not null default 'Not Voted',
  voted_for text not null default '',
  vote_10_boy text not null default '',
  vote_10_girl text not null default '',
  vote_9_boy text not null default '',
  vote_9_girl text not null default '',
  candidate_id text,
  position_name text not null default 'House Captains & Vice Captains',
  ballot_id text,
  cast_at timestamptz,
  cancelled_at timestamptz,
  active_photo_field text,
  photo_path text not null default '',
  photos_history jsonb not null default '[]'::jsonb,
  is_active boolean not null default true,
  updated_at timestamptz not null default now()
);

-- Upgrade existing voters table safely if created from an earlier version
alter table public.voters add column if not exists vote_10_boy text not null default '';
alter table public.voters add column if not exists vote_10_girl text not null default '';
alter table public.voters add column if not exists vote_9_boy text not null default '';
alter table public.voters add column if not exists vote_9_girl text not null default '';

create table if not exists public.candidates (
  id text primary key,
  admission_no text not null,
  full_name text not null,
  class_name text not null default '',
  section text not null default '',
  house_code text not null,
  house_name text not null,
  position_id text not null default 'CAPTAIN_BOY',
  position_name text not null default 'Boys Captain (Class 10 Boy)',
  tagline text not null default '',
  is_approved boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.ballots (
  id text primary key,
  election_id text not null default 'ELECTION_2026',
  admission_no text not null,
  house_code text not null,
  position_id text not null default 'CAPTAIN_BOY',
  candidate_id text not null,
  candidate_name text not null,
  position_name text not null default 'Boys Captain (Class 10 Boy)',
  photo_field text not null default 'Photo',
  photo_path text not null default '',
  status text not null default 'accepted',
  cast_at timestamptz not null default now(),
  cancelled_at timestamptz,
  cancel_reason text,
  cancelled_by text
);

alter table public.ballots add column if not exists position_id text not null default 'CAPTAIN_BOY';
alter table public.ballots add column if not exists booth_name text not null default 'Booth 1';
alter table public.voters add column if not exists booth_name text not null default 'Booth 1';

create table if not exists public.audit_logs (
  id text primary key,
  action text not null,
  ballot_id text,
  admission_no text,
  student_name text,
  house_code text,
  reason text,
  actor text,
  created_at timestamptz not null default now()
);

-- 2. Idempotent constraints (safe on re-run)
do $$
begin
  alter table public.voters drop constraint if exists voters_house_code_check;

  update public.voters
  set house_code = 'BHEESHMA', house_name = 'Bheeshma'
  where house_code in ('BISHMA', 'BHISHMA');

  update public.ballots
  set house_code = 'BHEESHMA'
  where house_code in ('BISHMA', 'BHISHMA');

  update public.audit_logs
  set house_code = 'BHEESHMA'
  where house_code in ('BISHMA', 'BHISHMA');

  delete from public.candidates
  where house_code in ('BISHMA', 'BHISHMA');

  alter table public.voters
    add constraint voters_house_code_check
    check (house_code in ('BHEESHMA', 'GURUDRONA', 'HANUMAN', 'KARNA', 'VASISTHA', 'VISHWAMITHRA', 'CENTRAL', 'ALL'));

  if not exists (
    select 1 from pg_constraint
    where conname = 'voters_final_status_check'
      and conrelid = 'public.voters'::regclass
  ) then
    alter table public.voters
      add constraint voters_final_status_check
      check (final_status in ('Not Voted', 'Voted', 'Cancelled'));
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'ballots_voter_fkey'
      and conrelid = 'public.ballots'::regclass
  ) then
    alter table public.ballots
      add constraint ballots_voter_fkey
      foreign key (admission_no) references public.voters(admission_no);
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'ballots_status_check'
      and conrelid = 'public.ballots'::regclass
  ) then
    alter table public.ballots
      add constraint ballots_status_check
      check (status in ('accepted', 'cancelled'));
  end if;
end $$;

-- 3. Indexes & database-enforced single-active-vote-per-role guard
create index if not exists voters_house_code_idx on public.voters (house_code);
create index if not exists voters_final_status_idx on public.voters (final_status);
create index if not exists candidates_house_pos_approved_idx on public.candidates (house_code, position_id, is_approved);
create index if not exists ballots_house_status_idx on public.ballots (house_code, status);
create index if not exists ballots_house_pos_status_idx on public.ballots (house_code, position_id, status);
create index if not exists ballots_admission_no_idx on public.ballots (admission_no);

drop index if exists public.ballots_one_accepted_per_voter_idx;
create unique index if not exists ballots_one_accepted_per_voter_role_idx
  on public.ballots (admission_no, position_id)
  where status = 'accepted';

-- 4. Clean overview view compatible with security_invoker (PostgreSQL 15+), mirroring all 4 Vote columns
drop view if exists public.elections_overview;
create view public.elections_overview
with (security_invoker = true) as
select
  admission_no as "Admission No.",
  full_name as "Name",
  class_name as "Class",
  section as "Section",
  house_name as "House",
  vote_10_boy as "Vote_10_Boy",
  vote_10_girl as "Vote_10_Girl",
  vote_9_boy as "Vote_9_Boy",
  vote_9_girl as "Vote_9_Girl",
  photo_path as "Photo",
  final_status as "Final",
  cast_at as "Time",
  ballot_id,
  cancelled_at
from public.voters;

-- 5. Expose schema cleanly & enable Row Level Security on all tables
grant usage on schema public to anon, authenticated, service_role;
grant select, insert, update on public.voters, public.candidates to anon, authenticated, service_role;
grant select, insert, update, delete on public.ballots to anon, authenticated, service_role;
grant select, insert on public.audit_logs to anon, authenticated, service_role;
grant select on public.elections_overview to anon, authenticated, service_role;

alter table public.voters enable row level security;
alter table public.candidates enable row level security;
alter table public.ballots enable row level security;
alter table public.audit_logs enable row level security;

drop policy if exists voters_select_policy on public.voters;
create policy voters_select_policy on public.voters
  for select to anon, authenticated, service_role using (true);

drop policy if exists voters_insert_policy on public.voters;
create policy voters_insert_policy on public.voters
  for insert to anon, authenticated, service_role with check (true);

drop policy if exists voters_update_policy on public.voters;
create policy voters_update_policy on public.voters
  for update to anon, authenticated, service_role using (true) with check (true);

drop policy if exists candidates_select_policy on public.candidates;
create policy candidates_select_policy on public.candidates
  for select to anon, authenticated, service_role using (true);

drop policy if exists candidates_write_policy on public.candidates;
create policy candidates_write_policy on public.candidates
  for insert to anon, authenticated, service_role with check (true);

drop policy if exists candidates_update_policy on public.candidates;
create policy candidates_update_policy on public.candidates
  for update to anon, authenticated, service_role using (true) with check (true);

drop policy if exists ballots_select_policy on public.ballots;
create policy ballots_select_policy on public.ballots
  for select to anon, authenticated, service_role using (true);

drop policy if exists ballots_insert_policy on public.ballots;
create policy ballots_insert_policy on public.ballots
  for insert to anon, authenticated, service_role with check (status = 'accepted');

drop policy if exists ballots_update_policy on public.ballots;
create policy ballots_update_policy on public.ballots
  for update to anon, authenticated, service_role
  using (status = 'accepted')
  with check (status = 'cancelled');

drop policy if exists ballots_delete_policy on public.ballots;
create policy ballots_delete_policy on public.ballots
  for delete to anon, authenticated, service_role
  using (true);

drop policy if exists audit_logs_select_policy on public.audit_logs;
create policy audit_logs_select_policy on public.audit_logs
  for select to anon, authenticated, service_role using (true);

drop policy if exists audit_logs_insert_policy on public.audit_logs;
create policy audit_logs_insert_policy on public.audit_logs
  for insert to anon, authenticated, service_role with check (true);

-- 6. Private Storage Bucket for Verification Photos
insert into storage.buckets (id, name, public)
values ('voter-photos', 'voter-photos', false)
on conflict (id) do nothing;

drop policy if exists voter_photos_select on storage.objects;
create policy voter_photos_select on storage.objects
  for select to anon, authenticated, service_role
  using (bucket_id = 'voter-photos');

drop policy if exists voter_photos_insert on storage.objects;
create policy voter_photos_insert on storage.objects
  for insert to anon, authenticated, service_role
  with check (bucket_id = 'voter-photos');

drop policy if exists voter_photos_update on storage.objects;
create policy voter_photos_update on storage.objects
  for update to anon, authenticated, service_role
  using (bucket_id = 'voter-photos')
  with check (bucket_id = 'voter-photos');

drop policy if exists voter_photos_delete on storage.objects;
create policy voter_photos_delete on storage.objects
  for delete to anon, authenticated, service_role
  using (bucket_id = 'voter-photos');
