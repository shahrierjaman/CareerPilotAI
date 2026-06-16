"""
job_recommender.py — fetch real jobs from Adzuna / Jooble / JSearch APIs and compute match scores.
"""

import requests
import logging
import html
import re
from utils.skill_extractor import extract_skills

# ── Country mapping (Adzuna‑supported subset) ──────────────────────────────────
COUNTRY_MAP = {
    "United States": "us",
    "United Kingdom": "gb",
    "Canada": "ca",
    "Germany": "de",
    "France": "fr",
    "Australia": "au",
    "India": "in",
    "Netherlands": "nl",
    "Singapore": "sg",
    "Spain": "es",
    "Italy": "it",
    "Brazil": "br",
    "Japan": "jp",
    "South Africa": "za",
    "Sweden": "se",
    "Ireland": "ie",
    "New Zealand": "nz",
    "Poland": "pl",
    "Switzerland": "ch",
    "Bangladesh": None,          # Adzuna doesn't support; will fall through
}

# ── Demo jobs (used only when no API keys or all requests fail) ────────────────
DEMO_JOBS = [
    {
        "title": "Data Scientist",
        "company": "TechCorp",
        "location": "San Francisco, CA (Remote)",
        "description": "Looking for a Data Scientist with Python, SQL, Machine Learning, and Pandas experience. Build predictive models and analyze large datasets.",
        "url": "https://www.linkedin.com/jobs/",
        "source": "Demo",
        "salary": "$120k - $160k",
        "posted": "2025-01-15",
    },
    {
        "title": "Machine Learning Engineer",
        "company": "AI Solutions Inc.",
        "location": "New York, NY",
        "description": "Seeking an ML Engineer skilled in TensorFlow, PyTorch, Docker, and Kubernetes to deploy models at scale.",
        "url": "https://www.indeed.com/",
        "source": "Demo",
        "salary": "$140k - $180k",
        "posted": "2025-01-12",
    },
    {
        "title": "Data Analyst",
        "company": "Global Analytics",
        "location": "London, UK",
        "description": "Analyze business data using SQL, Excel, Tableau, and Python. Strong communication skills required.",
        "url": "https://www.linkedin.com/jobs/",
        "source": "Demo",
        "salary": "£45k - £55k",
        "posted": "2025-01-10",
    },
    {
        "title": "Software Engineer (Python)",
        "company": "StartupXYZ",
        "location": "Remote",
        "description": "Build backend services with Python, Flask, PostgreSQL, and AWS. Familiarity with CI/CD and Agile is a plus.",
        "url": "https://www.linkedin.com/jobs/",
        "source": "Demo",
        "salary": "$110k - $140k",
        "posted": "2025-01-14",
    },
    {
        "title": "Junior Data Scientist",
        "company": "DataDriven Co.",
        "location": "Austin, TX",
        "description": "Entry-level role for candidates with Python, SQL, and basic ML knowledge. Willingness to learn is key.",
        "url": "https://www.indeed.com/",
        "source": "Demo",
        "salary": "$80k - $100k",
        "posted": "2025-01-16",
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudFirst",
        "location": "Berlin, Germany",
        "description": "Manage Kubernetes clusters, CI/CD pipelines, and infrastructure as code (Terraform). AWS or Azure experience needed.",
        "url": "https://www.linkedin.com/jobs/",
        "source": "Demo",
        "salary": "€70k - €90k",
        "posted": "2025-01-11",
    },
]


def _clean_html_tags(text: str) -> str:
    """Remove all HTML tags from a string, leaving only plain text."""
    # Remove anything that looks like an HTML tag
    clean = re.sub(r'<[^>]*>', '', text)
    # Collapse multiple spaces
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def fetch_jobs(
    skills: list,
    job_title: str = "",
    country_name: str = "United States",
    location: str = "",
    remote_only: bool = False,
    max_results: int = 6,
    adzuna_app_id: str = "",
    adzuna_app_key: str = "",
    jooble_key: str = "",
    api_keys: dict = None,
) -> list:
    """
    Fetch real job listings using multiple APIs in this order:
    1. Adzuna (if country supported and keys present)
    2. Jooble (if key present)
    3. JSearch (if key present)
    Falls back to demo jobs if no API keys or all attempts fail.
    """
    keys = {
        "adzuna_app_id": adzuna_app_id,
        "adzuna_app_key": adzuna_app_key,
        "jooble_key": jooble_key,
        "jsearch_key": "",
    }
    if api_keys:
        keys.update({k: v for k, v in api_keys.items() if v})

    country_code = COUNTRY_MAP.get(country_name, None)
    jobs = []

    # 1. Adzuna
    if country_code is not None and keys["adzuna_app_id"] and keys["adzuna_app_key"]:
        try:
            jobs = _fetch_adzuna(
                app_id=keys["adzuna_app_id"],
                app_key=keys["adzuna_app_key"],
                country_code=country_code,
                title=job_title or " ".join(skills[:3]),
                location=location,
                max_results=max_results,
            )
            if jobs:
                logging.info(f"Fetched {len(jobs)} jobs from Adzuna")
                return _normalize_adzuna_jobs(jobs)
        except Exception as e:
            logging.warning(f"Adzuna API failed: {e}")

    # 2. Jooble
    if keys["jooble_key"]:
        try:
            jobs = _fetch_jooble(
                api_key=keys["jooble_key"],
                keywords=job_title or " ".join(skills[:3]),
                location=location or country_name,
                max_results=max_results,
            )
            if jobs:
                logging.info(f"Fetched {len(jobs)} jobs from Jooble")
                return jobs   # already normalized inside _fetch_jooble
        except Exception as e:
            logging.warning(f"Jooble API failed: {e}")

    # 3. JSearch
    if keys["jsearch_key"]:
        try:
            jobs = _fetch_jsearch(
                api_key=keys["jsearch_key"],
                keywords=job_title or " ".join(skills[:3]),
                location=location or country_name,
                max_results=max_results,
            )
            if jobs:
                logging.info(f"Fetched {len(jobs)} jobs from JSearch")
                return jobs
        except Exception as e:
            logging.warning(f"JSearch API failed: {e}")

    # Fallback to demo
    if not any(keys.values()):
        logging.info("No API keys set – using demo jobs.")
    else:
        logging.warning("All API attempts failed. Showing demo data.")
    return _filter_demo(skills, job_title, location, remote_only, max_results)


def _fetch_adzuna(app_id, app_key, country_code, title, location, max_results):
    base_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": max_results,
        "what": title,
        "where": location or "",
        "content-type": "application/json",
    }
    resp = requests.get(base_url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", [])


def _normalize_adzuna_jobs(jobs: list) -> list:
    normalized = []
    for job in jobs:
        company = job.get("company", {}).get("display_name", "") if isinstance(job.get("company"), dict) else job.get("company", "")
        location = job.get("location", {}).get("display_name", "") if isinstance(job.get("location"), dict) else job.get("location", "")
        salary = ""
        if isinstance(job.get("salary_min"), (int, float)) and isinstance(job.get("salary_max"), (int, float)):
            salary = f"${job['salary_min']} - ${job['salary_max']}"
        else:
            salary = job.get("salary", "")
        raw_desc = job.get("description", "")
        desc = _clean_html_tags(html.unescape(raw_desc))
        normalized.append({
            "title": job.get("title", ""),
            "company": company,
            "location": location,
            "description": desc,
            "url": job.get("redirect_url", ""),
            "source": "Adzuna",
            "salary": salary,
            "posted": job.get("created", "")[:10] if job.get("created") else "",
        })
    return normalized


def _fetch_jooble(api_key, keywords, location, max_results):
    url = f"https://jooble.org/api/{api_key}"
    payload = {
        "keywords": keywords,
        "location": location,
        "page": 1,
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    raw_jobs = data.get("jobs", [])
    normalized = []
    for job in raw_jobs[:max_results]:
        snippet = job.get("snippet", "")
        if snippet.startswith("&nbsp;..."):
            snippet = snippet[9:]  # remove leading "&nbsp;..."
        desc = _clean_html_tags(html.unescape(snippet))
        normalized.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "description": desc,
            "url": job.get("link", ""),
            "source": "Jooble",
            "salary": job.get("salary", ""),
            "posted": job.get("updated", "")[:10] if job.get("updated") else "",
        })
    return normalized


def _fetch_jsearch(api_key, keywords, location, max_results):
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": f"{keywords} in {location}" if location else keywords,
        "page": "1",
        "num_pages": str(max_results),
    }
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    jobs = data.get("data", [])
    normalized = []
    for job in jobs:
        raw_desc = job.get("job_description", "")
        desc = _clean_html_tags(html.unescape(raw_desc))
        normalized.append({
            "title": job.get("job_title", ""),
            "company": job.get("employer_name", ""),
            "location": f"{job.get('job_city', '')}, {job.get('job_country', '')}".strip(", "),
            "description": desc,
            "url": job.get("job_apply_link", job.get("job_google_link", "")),
            "source": "JSearch",
            "salary": job.get("job_salary", ""),
            "posted": job.get("job_posted_at", "")[:10] if job.get("job_posted_at") else "",
        })
    return normalized


def _filter_demo(skills, job_title, location, remote_only, max_results):
    filtered = []
    for job in DEMO_JOBS:
        if job_title and job_title.lower() not in job["title"].lower():
            continue
        if location and location.lower() not in job["location"].lower():
            continue
        if remote_only and "remote" not in job["location"].lower():
            continue
        filtered.append(job)
        if len(filtered) >= max_results:
            break
    return filtered


def compute_job_match(user_skills: list, job: dict) -> dict:
    description = job.get("description", "")
    if not description:
        return {"match_pct": 0, "matching_skills": [], "missing_skills": []}

    job_tech, _ = extract_skills(description)

    if not job_tech:
        return {"match_pct": 0, "matching_skills": [], "missing_skills": []}

    user_lower = {s.lower() for s in user_skills}
    job_lower = {s.lower() for s in job_tech}

    matching = [s for s in job_tech if s.lower() in user_lower]
    missing = [s for s in job_tech if s.lower() not in user_lower]

    match_pct = (len(matching) / len(job_tech)) * 100 if job_tech else 0

    return {
        "match_pct": round(match_pct, 1),
        "matching_skills": matching,
        "missing_skills": missing,
    }