USE job_market_analyzer;

INSERT IGNORE INTO skills (skill_id, skill_name) VALUES
    (1, 'python'),
    (2, 'git'),
    (3, 'sql'),
    (4, 'flask'),
    (5, 'docker'),
    (6, 'java'),
    (7, 'javascript'),
    (8, 'html'),
    (9, 'css'),
    (10, 'testing'),
    (11, 'pytest'),
    (12, 'selenium'),
    (13, 'linux'),
    (14, 'networking'),
    (15, 'security'),
    (16, 'object-oriented programming'),
    (17, 'react'),
    (18, 'node.js'),
    (19, 'mysql'),
    (20, 'postgresql'),
    (21, 'pandas'),
    (22, 'excel'),
    (23, 'power bi'),
    (24, 'aws'),
    (25, 'azure'),
    (26, 'c#'),
    (27, 'c++'),
    (28, 'typescript'),
    (29, 'jira'),
    (30, 'rest api');

INSERT IGNORE INTO jobs (   -- 我们用 INSERT IGNORE，正是为了兼容你已经在 Console 手动插入过的数据
    job_id,
    company,
    title,
    location,
    workplace_type,
    employment_type,
    experience_level,
    salary_min,
    salary_max
) VALUES
    (1, 'Northern Byte Labs', 'Software Engineer Intern', 'Edmonton, AB', 'hybrid', 'internship', 'entry', 45000, 58000),
    (2, 'Prairie Data Group', 'Data Analyst Intern', 'Calgary, AB', 'hybrid', 'internship', 'entry', 43000, 55000),
    (3, 'Vertex Cloud', 'Junior Backend Developer', 'Edmonton, AB', 'remote', 'full_time', 'junior', 65000, 82000),
    (4, 'Maple Health Tech', 'QA Automation Intern', 'Edmonton, AB', 'hybrid', 'internship', 'entry', 43000, 55000),
    (5, 'Peak Commerce', 'Junior Software Developer', 'Calgary, AB', 'onsite', 'full_time', 'junior', 62000, 78000),
    (6, 'Aurora Digital', 'Frontend Developer Intern', 'Canada Remote', 'remote', 'internship', 'entry', 42000, 54000),
    (7, 'Greenline Systems', 'Data Engineer', 'Calgary, AB', 'hybrid', 'full_time', 'junior', 70000, 88000),
    (8, 'Northstar Finance', 'Junior Java Developer', 'Edmonton, AB', 'onsite', 'full_time', 'junior', 68000, 85000),
    (9, 'Urban Transit Labs', 'Business Intelligence Analyst', 'Edmonton, AB', 'hybrid', 'full_time', 'junior', 63000, 79000),
    (10, 'RapidRoute Systems', 'Junior Full Stack Developer', 'Canada Remote', 'remote', 'full_time', 'junior', 64000, 79000),
    (11, 'Cedar Cybersecurity', 'Security Analyst Intern', 'Calgary, AB', 'hybrid', 'internship', 'entry', 44000, 56000),
    (12, 'Alberta Energy Analytics', 'Data Analyst', 'Calgary, AB', 'hybrid', 'full_time', 'junior', 67000, 83000),
    (13, 'Blue River Software', 'Python Developer', 'Edmonton, AB', 'remote', 'full_time', 'junior', 68000, 86000),
    (14, 'Westgrid Networks', 'Network Support Technician', 'Edmonton, AB', 'onsite', 'full_time', 'entry', 50000, 65000),
    (15, 'Cobalt Media', 'Web Developer Intern', 'Canada Remote', 'remote', 'internship', 'entry', 40000, 52000),
    (16, 'Evergreen Insurance', 'QA Tester', 'Calgary, AB', 'hybrid', 'full_time', 'entry', 54000, 68000),
    (17, 'Atlas Manufacturing', 'Junior C# Developer', 'Edmonton, AB', 'onsite', 'full_time', 'junior', 63000, 80000),
    (18, 'Northern Lights AI', 'Machine Learning Intern', 'Canada Remote', 'remote', 'internship', 'entry', 46000, 60000),
    (19, 'Summit Consulting', 'Software Test Engineer', 'Calgary, AB', 'hybrid', 'full_time', 'junior', 65000, 81000),
    (20, 'Prairie Retail Tech', 'Database Administrator Intern', 'Edmonton, AB', 'onsite', 'internship', 'entry', 43000, 56000),
    (21, 'Riverstone Solutions', 'Junior Python Developer', 'Edmonton, AB', 'hybrid', 'full_time', 'junior', 66000, 84000),
    (22, 'Cloudbridge Canada', 'DevOps Engineer', 'Canada Remote', 'remote', 'full_time', 'intermediate', 85000, 110000),
    (23, 'Maple Education Tech', 'Technical Support Specialist', 'Calgary, AB', 'hybrid', 'part_time', 'entry', 38000, 48000),
    (24, 'Borealis Logistics', 'Junior Data Engineer', 'Edmonton, AB', 'onsite', 'full_time', 'junior', 69000, 87000),
    (25, 'Canyon Software', 'React Developer', 'Canada Remote', 'remote', 'full_time', 'junior', 67000, 85000),
    (26, 'North Peak Health', 'Systems Administrator', 'Calgary, AB', 'onsite', 'full_time', 'junior', 62000, 78000),
    (27, 'RapidRoute Systems', 'Junior Full Stack Developer', 'Canada Remote', 'remote', 'full_time', 'junior', 64000, 79000),
    (28, 'Aspen Analytics', 'Power BI Analyst', 'Edmonton, AB', 'hybrid', 'full_time', 'junior', 60000, 76000),
    (29, 'Ironwood Games', 'Junior Java Developer', 'Calgary, AB', 'hybrid', 'full_time', 'junior', 65000, 82000),
    (30, 'Frontier Cloud Services', 'Cloud Support Engineer', 'Canada Remote', 'remote', 'full_time', 'entry', 58000, 72000);


INSERT IGNORE INTO job_skills (job_id, skill_id, skill_type) VALUES
    (1, 1, 'required'), (1, 2, 'required'), (1, 3, 'required'), (1, 4, 'preferred'), (1, 5, 'preferred'),
    (2, 3, 'required'), (2, 21, 'required'), (2, 22, 'required'), (2, 23, 'preferred'),
    (3, 1, 'required'), (3, 3, 'required'), (3, 19, 'required'), (3, 2, 'preferred'),
    (4, 1, 'required'), (4, 10, 'required'), (4, 11, 'required'), (4, 12, 'preferred'),
    (5, 6, 'required'), (5, 16, 'required'), (5, 2, 'required'), (5, 3, 'preferred'),
    (6, 7, 'required'), (6, 8, 'required'), (6, 9, 'required'), (6, 17, 'preferred'),
    (7, 1, 'required'), (7, 3, 'required'), (7, 19, 'required'), (7, 24, 'preferred'),
    (8, 6, 'required'), (8, 16, 'required'), (8, 3, 'required'), (8, 2, 'preferred'),
    (9, 3, 'required'), (9, 21, 'required'), (9, 22, 'required'), (9, 23, 'preferred'),
    (10, 7, 'required'), (10, 17, 'required'), (10, 18, 'required'), (10, 3, 'preferred'),
    (11, 13, 'required'), (11, 14, 'required'), (11, 15, 'required'), (11, 2, 'preferred'),
    (12, 3, 'required'), (12, 21, 'required'), (12, 22, 'required'), (12, 23, 'preferred'),
    (13, 1, 'required'), (13, 3, 'required'), (13, 2, 'required'), (13, 4, 'preferred'),
    (14, 13, 'required'), (14, 14, 'required'), (14, 2, 'required'), (14, 29, 'preferred'),
    (15, 8, 'required'), (15, 9, 'required'), (15, 7, 'required'), (15, 17, 'preferred'),
    (16, 10, 'required'), (16, 11, 'required'), (16, 2, 'required'), (16, 29, 'preferred'),
    (17, 26, 'required'), (17, 16, 'required'), (17, 3, 'required'), (17, 2, 'preferred'),
    (18, 1, 'required'), (18, 21, 'required'), (18, 3, 'required'), (18, 24, 'preferred'),
    (19, 10, 'required'), (19, 11, 'required'), (19, 12, 'required'), (19, 2, 'preferred'),
    (20, 3, 'required'), (20, 19, 'required'), (20, 13, 'required'), (20, 2, 'preferred'),
    (21, 1, 'required'), (21, 3, 'required'), (21, 2, 'required'), (21, 4, 'preferred'),
    (22, 5, 'required'), (22, 13, 'required'), (22, 24, 'required'), (22, 25, 'preferred'),
    (23, 2, 'required'), (23, 29, 'required'), (23, 10, 'preferred'),
    (24, 1, 'required'), (24, 3, 'required'), (24, 19, 'required'), (24, 5, 'preferred'),
    (25, 7, 'required'), (25, 17, 'required'), (25, 28, 'required'), (25, 8, 'preferred'),
    (26, 13, 'required'), (26, 14, 'required'), (26, 19, 'required'), (26, 29, 'preferred'),
    (27, 7, 'required'), (27, 8, 'required'), (27, 9, 'required'), (27, 17, 'preferred'),
    (28, 23, 'required'), (28, 22, 'required'), (28, 3, 'required'), (28, 21, 'preferred'),
    (29, 6, 'required'), (29, 16, 'required'), (29, 3, 'required'), (29, 2, 'preferred'),
    (30, 24, 'required'), (30, 13, 'required'), (30, 5, 'required'), (30, 25, 'preferred');


SELECT
    jobs.title,
    skills.skill_name,
    job_skills.skill_type
FROM job_skills
         INNER JOIN skills
                    ON skills.skill_id = job_skills.skill_id
         INNER JOIN jobs
                    ON jobs.job_id = job_skills.job_id
WHERE jobs.job_id = 2;

USE job_market_analyzer;

SELECT *
FROM jobs
WHERE employment_type = 'internship';




SELECT
    j.job_id,
    j.company,
    j.title,
    j.location,
    j.application_url,
    GROUP_CONCAT(DISTINCT s.skill_name ORDER BY s.skill_name SEPARATOR ', ') AS matched_skills
FROM jobs AS j
         JOIN job_skills AS js
              ON js.job_id = j.job_id
         JOIN skills AS s
              ON s.skill_id = js.skill_id
WHERE s.skill_name IN (
                       'c',
                       'linux',
                       'operating systems',
                       'reverse engineering',
                       'cybersecurity',
                       'network security',
                       'application security',
                       'penetration testing',
                       'exploit development',
                       'cryptography',
                       'web application firewall',
                       'web application and api protection'
    )
GROUP BY
    j.job_id, j.company, j.title, j.location, j.application_url
ORDER BY j.job_id DESC;











