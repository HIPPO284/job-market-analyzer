USE job_market_analyzer;

ALTER TABLE jobs
    ADD COLUMN source_name VARCHAR(120),
    ADD COLUMN source_job_id VARCHAR(100),
    ADD COLUMN source_updated_at DATE,
    ADD COLUMN description_text TEXT,
    ADD CONSTRAINT uq_jobs_source UNIQUE (source_name, source_job_id);


SHOW COLUMNS FROM jobs;
SHOW INDEX FROM jobs WHERE Key_name = 'uq_jobs_source';

ALTER TABLE jobs
    MODIFY location VARCHAR(300) NOT NULL;


ALTER TABLE jobs
    MODIFY COLUMN company VARCHAR(255) NOT NULL,
    MODIFY COLUMN title VARCHAR(512) NOT NULL,
    MODIFY COLUMN location TEXT NOT NULL,
    MODIFY COLUMN description_text MEDIUMTEXT NULL,
    MODIFY COLUMN application_url TEXT NULL,
    MODIFY COLUMN source_job_id VARCHAR(255) NULL;

ALTER TABLE locations
    MODIFY COLUMN name VARCHAR(255) NOT NULL;

ALTER TABLE skills
    MODIFY COLUMN skill_name VARCHAR(200) NOT NULL;

ALTER TABLE skill_aliases
    MODIFY COLUMN alias_name VARCHAR(255) NOT NULL;