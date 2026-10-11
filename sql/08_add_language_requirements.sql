USE job_market_analyzer;

ALTER TABLE jobs
    ADD COLUMN language_requirements TEXT NULL;


USE job_market_analyzer;

-- Stripe 171-320 coverage expansion.
-- This script is safe to run again:
-- 1. existing skill names are skipped;
-- 2. an existing alias is left linked as it was;
-- 3. aliases are always linked through the real skill_id in skills.

START TRANSACTION;

-- skills.skill_id is not AUTO_INCREMENT in the current schema.
-- Start after the current largest ID, then assign one ID per missing standard skill.
SET @next_skill_id := (SELECT COALESCE(MAX(skill_id), 0) FROM skills);

INSERT INTO skills (skill_id, skill_name)
SELECT
    @next_skill_id := @next_skill_id + 1,
    candidate.skill_name
FROM (
         SELECT 'a/b testing' AS skill_name
         UNION ALL SELECT 'aml'
         UNION ALL SELECT 'content marketing'
         UNION ALL SELECT 'databricks'
         UNION ALL SELECT 'deep learning'
         UNION ALL SELECT 'experimentation'
         UNION ALL SELECT 'financial crimes'
         UNION ALL SELECT 'fraud detection'
         UNION ALL SELECT 'fraud prevention'
         UNION ALL SELECT 'kyb'
         UNION ALL SELECT 'kyc'
         UNION ALL SELECT 'marketing automation'
         UNION ALL SELECT 'partner management'
         UNION ALL SELECT 'payment processing'
         UNION ALL SELECT 'privacy'
         UNION ALL SELECT 'solutions architecture'
         UNION ALL SELECT 'statistical analysis'
         UNION ALL SELECT 'technical account management'
         UNION ALL SELECT 'technical accounting'
         UNION ALL SELECT 'transfer pricing'
     ) AS candidate
         LEFT JOIN skills AS existing
                   ON existing.skill_name = candidate.skill_name
WHERE existing.skill_id IS NULL
ORDER BY candidate.skill_name;

-- Each row is: standard skill name -> spelling / abbreviation used in job postings.
-- The JOIN obtains the real skill_id inserted above, so no IDs are hand-written.
INSERT INTO skill_aliases (skill_id, alias_name)
SELECT
    s.skill_id,
    candidate.alias_name
FROM (
         SELECT 'a/b testing' AS skill_name, 'a/b testing' AS alias_name
         UNION ALL SELECT 'a/b testing', 'a b testing'
         UNION ALL SELECT 'a/b testing', 'ab testing'
         UNION ALL SELECT 'a/b testing', 'split testing'

         UNION ALL SELECT 'aml', 'aml'
         UNION ALL SELECT 'aml', 'anti money laundering'
         UNION ALL SELECT 'aml', 'anti-money-laundering'

         UNION ALL SELECT 'content marketing', 'content marketing'

         UNION ALL SELECT 'databricks', 'databricks'
         UNION ALL SELECT 'databricks', 'databricks lakehouse'
         UNION ALL SELECT 'databricks', 'databricks platform'

         UNION ALL SELECT 'deep learning', 'deep learning'
         UNION ALL SELECT 'deep learning', 'neural network'
         UNION ALL SELECT 'deep learning', 'neural networks'

         UNION ALL SELECT 'experimentation', 'experimentation'
         UNION ALL SELECT 'experimentation', 'product experimentation'

         UNION ALL SELECT 'financial crimes', 'financial crime'
         UNION ALL SELECT 'financial crimes', 'financial crime investigations'
         UNION ALL SELECT 'financial crimes', 'financial crimes'

         UNION ALL SELECT 'fraud detection', 'fraud detection'
         UNION ALL SELECT 'fraud detection', 'fraud monitoring'

         UNION ALL SELECT 'fraud prevention', 'fraud mitigation'
         UNION ALL SELECT 'fraud prevention', 'fraud prevention'

         UNION ALL SELECT 'kyb', 'know your business'
         UNION ALL SELECT 'kyb', 'know-your-business'
         UNION ALL SELECT 'kyb', 'kyb'

         UNION ALL SELECT 'kyc', 'know your customer'
         UNION ALL SELECT 'kyc', 'know-your-customer'
         UNION ALL SELECT 'kyc', 'kyc'

         UNION ALL SELECT 'marketing automation', 'marketing automation'

         UNION ALL SELECT 'partner management', 'partner management'
         UNION ALL SELECT 'partner management', 'partnership management'

         UNION ALL SELECT 'payment processing', 'card payment processing'
         UNION ALL SELECT 'payment processing', 'payment processing'
         UNION ALL SELECT 'payment processing', 'payments processing'

         UNION ALL SELECT 'privacy', 'data privacy'
         UNION ALL SELECT 'privacy', 'privacy'
         UNION ALL SELECT 'privacy', 'privacy management'
         UNION ALL SELECT 'privacy', 'privacy operations'

         UNION ALL SELECT 'solutions architecture', 'solution architecture'
         UNION ALL SELECT 'solutions architecture', 'solutions architecture'

         UNION ALL SELECT 'statistical analysis', 'statistical analysis'
         UNION ALL SELECT 'statistical analysis', 'statistical modeling'
         UNION ALL SELECT 'statistical analysis', 'statistical modelling'

         UNION ALL SELECT 'technical account management', 'technical account management'
         UNION ALL SELECT 'technical account management', 'technical account manager'

         UNION ALL SELECT 'technical accounting', 'technical accounting'

         UNION ALL SELECT 'transfer pricing', 'transfer pricing'

         -- These two standard skills already exist in your database.
         UNION ALL SELECT 'sox compliance', 'sarbanes-oxley'
         UNION ALL SELECT 'sox compliance', 'sox'
         UNION ALL SELECT 'sanctions compliance', 'sanctions screening'
         UNION ALL SELECT 'sanctions compliance', 'sanctions screening compliance'
     ) AS candidate
         JOIN skills AS s
              ON s.skill_name = candidate.skill_name
ON DUPLICATE KEY UPDATE
    alias_name = VALUES(alias_name);

COMMIT;

-- Verification: every new alias should display with the standard skill it references.
SELECT
    s.skill_id,
    s.skill_name,
    a.alias_name
FROM skills AS s
         LEFT JOIN skill_aliases AS a
                   ON a.skill_id = s.skill_id
WHERE s.skill_name IN (
                       'a/b testing', 'aml', 'content marketing', 'databricks',
                       'deep learning', 'experimentation', 'financial crimes',
                       'fraud detection', 'fraud prevention', 'kyb', 'kyc',
                       'marketing automation', 'partner management', 'payment processing',
                       'privacy', 'solutions architecture', 'statistical analysis',
                       'technical account management', 'technical accounting',
                       'transfer pricing', 'sox compliance', 'sanctions compliance'
    )
ORDER BY s.skill_name, a.alias_name;
