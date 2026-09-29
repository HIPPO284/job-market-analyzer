USE job_market_analyzer;

CREATE TABLE skill_aliases (
    alias_id  INT NOT NULL AUTO_INCREMENT,
    alias_name VARCHAR(100) NOT NULL UNIQUE,
    skill_id INT NOT NULL,
    PRIMARY KEY (alias_id),
    CONSTRAINT fk_alias_skill FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);

SHOW COLUMNS FROM skill_aliases;
SHOW INDEX FROM skill_aliases;
SHOW CREATE TABLE skill_aliases;

USE job_market_analyzer;

INSERT INTO skill_aliases (alias_name, skill_id)
VALUES
    ('python 3', 1),
    ('python3', 1),
    ('python programming', 1);

SELECT
    skill_aliases.alias_id,
    skill_aliases.alias_name,
    skills.skill_id,
    skills.skill_name AS canonical_skill
FROM skill_aliases
         JOIN skills
              ON skill_aliases.skill_id = skills.skill_id
ORDER BY skill_aliases.alias_id;

INSERT INTO skill_aliases (alias_name, skill_id)
VALUES ('python3', 1);