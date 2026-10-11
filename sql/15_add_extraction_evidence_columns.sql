-- Run this once in the MySQL Local Root console.
USE job_market_analyzer;

ALTER TABLE jobs
    ADD COLUMN education_requirement_text TEXT NULL,
    ADD COLUMN experience_requirement_text TEXT NULL,
    ADD COLUMN working_time_text TEXT NULL;

SHOW COLUMNS FROM jobs
WHERE Field IN (
    'education_requirement_text',
    'experience_requirement_text',
    'working_time_text'
);
