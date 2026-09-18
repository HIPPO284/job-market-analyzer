CREATE DATABASE IF NOT EXISTS job_market_analyzer
CHARACTER SET utf8mb4;

USE job_market_analyzer;

CREATE TABLE IF NOT EXISTS jobs (
    job_id INT PRIMARY KEY,
    company VARCHAR(150) NOT NULL,
    title VARCHAR(150) NOT NULL,
    location VARCHAR(100) NOT NULL,
    workplace_type VARCHAR(25) NOT NULL,
    employment_type VARCHAR(25) NOT NULL,
    experience_level VARCHAR(25) NOT NULL,
    salary_min INT NOT NULL,
    salary_max INT NOT NULL,

    CONSTRAINT chk_salary_min_nonnegative
        CHECK (salary_min >= 0),

    CONSTRAINT chk_salary_range
        CHECK (salary_max >= salary_min)
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id INT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id INT NOT NULL,
    skill_id INT NOT NULL,
    skill_type VARCHAR(20) NOT NULL,

    CONSTRAINT chk_skill_type
        CHECK (skill_type IN ('required', 'preferred')),

    PRIMARY KEY (job_id, skill_id),

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id),

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id)
);