"""
skill_extractor.py — extract technical and soft skills from resume text
using SkillNER (preferred) or a static taxonomy as fallback.
"""

import re
import logging
from data.skills_database import (
    TECH_SKILLS_LIST,
    SOFT_SKILLS_LIST,
    SKILL_NORMALIZATION_MAP,
)

# Try to import SkillNER (optional advanced extraction)
try:
    from skillNer.general_params import SKILL_DB
    from skillNer.skill_extractor_class import SkillExtractor
    import spacy
    # Load spaCy model (make sure en_core_web_trf or en_core_web_lg is installed)
    nlp = spacy.load("en_core_web_trf")  # or "en_core_web_lg" if trf not available
    skill_extractor = SkillExtractor(nlp, SKILL_DB, spacy.load("en_core_web_trf").get_pipe("transformer") if "transformer" in nlp.pipe_names else None)
    SKILLNER_AVAILABLE = True
except ImportError:
    SKILLNER_AVAILABLE = False
    logging.warning("SkillNER not installed. Falling back to static skill list.")


def _normalize_skill(skill: str) -> str:
    """Normalize a skill name using the normalization map."""
    skill_lower = skill.strip().lower()
    # Direct lookup
    if skill_lower in SKILL_NORMALIZATION_MAP:
        return SKILL_NORMALIZATION_MAP[skill_lower]
    # Also try removing trailing 's' (e.g., "Dockers" -> "Docker")
    if skill_lower.endswith("s"):
        singular = skill_lower.rstrip("s")
        if singular in SKILL_NORMALIZATION_MAP:
            return SKILL_NORMALIZATION_MAP[singular]
    # Capitalize first letter of each word as fallback
    return skill.strip().title()


def _extract_static(text: str) -> tuple:
    """Fallback extraction using regex on static skill lists."""
    def _build_pattern(skills):
        sorted_skills = sorted(skills, key=lambda s: (-len(s), s))
        escaped = [re.escape(s) for s in sorted_skills]
        pattern = r"\b(?:" + "|".join(escaped) + r")\b"
        return re.compile(pattern, re.IGNORECASE)

    tech_pattern = _build_pattern(TECH_SKILLS_LIST)
    soft_pattern = _build_pattern(SOFT_SKILLS_LIST)

    tech_raw = set(tech_pattern.findall(text))
    soft_raw = set(soft_pattern.findall(text))

    tech_norm = []
    for skill in tech_raw:
        norm = _normalize_skill(skill)
        if norm not in tech_norm:
            tech_norm.append(norm)

    soft_norm = []
    for skill in soft_raw:
        norm = _normalize_skill(skill)
        if norm not in soft_norm and norm not in tech_norm:
            soft_norm.append(norm)

    return tech_norm, soft_norm


def extract_skills(text: str) -> tuple:
    """
    Extract technical and soft skills from resume text.
    Returns (tech_skills, soft_skills) as lists of normalized skill names.
    """
    if SKILLNER_AVAILABLE:
        try:
            # Use SkillNER
            doc = nlp(text)
            annotations = skill_extractor.annotate(doc)
            # Extract full matches (skill name) and normalize
            tech = set()
            soft = set()
            for match in annotations["results"]["full_matches"]:
                skill_name = match["skill_name"]
                norm = _normalize_skill(skill_name)
                # Determine if tech or soft based on our lists
                if skill_name.lower() in {s.lower() for s in TECH_SKILLS_LIST}:
                    tech.add(norm)
                elif skill_name.lower() in {s.lower() for s in SOFT_SKILLS_LIST}:
                    soft.add(norm)
                else:
                    # If unknown, put in tech (most skills are tech)
                    tech.add(norm)
            tech_skills = list(tech)
            soft_skills = [s for s in soft if s not in tech]  # avoid duplicates
            if not tech_skills:  # fallback if SkillNER returned empty
                return _extract_static(text)
            return tech_skills, soft_skills
        except Exception as e:
            logging.error(f"SkillNER extraction failed: {e}")
            return _extract_static(text)
    else:
        return _extract_static(text)