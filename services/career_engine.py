"""
career_engine.py — gap analysis, learning path generation, and career readiness scoring.
"""

from data.skills_database import JOB_ROLE_SKILLS, get_available_roles


def analyze_skill_gap(user_skills: list, target_role: str) -> dict:
    """
    Compare user's skills to target role requirements.
    Returns a dict with:
        - coverage_pct: percentage of core skills covered
        - matching_core: list of core skills user already has
        - core_missing: core skills user lacks
        - advanced_missing: advanced skills user lacks
        - nice_to_have_missing: nice-to-have skills user lacks
        - all_core: full list of core skills for the role
    """
    if target_role not in JOB_ROLE_SKILLS:
        # If role unknown, return empty gap (no requirements)
        return {
            "coverage_pct": 100,
            "matching_core": [],
            "core_missing": [],
            "advanced_missing": [],
            "nice_to_have_missing": [],
            "all_core": [],
        }

    role_reqs = JOB_ROLE_SKILLS[target_role]
    core = role_reqs.get("core", [])
    advanced = role_reqs.get("advanced", [])
    nice_to_have = role_reqs.get("nice_to_have", [])

    # Normalize user skills to lowercase for comparison
    user_lower = {s.lower() for s in user_skills}

    matching_core = [s for s in core if s.lower() in user_lower]
    core_missing = [s for s in core if s.lower() not in user_lower]
    advanced_missing = [s for s in advanced if s.lower() not in user_lower]
    nice_missing = [s for s in nice_to_have if s.lower() not in user_lower]

    coverage = (len(matching_core) / len(core) * 100) if core else 100

    return {
        "coverage_pct": round(coverage, 1),
        "matching_core": matching_core,
        "core_missing": core_missing,
        "advanced_missing": advanced_missing,
        "nice_to_have_missing": nice_missing,
        "all_core": core,
    }


def generate_learning_path(user_skills: list, target_role: str, gap_data: dict = None) -> list:
    """
    Generate an ordered list of learning steps to bridge skill gaps.
    Each step is a dict with:
        step, skill, priority, reason, estimated_time, resources
    """
    if gap_data is None:
        gap_data = analyze_skill_gap(user_skills, target_role)

    core_missing = gap_data.get("core_missing", [])
    advanced_missing = gap_data.get("advanced_missing", [])
    nice_missing = gap_data.get("nice_to_have_missing", [])

    # Combine missing skills with priority labels
    to_learn = []
    for skill in core_missing:
        to_learn.append({"skill": skill, "priority": "Essential", "reason": f"Required for {target_role} roles"})
    for skill in advanced_missing:
        to_learn.append({"skill": skill, "priority": "Important", "reason": f"Expected for senior {target_role} positions"})
    for skill in nice_missing:
        to_learn.append({"skill": skill, "priority": "Nice-to-Have", "reason": f"Differentiates you from other candidates"})

    # Sort: Essential first, then Important, then Nice-to-Have
    priority_order = {"Essential": 0, "Important": 1, "Nice-to-Have": 2}
    to_learn.sort(key=lambda x: priority_order.get(x["priority"], 99))

    # Build steps
    steps = []
    for i, item in enumerate(to_learn, 1):
        skill = item["skill"]
        priority = item["priority"]
        reason = item["reason"]
        resources = _get_resources_for_skill(skill)
        estimated_time = _estimate_learning_time(skill, priority)
        steps.append({
            "step": i,
            "skill": skill,
            "priority": priority,
            "reason": reason,
            "estimated_time": estimated_time,
            "resources": resources,
        })

    return steps


def _get_resources_for_skill(skill: str) -> list:
    """
    Return free learning resources for a given skill.
    Each resource: {type, title, url}
    """
    # A simple mapping for some popular skills. Fallback: generic search link.
    resource_map = {
        "Python": [
            {"type": "Course", "title": "Python for Everybody (Coursera)", "url": "https://www.coursera.org/specializations/python"},
            {"type": "Interactive", "title": "freeCodeCamp Python", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/"},
            {"type": "YouTube", "title": "Python Full Course (Programming with Mosh)", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc"},
        ],
        "SQL": [
            {"type": "Course", "title": "SQL for Data Science (Coursera)", "url": "https://www.coursera.org/learn/sql-for-data-science"},
            {"type": "Interactive", "title": "SQLZoo", "url": "https://sqlzoo.net/"},
            {"type": "YouTube", "title": "SQL Tutorial (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
        ],
        "Machine Learning": [
            {"type": "Course", "title": "Machine Learning by Andrew Ng (Coursera)", "url": "https://www.coursera.org/learn/machine-learning"},
            {"type": "Interactive", "title": "Kaggle Learn", "url": "https://www.kaggle.com/learn"},
            {"type": "Book", "title": "Hands-On ML with Scikit-Learn & TensorFlow", "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/"},
        ],
        "Deep Learning": [
            {"type": "Course", "title": "Deep Learning Specialization (Coursera)", "url": "https://www.coursera.org/specializations/deep-learning"},
            {"type": "Course", "title": "fast.ai Practical Deep Learning", "url": "https://course.fast.ai/"},
            {"type": "YouTube", "title": "Deep Learning Crash Course (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=VyWAvY2CF9c"},
        ],
        "TensorFlow": [
            {"type": "Course", "title": "TensorFlow Developer Certificate (Coursera)", "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice"},
            {"type": "Documentation", "title": "TensorFlow Official Tutorials", "url": "https://www.tensorflow.org/tutorials"},
        ],
        "PyTorch": [
            {"type": "Course", "title": "PyTorch for Deep Learning (freeCodeCamp)", "url": "https://www.freecodecamp.org/learn/deep-learning-with-pytorch/"},
            {"type": "Documentation", "title": "PyTorch Tutorials", "url": "https://pytorch.org/tutorials/"},
        ],
        "Docker": [
            {"type": "Course", "title": "Docker for Beginners (freeCodeCamp)", "url": "https://www.freecodecamp.org/news/docker-handbook/"},
            {"type": "Interactive", "title": "Play with Docker", "url": "https://labs.play-with-docker.com/"},
            {"type": "YouTube", "title": "Docker Tutorial (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE"},
        ],
        "Kubernetes": [
            {"type": "Course", "title": "Kubernetes Basics (freeCodeCamp)", "url": "https://www.freecodecamp.org/news/kubernetes-course/"},
            {"type": "Interactive", "title": "Kubernetes Playground", "url": "https://www.katacoda.com/courses/kubernetes"},
        ],
        "AWS": [
            {"type": "Course", "title": "AWS Cloud Practitioner Essentials (AWS Free)", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/"},
            {"type": "YouTube", "title": "AWS Certified Cloud Practitioner (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=SOTamWNgDKc"},
        ],
        "Statistics": [
            {"type": "Course", "title": "Statistics with Python (Coursera)", "url": "https://www.coursera.org/specializations/statistics-with-python"},
            {"type": "Book", "title": "OpenIntro Statistics (free)", "url": "https://www.openintro.org/book/os/"},
        ],
        "Data Structures": [
            {"type": "Course", "title": "Data Structures & Algorithms (freeCodeCamp)", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"},
            {"type": "Interactive", "title": "LeetCode (free tier)", "url": "https://leetcode.com/"},
        ],
        "Algorithms": [
            {"type": "Course", "title": "Algorithms Specialization (Coursera)", "url": "https://www.coursera.org/specializations/algorithms"},
        ],
        "Linux": [
            {"type": "Course", "title": "Linux for Beginners (freeCodeCamp)", "url": "https://www.freecodecamp.org/news/linux-command-line-tutorial/"},
        ],
        "Git": [
            {"type": "Interactive", "title": "Learn Git Branching", "url": "https://learngitbranching.js.org/"},
            {"type": "YouTube", "title": "Git & GitHub Crash Course (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk"},
        ],
        "R": [
            {"type": "Course", "title": "R Programming (Coursera)", "url": "https://www.coursera.org/learn/r-programming"},
        ],
        "Tableau": [
            {"type": "Course", "title": "Tableau Public (free)", "url": "https://public.tableau.com/en-us/s/resources"},
        ],
        "Power BI": [
            {"type": "Course", "title": "Microsoft Learn: Power BI", "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi"},
        ],
        "JavaScript": [
            {"type": "Interactive", "title": "freeCodeCamp JavaScript", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"},
        ],
        "HTML5": [
            {"type": "Interactive", "title": "freeCodeCamp HTML", "url": "https://www.freecodecamp.org/learn/responsive-web-design/"},
        ],
        "CSS3": [
            {"type": "Interactive", "title": "freeCodeCamp CSS", "url": "https://www.freecodecamp.org/learn/responsive-web-design/"},
        ],
    }

    # Generic fallback resources
    generic_resources = [
        {"type": "Course", "title": f"Search freeCodeCamp for '{skill}'", "url": f"https://www.freecodecamp.org/news/search/?query={skill.replace(' ', '%20')}"},
        {"type": "Course", "title": f"Search Coursera (audit) for '{skill}'", "url": f"https://www.coursera.org/search?query={skill.replace(' ', '%20')}"},
        {"type": "YouTube", "title": f"Search YouTube for '{skill} tutorial'", "url": f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial"},
    ]

    return resource_map.get(skill, generic_resources)


def _estimate_learning_time(skill: str, priority: str) -> str:
    """Rough estimate of learning time based on skill complexity and priority."""
    short_skills = {"Git", "SQL", "Linux", "HTML5", "CSS3", "Docker", "Tableau", "Power BI", "R"}
    medium_skills = {"Python", "Statistics", "Data Structures", "Algorithms", "JavaScript", "AWS", "Kubernetes", "TensorFlow", "PyTorch"}
    # long/complex skills default to 3-6 months

    if skill in short_skills:
        base = "1–3 weeks"
    elif skill in medium_skills:
        base = "1–3 months"
    else:
        base = "3–6 months"

    if priority == "Essential":
        return base + " (focus first)"
    elif priority == "Important":
        return base
    else:
        return "2–4 months (optional)"


def compute_career_readiness(
    ats_score: float,
    tech_skills: list,
    soft_skills: list,
    has_certifications: bool,
    years_experience: float,
    avg_job_match: float
) -> dict:
    """
    Compute a career readiness score (0-100) and level.
    Returns dict with score, level, level_color, breakdown, suggestions.
    """
    # Weights for overall readiness
    w_ats = 25
    w_tech_skills = 25
    w_soft_skills = 10
    w_certs = 5
    w_experience = 20
    w_job_match = 15

    # Convert each component to 0-100 scale
    ats_component = ats_score  # already 0-100
    tech_component = min(len(tech_skills) * 5, 100)  # 20 skills = 100
    soft_component = min(len(soft_skills) * 10, 100)  # 10 soft skills = 100
    cert_component = 100 if has_certifications else 0
    exp_component = min(years_experience * 10, 100)  # 10 years = 100
    match_component = avg_job_match  # already 0-100

    total = (
        ats_component * w_ats +
        tech_component * w_tech_skills +
        soft_component * w_soft_skills +
        cert_component * w_certs +
        exp_component * w_experience +
        match_component * w_job_match
    ) / 100

    score = round(total, 1)

    # Determine level
    if score >= 85:
        level = "Ready to Apply"
        color = "#22c55e"  # green
    elif score >= 65:
        level = "Almost Ready"
        color = "#f59e0b"  # amber
    elif score >= 45:
        level = "Developing"
        color = "#f97316"  # orange
    else:
        level = "Needs Work"
        color = "#ef4444"  # red

    # Breakdown (max points for each component)
    breakdown = {
        f"ATS Score ({w_ats}%)": round(ats_component * w_ats / 100, 1),
        f"Tech Skills ({w_tech_skills}%)": round(tech_component * w_tech_skills / 100, 1),
        f"Soft Skills ({w_soft_skills}%)": round(soft_component * w_soft_skills / 100, 1),
        f"Certifications ({w_certs}%)": round(cert_component * w_certs / 100, 1),
        f"Experience ({w_experience}%)": round(exp_component * w_experience / 100, 1),
        f"Job Match ({w_job_match}%)": round(match_component * w_job_match / 100, 1),
    }

    # Suggestions
    suggestions = []
    if ats_score < 70:
        suggestions.append("Improve your resume ATS score: add keywords, bullet points, and quantifiable results.")
    if len(tech_skills) < 8:
        suggestions.append("Build more technical skills — aim for at least 10-12 on your resume.")
    if len(soft_skills) < 3:
        suggestions.append("Highlight soft skills like communication, teamwork, and problem-solving.")
    if not has_certifications:
        suggestions.append("Earn a certification (AWS, Google, Coursera) to boost credibility.")
    if years_experience < 2:
        suggestions.append("Gain more hands-on experience through internships, freelancing, or open-source contributions.")
    if avg_job_match < 50:
        suggestions.append("Tailor your resume to target roles; your skills may not align well with job requirements.")
    if not suggestions:
        suggestions.append("You're in great shape! Keep updating your skills and resume as you progress.")

    return {
        "score": score,
        "level": level,
        "level_color": color,
        "breakdown": breakdown,
        "suggestions": suggestions[:5],
    }