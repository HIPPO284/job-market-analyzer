import json
from pathlib import Path
from datetime import datetime
from time import perf_counter
from job_sources.greenhouse_source import fetch_greenhouse_jobs
from jobs_data_ai_normalization import greenhouse_ai_normalizer, SYSTEM_PROMPT


if __name__ == "__main__":
    sample_ids = {
        7504487,  # 薪资包含奖金
        8188498,  # 薪资说明位于金额之前
        8172582,  # 学历可以用工作经验替代
        8234130,  # 虽然写 required，但允许经验替代
        7774167,  # 正在攻读学位的实习生
    }

    input_path = Path(__file__).parent / "greenhouse_output_20261008_224038.json"
    saved_jobs = json.loads(input_path.read_text(encoding="utf-8"))

    sample_jobs = []
    for job in saved_jobs:
        if job["source_job_id"] in sample_ids:
            sample_jobs.append({
                "id": job["source_job_id"],
                "title": job["title"],
                "content": job["description_text"],
                "offices": job.get("raw_offices") or [],
                "location": {
                    "name": job.get("raw_location_text") or ""
                },
            })

    print(f"Found {len(sample_jobs)} sample jobs")

    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 找到已有的最大编号，下一次加一
    run_number = 1
    for existing_file in output_dir.glob("skill_prompt_check_*.json"):
        number_text = (
            existing_file.stem
            .removeprefix("skill_prompt_check_")
            .split("_")[0]
        )
        if number_text.isdigit():
            run_number = max(run_number, int(number_text) + 1)

    started_at = datetime.now().astimezone()
    timer_start = perf_counter()

    ai_output = greenhouse_ai_normalizer(sample_jobs)

    elapsed_seconds = round(perf_counter() - timer_start, 2)
    finished_at = datetime.now().astimezone()

    output_path = output_dir / (
        f"skill_prompt_check_{run_number:03d}_"
        f"{started_at:%Y%m%d_%H%M%S}.json"
    )

    result = {
        "run_number": run_number,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "elapsed_seconds": elapsed_seconds,
        "system_prompt": SYSTEM_PROMPT,
        "source_jobs": sample_jobs,
        "ai_output": ai_output,
    }

    with output_path.open("x", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print(f"Test number: {run_number}")
    print(f"Normalized {len(ai_output)} jobs")
    print(f"Elapsed: {elapsed_seconds} seconds")
    print(f"Saved to: {output_path}")

    print(f"Normalized {len(ai_output)} jobs")
    print(f"Saved to: {output_path}")