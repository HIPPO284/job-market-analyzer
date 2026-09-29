USE job_market_analyzer;

ALTER TABLE jobs
    ADD COLUMN source_name VARCHAR(120),
    ADD COLUMN source_job_id VARCHAR(100),
    ADD COLUMN source_updated_at DATE,
    ADD COLUMN description_text TEXT,
    ADD CONSTRAINT uq_jobs_source UNIQUE (source_name, source_job_id);


SHOW COLUMNS FROM jobs;
SHOW INDEX FROM jobs WHERE Key_name = 'uq_jobs_source';

