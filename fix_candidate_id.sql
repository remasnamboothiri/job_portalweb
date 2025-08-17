-- Fix candidate_id column issue in jobapp_interview table

-- Drop existing foreign key constraint if it exists
ALTER TABLE jobapp_interview DROP CONSTRAINT IF EXISTS jobapp_interview_candidate_id_fkey;

-- Add candidate_id column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='jobapp_interview' AND column_name='candidate_id') THEN
        ALTER TABLE jobapp_interview ADD COLUMN candidate_id INTEGER;
    END IF;
END $$;

-- Add the foreign key constraint
ALTER TABLE jobapp_interview 
ADD CONSTRAINT jobapp_interview_candidate_id_fkey 
FOREIGN KEY (candidate_id) REFERENCES jobapp_customuser(id) ON DELETE SET NULL;