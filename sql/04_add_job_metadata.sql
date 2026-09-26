USE job_market_analyzer;

ALTER TABLE jobs
    MODIFY COLUMN workplace_type VARCHAR(25) NULL,
    MODIFY COLUMN employment_type VARCHAR(25) NULL,
    MODIFY COLUMN experience_level VARCHAR(25) NULL,
    MODIFY COLUMN salary_min INT NULL,
    MODIFY COLUMN salary_max INT NULL,
    ADD COLUMN minimum_education_level VARCHAR(20) NULL,
    ADD COLUMN posted_date DATE NULL,
    ADD COLUMN application_deadline DATE NULL,
    ADD COLUMN application_url VARCHAR(2048) NULL;

DESCRIBE jobs;