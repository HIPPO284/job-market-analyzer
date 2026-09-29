USE job_market_analyzer;

ALTER TABLE job_skills
    DROP FOREIGN KEY job_skills_ibfk_1;

ALTER TABLE jobs
    MODIFY COLUMN job_id INT NOT NULL AUTO_INCREMENT;

ALTER TABLE job_skills
    ADD CONSTRAINT fk_job_skills_job
        FOREIGN KEY (job_id)
            REFERENCES jobs(job_id);

DESCRIBE jobs;
DESCRIBE job_skills;
SHOW CREATE TABLE job_skills;
SHOW CREATE TABLE jobs;

USE job_market_analyzer;
SHOW INDEX FROM skills;
SHOW CREATE TABLE skills;