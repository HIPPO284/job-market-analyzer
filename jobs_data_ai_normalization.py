from pydantic import BaseModel
from ollama import chat
from job_sources.greenhouse_source import greenhouse_jobs

class JobExtraction(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    language_requirements: list[str]
    minimum_education_level: str | None
    education_requirement_text: str | None
    experience_requirement_text: str | None
    employment_type: str | None
    role_summary: str | None
    salary_min: int | None
    salary_max: int | None
    salary_period: str | None
    salary_currency: str | None

SYSTEM_PROMPT = """
You are a job posting information extractor.

Extract information only from the provided job description.
Do not use outside knowledge.
Do not guess missing information.
Do not add commentary, explanations, markdown, or extra fields.

Required skills:
- Extract only specific, job-relevant hard skills that can reasonably be
  selected from a skills list: programming languages, frameworks, databases,
  cloud platforms, operating systems, security technologies, data tools, or
  named professional software.
- Return short canonical skill labels, never full sentences. For example:
  "python", "sql", "aws", "salesforce", "cloud security".
- Do not extract soft skills, personality traits, physical abilities, travel
  requirements, generic responsibilities, quota targets, years of experience,
  degrees, human languages, benefits, or company marketing language.
- Do not turn a general task into a skill. For example, do not extract
  "communication", "sales negotiation", "meeting targets", or
  "willingness to use AI tools".
- Return at most 12 required skills. If more are mentioned, keep only the
  most specific tools, technologies, and directly required hard skills.

Preferred skills:
- Extract skills explicitly described as preferred, desirable, nice-to-have,
  a plus, or bonus qualifications.
- If a skill is clearly required and also appears in a preferred section,
  place it only in required_skills.
- Return at most 8 preferred skills and follow the same hard-skill rules.

Language requirements:
- Extract human language requirements only.
- Preserve the required proficiency when explicitly stated.
- Use concise values such as "English (fluent)" or
  "Cantonese (required)".
- Do not include programming languages in language_requirements.

Education:
- minimum_education_level may only be one of:
  "high_school", "diploma", "associate", "bachelor", "master", or "phd".
- Use null when no strict minimum education level is explicitly required.
- If the description says that education can be replaced by equivalent work
  experience, set minimum_education_level to null.
- Put the relevant original education requirement into
  education_requirement_text.

Experience:
- Put explicit years-of-experience requirements or experience conditions into
  experience_requirement_text.
- Do not infer years of experience from the job title.

Employment type:
- Use only "full_time", "part_time", "internship", "contract", or "temporary"
  when explicitly stated.
- Otherwise return null.

Salary:
- Extract only explicitly stated salary ranges or salary amounts.
- Keep salary values in the original currency and original pay period.
- Convert abbreviated values such as "418K" to 418000.
- salary_period may only be "annual", "monthly", "weekly", "biweekly",
  "daily", or "hourly".
- Do not convert currencies.
- Do not annualize monthly, weekly, daily, or hourly pay.
- Do not treat benefits, equity, bonuses, or vague compensation statements as
  a salary range.
- If a salary range clearly includes variable compensation, commission, or OTE,
  return null for all salary fields.

Role summary:
- Write one factual English sentence of no more than 30 words.
- Summarize the primary purpose and responsibilities of the role.
- Do not include company marketing language or unsupported claims.

For missing text fields return null.
For missing list fields return [].
Return only data that matches the requested schema.
"""

job_description = greenhouse_jobs[1]["description_text"]

response = chat(
    model="gpt-oss:20b",
    format=JobExtraction.model_json_schema(),
    messages=[
        {
            "role" : "system",
            "content" : SYSTEM_PROMPT,
        },
        {
            "role" : "user",
            "content" :  ("Extract structured information from the job description below.\n\n" + job_description),
        }
    ],
)
print(response.message.content)
