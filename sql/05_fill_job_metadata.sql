USE job_market_analyzer;

UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-15', application_deadline = '2026-10-15', application_url = NULL WHERE job_id = 1;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-16', application_deadline = '2026-10-16', application_url = NULL WHERE job_id = 2;
UPDATE jobs SET minimum_education_level = NULL, posted_date = '2026-09-17', application_deadline = NULL, application_url = NULL WHERE job_id = 3;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-12', application_deadline = '2026-10-12', application_url = NULL WHERE job_id = 4;
UPDATE jobs SET minimum_education_level = 'master', posted_date = '2026-09-18', application_deadline = '2026-10-25', application_url = NULL WHERE job_id = 5;

UPDATE jobs SET minimum_education_level = NULL, posted_date = '2026-09-10', application_deadline = '2026-10-10', application_url = NULL WHERE job_id = 6;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-14', application_deadline = '2026-10-14', application_url = NULL WHERE job_id = 7;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-19', application_deadline = '2026-10-19', application_url = NULL WHERE job_id = 8;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-11', application_deadline = '2026-10-11', application_url = NULL WHERE job_id = 9;
UPDATE jobs SET minimum_education_level = 'master', posted_date = '2026-09-08', application_deadline = '2026-10-08', application_url = NULL WHERE job_id = 10;

UPDATE jobs SET minimum_education_level = NULL, posted_date = '2026-09-17', application_deadline = NULL, application_url = NULL WHERE job_id = 11;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-06', application_deadline = '2026-10-06', application_url = NULL WHERE job_id = 12;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-13', application_deadline = '2026-10-13', application_url = NULL WHERE job_id = 13;
UPDATE jobs SET minimum_education_level = 'master', posted_date = '2026-09-20', application_deadline = '2026-11-01', application_url = NULL WHERE job_id = 14;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-05', application_deadline = '2026-10-05', application_url = NULL WHERE job_id = 15;

UPDATE jobs SET minimum_education_level = NULL, posted_date = '2026-09-09', application_deadline = '2026-10-09', application_url = NULL WHERE job_id = 16;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-15', application_deadline = '2026-10-20', application_url = NULL WHERE job_id = 17;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-16', application_deadline = '2026-10-16', application_url = NULL WHERE job_id = 18;
UPDATE jobs SET minimum_education_level = 'master', posted_date = '2026-09-18', application_deadline = '2026-10-30', application_url = NULL WHERE job_id = 19;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-10', application_deadline = NULL, application_url = NULL WHERE job_id = 20;

UPDATE jobs SET minimum_education_level = NULL, posted_date = '2026-09-07', application_deadline = '2026-10-07', application_url = NULL WHERE job_id = 21;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-12', application_deadline = '2026-10-12', application_url = NULL WHERE job_id = 22;
UPDATE jobs SET minimum_education_level = 'master', posted_date = '2026-09-19', application_deadline = '2026-11-05', application_url = NULL WHERE job_id = 23;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-01', application_deadline = '2026-09-30', application_url = NULL WHERE job_id = 24;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-13', application_deadline = '2026-10-13', application_url = NULL WHERE job_id = 25;

UPDATE jobs SET minimum_education_level = NULL, posted_date = '2026-09-16', application_deadline = '2026-10-16', application_url = NULL WHERE job_id = 26;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-18', application_deadline = '2026-10-31', application_url = NULL WHERE job_id = 27;
UPDATE jobs SET minimum_education_level = 'master', posted_date = '2026-09-20', application_deadline = '2026-11-10', application_url = NULL WHERE job_id = 28;
UPDATE jobs SET minimum_education_level = 'bachelor', posted_date = '2026-09-05', application_deadline = '2026-10-05', application_url = NULL WHERE job_id = 29;
UPDATE jobs SET minimum_education_level = NULL, posted_date = '2026-09-15', application_deadline = '2026-10-15', application_url = NULL WHERE job_id = 30;

SELECT job_id, title, minimum_education_level, posted_date,
       application_deadline, application_url
FROM jobs
ORDER BY job_id;