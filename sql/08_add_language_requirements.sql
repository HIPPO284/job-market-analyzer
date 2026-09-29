USE job_market_analyzer;

ALTER TABLE jobs
    ADD COLUMN language_requirements TEXT NULL;