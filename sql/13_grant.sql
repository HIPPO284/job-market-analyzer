GRANT INSERT, UPDATE
    ON job_market_analyzer.jobs
    TO 'job_app'@'localhost';

GRANT INSERT, UPDATE
    ON job_market_analyzer.locations
    TO 'job_app'@'localhost';

GRANT INSERT, UPDATE, DELETE
    ON job_market_analyzer.job_skills
    TO 'job_app'@'localhost';

GRANT INSERT, UPDATE, DELETE
    ON job_market_analyzer.job_locations
    TO 'job_app'@'localhost';