"""
ats_scorer.py — heuristic ATS scoring engine that evaluates resume quality
based on sections, keywords, and formatting.
"""

from dataclasses import dataclass, field
from collections import Counter
import re


@dataclass
class ATSResult:
    total_score: float
    grade: str
    breakdown: dict  # section_name -> {"score": int, "max": int, "pct": float}
    strengths: list
    weaknesses: list
    suggestions: list


# Weights for each scoring category (must sum to 100)
WEIGHTS = {
    "Contact Information": 10,
    "Professional Summary": 5,
    "Skills": 20,
    "Experience": 25,
    "Education": 10,
    "Certifications": 5,
    "Projects": 5,
    "Formatting & Keywords": 20,
}

# Minimum words expected in each section
MIN_WORDS = {
    "summary": 10,
    "experience": 30,
    "skills": 5,
    "education": 5,
    "certifications": 3,
    "projects": 5,
}

# Action verbs list (same as resume_parser's but we can duplicate or import)
ACTION_VERBS_SET = {
    "accelerated", "accomplished", "achieved", "acquired", "adapted",
    "addressed", "administered", "advised", "allocated", "analyzed",
    "applied", "approved", "architected", "assembled", "assessed",
    "assisted", "attained", "audited", "automated", "built",
    "calculated", "captured", "championed", "collaborated", "combined",
    "communicated", "compared", "compiled", "completed", "composed",
    "conceived", "conducted", "configured", "consolidated", "constructed",
    "consulted", "contributed", "converted", "convinced", "coordinated",
    "created", "cultivated", "customized", "debugged", "decreased",
    "defined", "delegated", "delivered", "demonstrated", "deployed",
    "designed", "detected", "developed", "devised", "diagnosed",
    "directed", "discovered", "documented", "drafted", "earned",
    "edited", "educated", "eliminated", "enabled", "encouraged",
    "engineered", "enhanced", "established", "evaluated", "examined",
    "executed", "expanded", "expedited", "facilitated", "finalized",
    "forecasted", "formulated", "founded", "generated", "guided",
    "headed", "identified", "illustrated", "implemented", "improved",
    "increased", "influenced", "initiated", "innovated", "inspected",
    "installed", "instituted", "integrated", "interpreted", "interviewed",
    "introduced", "invented", "investigated", "launched", "led",
    "leveraged", "maintained", "managed", "marketed", "maximized",
    "measured", "mediated", "mentored", "merged", "migrated",
    "minimized", "modeled", "modernized", "modified", "monitored",
    "motivated", "negotiated", "operated", "optimized", "orchestrated",
    "organized", "overhauled", "oversaw", "performed", "persuaded",
    "planned", "prepared", "presented", "prioritized", "processed",
    "produced", "programmed", "promoted", "proposed", "provided",
    "published", "purchased", "recommended", "reconciled", "recorded",
    "redesigned", "reduced", "refactored", "refined", "released",
    "reorganized", "reported", "researched", "resolved", "restructured",
    "revamped", "reviewed", "revised", "scheduled", "secured",
    "selected", "simplified", "solved", "spearheaded", "standardized",
    "streamlined", "strengthened", "structured", "supervised", "supported",
    "surpassed", "synthesized", "tested", "trained", "transformed",
    "troubleshot", "unified", "updated", "upgraded", "validated",
    "visualized", "won", "wrote",
}


def run_ats_scoring(text: str, sections: dict, tech_skills: list) -> ATSResult:
    """
    Analyze resume text and sections to produce an ATS score and feedback.
    """
    # Initialize scores
    scores = {cat: 0 for cat in WEIGHTS}

    # 1. Contact Information (from text, not sections)
    contact_score = _score_contact(text)
    scores["Contact Information"] = contact_score

    # 2. Professional Summary
    summary_text = sections.get("summary", "")
    scores["Professional Summary"] = _score_summary(summary_text)

    # 3. Skills
    skills_text = sections.get("skills", "")
    scores["Skills"] = _score_skills(skills_text, tech_skills)

    # 4. Experience
    experience_text = sections.get("experience", "")
    scores["Experience"] = _score_experience(experience_text, text)

    # 5. Education
    education_text = sections.get("education", "")
    scores["Education"] = _score_section_presence(education_text, WEIGHTS["Education"])

    # 6. Certifications
    cert_text = sections.get("certifications", "")
    scores["Certifications"] = _score_section_presence(cert_text, WEIGHTS["Certifications"])

    # 7. Projects
    projects_text = sections.get("projects", "")
    scores["Projects"] = _score_section_presence(projects_text, WEIGHTS["Projects"])

    # 8. Formatting & Keywords (overall)
    scores["Formatting & Keywords"] = _score_formatting(text, tech_skills)

    # Compute total
    total_score = sum(scores.values())
    # Cap at 100
    total_score = min(total_score, 100.0)

    # Grade
    grade = _determine_grade(total_score)

    # Build breakdown dict with pct
    breakdown = {}
    for section, max_score in WEIGHTS.items():
        score_val = scores[section]
        pct = (score_val / max_score * 100) if max_score > 0 else 0
        breakdown[section] = {
            "score": score_val,
            "max": max_score,
            "pct": round(pct, 1),
        }

    # Strengths, weaknesses, suggestions
    strengths, weaknesses = _analyze_strengths_weaknesses(scores, WEIGHTS, sections, tech_skills)
    suggestions = _generate_suggestions(scores, sections, tech_skills)

    return ATSResult(
        total_score=round(total_score, 1),
        grade=grade,
        breakdown=breakdown,
        strengths=strengths,
        weaknesses=weaknesses,
        suggestions=suggestions,
    )


def _score_contact(text: str) -> float:
    """Score contact info (max 10 points) based on presence of email, phone, LinkedIn, GitHub, portfolio."""
    from utils.resume_parser import extract_contact_info
    contact = extract_contact_info(text)
    score = 0
    if contact.get("email"):
        score += 3
    if contact.get("phone"):
        score += 2
    if contact.get("linkedin"):
        score += 2
    if contact.get("github"):
        score += 2
    if contact.get("portfolio"):
        score += 1
    return min(score, WEIGHTS["Contact Information"])


def _score_summary(summary_text: str) -> float:
    """Score professional summary (max 5 points) based on length and keywords."""
    if not summary_text.strip():
        return 0
    words = summary_text.split()
    score = 1  # base for having it
    if len(words) >= 20:
        score += 1
    if len(words) >= 50:
        score += 1
    # Check for target role keywords or action verbs
    if any(verb in summary_text.lower() for verb in ["experienced", "driven", "passionate", "results-oriented"]):
        score += 1
    if len(words) >= 80:
        score += 1
    return min(score, WEIGHTS["Professional Summary"])


def _score_skills(skills_text: str, tech_skills: list) -> float:
    """Score skills section (max 20 points)."""
    score = 0
    # Presence of skills section text
    if skills_text.strip():
        score += 3
    # Number of tech skills extracted
    num_tech = len(tech_skills)
    if num_tech >= 5:
        score += 3
    if num_tech >= 10:
        score += 4
    if num_tech >= 15:
        score += 3
    # Skills section word count
    word_count = len(skills_text.split())
    if word_count >= 10:
        score += 2
    if word_count >= 20:
        score += 2
    if word_count >= 30:
        score += 3
    return min(score, WEIGHTS["Skills"])


def _score_experience(experience_text: str, full_text: str) -> float:
    """Score experience section (max 25 points)."""
    score = 0
    if not experience_text.strip():
        return 0

    # Presence and length
    word_count = len(experience_text.split())
    if word_count >= 30:
        score += 2
    if word_count >= 80:
        score += 3
    if word_count >= 150:
        score += 2

    # Quantified achievements (use same detection as parser)
    from utils.resume_parser import detect_quantified_achievements
    achievements = detect_quantified_achievements(experience_text)
    if achievements:
        num = len(achievements)
        score += min(num * 2, 6)  # up to 6 points

    # Action verbs
    from utils.resume_parser import detect_action_verbs
    verbs = detect_action_verbs(experience_text)
    if verbs:
        num_verbs = len(verbs)
        if num_verbs >= 3:
            score += 2
        if num_verbs >= 6:
            score += 3
        if num_verbs >= 10:
            score += 2

    # Use of bullet points (indicator of good formatting)
    if "•" in experience_text or "- " in experience_text or "* " in experience_text:
        score += 2

    # Estimated years (from full text or experience)
    from utils.resume_parser import estimate_years_experience
    years = estimate_years_experience(full_text)
    if years >= 1:
        score += 2
    if years >= 5:
        score += 2

    return min(score, WEIGHTS["Experience"])


def _score_section_presence(section_text: str, max_score: float) -> float:
    """Generic section scorer based on presence and word count."""
    if not section_text.strip():
        return 0
    words = len(section_text.split())
    if words >= 5:
        return max_score * 0.5
    elif words >= 10:
        return max_score * 0.8
    else:
        return max_score * 1.0 if words >= 15 else max_score * 0.3


def _score_formatting(text: str, tech_skills: list) -> float:
    """Evaluate overall formatting, keywords, and density (max 20 points)."""
    score = 0
    lines = text.splitlines()
    total_words = len(text.split())

    # Overall length
    if 200 <= total_words <= 800:
        score += 3
    elif total_words > 800:
        score += 2
    else:
        score += 1

    # Use of bullet points
    bullet_lines = sum(1 for line in lines if line.strip().startswith(("•", "-", "*")))
    if bullet_lines >= 5:
        score += 2
    if bullet_lines >= 10:
        score += 2

    # Action verbs in full text
    from utils.resume_parser import detect_action_verbs
    verbs = detect_action_verbs(text)
    if verbs:
        num_verbs = len(verbs)
        if num_verbs >= 5:
            score += 2
        if num_verbs >= 10:
            score += 3

    # Quantified achievements in full text
    from utils.resume_parser import detect_quantified_achievements
    achievements = detect_quantified_achievements(text)
    if achievements:
        num_ach = len(achievements)
        if num_ach >= 2:
            score += 2
        if num_ach >= 5:
            score += 3

    # Keyword variety (unique words ratio)
    words = re.findall(r'\b\w+\b', text.lower())
    unique_ratio = len(set(words)) / max(1, len(words))
    if unique_ratio > 0.6:
        score += 2

    return min(score, WEIGHTS["Formatting & Keywords"])


def _determine_grade(total_score: float) -> str:
    if total_score >= 85:
        return "Excellent"
    elif total_score >= 70:
        return "Good"
    elif total_score >= 50:
        return "Fair"
    else:
        return "Poor"


def _analyze_strengths_weaknesses(scores, weights, sections, tech_skills):
    strengths = []
    weaknesses = []

    # Contact
    if scores["Contact Information"] >= 8:
        strengths.append("Complete contact information with LinkedIn and GitHub.")
    elif scores["Contact Information"] <= 3:
        weaknesses.append("Missing critical contact details (email, phone, LinkedIn).")

    # Summary
    if scores["Professional Summary"] >= 4:
        strengths.append("Well-written professional summary.")
    elif scores["Professional Summary"] <= 1 and sections.get("summary", "").strip():
        weaknesses.append("Professional summary is too short or generic.")

    # Skills
    if scores["Skills"] >= 16:
        strengths.append("Comprehensive skills section with many relevant technologies.")
    elif scores["Skills"] <= 5:
        weaknesses.append("Weak or missing skills section. List your technical and soft skills.")

    # Experience
    if scores["Experience"] >= 20:
        strengths.append("Strong experience section with quantified achievements.")
    elif scores["Experience"] <= 8:
        weaknesses.append("Experience section lacks detail, metrics, or action verbs.")

    # Education
    if scores["Education"] >= 8:
        strengths.append("Education section present and detailed.")
    elif scores["Education"] == 0:
        weaknesses.append("No education section found. Add your degrees/certificates.")

    # Certifications
    if scores["Certifications"] >= 4:
        strengths.append("Certifications included, adding credibility.")
    elif scores["Certifications"] == 0 and "certifications" not in sections:
        weaknesses.append("No certifications listed. Add any relevant certifications.")

    # Formatting
    if scores["Formatting & Keywords"] >= 16:
        strengths.append("Excellent formatting with bullet points, action verbs, and metrics.")
    elif scores["Formatting & Keywords"] <= 7:
        weaknesses.append("Poor formatting. Use bullet points, action verbs, and quantify results.")

    # Extra: tech skill count
    if len(tech_skills) >= 10:
        strengths.append("High number of relevant technical skills detected.")
    elif len(tech_skills) < 5:
        weaknesses.append("Very few technical skills detected; your resume may not pass ATS filters.")

    # If no strengths found, add a default
    if not strengths:
        strengths.append("Resume has basic structure — improve content to stand out.")
    if not weaknesses:
        weaknesses.append("No major weaknesses found! Keep refining to maintain a top score.")

    return strengths, weaknesses


def _generate_suggestions(scores, sections, tech_skills):
    suggestions = []

    # Contact
    if scores["Contact Information"] < 8:
        suggestions.append("Add a professional email, phone number, and LinkedIn profile to your contact section.")
    if scores["Contact Information"] < 5:
        suggestions.append("Include links to your GitHub and portfolio/website for technical roles.")

    # Summary
    if scores["Professional Summary"] < 3:
        suggestions.append("Craft a 3-4 line professional summary highlighting your key strengths and target role.")
    elif scores["Professional Summary"] < 5:
        suggestions.append("Expand your summary with quantifiable achievements and specific skills.")

    # Skills
    if scores["Skills"] < 10:
        suggestions.append("Create a dedicated 'Skills' section with bullet points listing technical tools and soft skills.")
    elif len(tech_skills) < 8:
        suggestions.append("List more technical skills (programming languages, frameworks, tools) to improve ATS matching.")

    # Experience
    if scores["Experience"] < 15:
        suggestions.append("Use bullet points with strong action verbs (e.g., 'Developed', 'Led', 'Optimized') and quantify results (e.g., 'Increased efficiency by 20%').")
    if scores["Experience"] < 10:
        suggestions.append("Include any internships, volunteer work, or projects to strengthen your experience section.")

    # Education
    if scores["Education"] == 0:
        suggestions.append("Add an education section with your degree(s), institution, and graduation year.")
    elif scores["Education"] < 5:
        suggestions.append("Expand education details: include relevant coursework, GPA (if >3.5), or honors.")

    # Certifications
    if scores["Certifications"] == 0:
        suggestions.append("List any certifications (e.g., AWS, Google, Microsoft, Coursera) to boost credibility.")

    # Formatting
    if scores["Formatting & Keywords"] < 12:
        suggestions.append("Use consistent formatting: bullet points, clear section headings, and a maximum of 2 pages.")
    if scores["Formatting & Keywords"] < 15:
        suggestions.append("Add more quantifiable achievements and metrics to demonstrate impact.")

    # Generic if few suggestions
    if len(suggestions) < 3:
        suggestions.append("Keep your resume concise (1-2 pages) and tailor it to each job description with relevant keywords.")

    return suggestions[:8]  # Return top 8