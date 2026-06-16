"""
resume_parser.py — extract text, sections, contact info, experience, action verbs,
and quantified achievements from raw resume text.
"""

import re
import io
import pdfplumber
from docx import Document
from collections import OrderedDict
import phonenumbers


# ── Text Extraction ────────────────────────────────────────────────────────────
def extract_text(file_bytes: bytes, ext: str) -> str:
    """Extract full text from PDF or DOCX file bytes."""
    if ext == "pdf":
        return _extract_text_pdf(file_bytes)
    elif ext == "docx":
        return _extract_text_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def _extract_text_pdf(file_bytes: bytes) -> str:
    text = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def _extract_text_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [para.text for para in doc.paragraphs]
    return "\n".join(paragraphs)


# ── Section Detection ──────────────────────────────────────────────────────────
SECTION_KEYWORDS = {
    "summary": ["summary", "profile", "about me", "objective", "professional summary"],
    "experience": ["experience", "work experience", "employment", "work history", "professional experience"],
    "education": ["education", "academic background", "academic history", "qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "key skills", "technologies"],
    "projects": ["projects", "project experience", "key projects", "portfolio"],
    "certifications": ["certifications", "certificates", "licenses", "accreditations"],
    "contact": ["contact", "personal details", "contact information"],
    "awards": ["awards", "honors", "achievements"],
    "languages": ["languages", "language proficiency"],
}


def _normalize_line(line: str) -> str:
    return line.strip().lower().rstrip(":")


def detect_sections(text: str) -> dict:
    """
    Split the resume text into named sections.
    Returns a dict mapping section name -> section text.
    """
    lines = text.splitlines()
    sections = OrderedDict()
    current_section = "other"
    current_text = []

    # Find all section start indices
    section_starts = []
    for i, line in enumerate(lines):
        clean = _normalize_line(line)
        for sec_name, keywords in SECTION_KEYWORDS.items():
            if clean in keywords:
                section_starts.append((i, sec_name))
                break

    # Sort by line index
    section_starts.sort(key=lambda x: x[0])

    if not section_starts:
        return {"other": text}

    start_idx, first_sec = section_starts[0]
    if start_idx > 0:
        sections["header"] = "\n".join(lines[:start_idx]).strip()

    for i, (line_idx, sec_name) in enumerate(section_starts):
        content_start = line_idx + 1
        if i + 1 < len(section_starts):
            content_end = section_starts[i + 1][0]
        else:
            content_end = len(lines)
        section_text = "\n".join(lines[content_start:content_end]).strip()
        sections[sec_name] = section_text

    return sections


# ── Contact Info Extraction ────────────────────────────────────────────────────
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
# LinkedIn, GitHub, Portfolio patterns
LINKEDIN_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?", re.IGNORECASE
)
GITHUB_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?", re.IGNORECASE
)
PORTFOLIO_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.(?:com|io|me|net|org|dev)/[^\s]*",
    re.IGNORECASE,
)


def _extract_phone_numbers(text: str):
    """Use phonenumbers library to find valid phone numbers."""
    possible = []
    for match in phonenumbers.PhoneNumberMatcher(text, "US"):  # try US as default region
        possible.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
    # Also try without region (slower but catches more)
    if not possible:
        for match in phonenumbers.PhoneNumberMatcher(text, None):
            possible.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
    # Fallback regex if phonenumbers fails
    if not possible:
        # Simple pattern: digits with separators, min 7 digits
        phone_regex = re.compile(
            r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{0,4}"
        )
        matches = phone_regex.findall(text)
        possible = [m.strip() for m in matches if len(re.sub(r"\D", "", m)) >= 7]
    return possible


def extract_contact_info(text: str) -> dict:
    """
    Extract email, phone, LinkedIn, GitHub, and portfolio URL.
    Returns dict with keys: email, phone, linkedin, github, portfolio.
    Values are None if not found.
    """
    contact = {
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "portfolio": None,
    }

    # Email (first match)
    emails = EMAIL_REGEX.findall(text)
    if emails:
        contact["email"] = emails[0]

    # Phone (best match using phonenumbers)
    phones = _extract_phone_numbers(text)
    if phones:
        contact["phone"] = phones[0]  # first valid number

    # LinkedIn
    linkedin_matches = LINKEDIN_REGEX.findall(text)
    if linkedin_matches:
        url = linkedin_matches[0]
        if not url.startswith("http"):
            url = "https://" + url
        contact["linkedin"] = url

    # GitHub
    github_matches = GITHUB_REGEX.findall(text)
    if github_matches:
        url = github_matches[0]
        if not url.startswith("http"):
            url = "https://" + url
        contact["github"] = url

    # Portfolio (exclude LinkedIn/GitHub/email)
    all_urls = re.findall(PORTFOLIO_REGEX, text)
    for url in all_urls:
        full_url = url.strip()
        if "linkedin.com" in full_url or "github.com" in full_url:
            continue
        if "@" in full_url:
            continue
        contact["portfolio"] = full_url
        break

    return contact


# ── Years of Experience Estimation ──────────────────────────────────────────────
EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*(?:years|yrs)\s*(?:of\s*)?experience",
    r"over\s*(\d+)\s*(?:years|yrs)",
    r"more than\s*(\d+)\s*(?:years|yrs)",
    r"(\d+)\s*(?:years|yrs)\s*experience",
    r"experience\s*:\s*(\d+)\s*(?:years|yrs)",
]


def estimate_years_experience(text: str) -> int:
    """Heuristically estimate years of professional experience."""
    text_lower = text.lower()

    # Try explicit statements
    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1))

    # Fallback: find date ranges like "2018 – 2023" in entire resume
    years = re.findall(r"\b(19|20)\d{2}\b", text)
    if len(years) >= 2:
        years_int = sorted(int(y) for y in years)
        span = years_int[-1] - years_int[0]
        if 1 <= span <= 50:
            return span

    return 0


# ── Action Verb Detection ──────────────────────────────────────────────────────
ACTION_VERBS = {
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


def detect_action_verbs(text: str) -> list:
    """
    Find action verbs that appear as the first word in bullet points
    or anywhere in the text. Returns a list of unique verbs found.
    """
    found = set()
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Remove common bullet characters
        for bullet in ["•", "-", "*", ">", "‣", "◦"]:
            if stripped.startswith(bullet):
                stripped = stripped[1:].strip()
                break
        # First word
        first_word = re.split(r"\s+", stripped)[0].lower().rstrip(",.;:")
        if first_word in ACTION_VERBS:
            found.add(first_word)

    # Also check globally for any action verbs not caught as first word
    words = set(re.findall(r"\b\w+\b", text.lower()))
    found.update(words.intersection(ACTION_VERBS))

    return sorted(found)


# ── Quantified Achievements Detection ───────────────────────────────────────────
QUANT_PATTERNS = [
    r"(?:increased?|decreased?|reduced?|improved?|boosted?|grew?|raised?|cut|saved?|generated?|delivered?|achieved?|earned?|won|secured?|managed|led|supervised|trained|mentored|coordinated|executed|completed|finished|processed|handled)\s+.+?(?:\d+%|\$\s*\d+|\d+\s*(?:users?|clients?|members?|employees?|partners?|contracts?|projects?|products?|features?|lines of code|bugs|issues|tickets|servers?|databases?|applications?|sites?|pages?|apps?|transactions?|orders?|customers?|deals?|dollars?|million|billion))",
    r"(?:team of|budget of|revenue of|worth of|savings of)\s+\d+",
    r"\d+\s*%\s*(?:increase|decrease|reduction|improvement|growth|savings|boost|gain|drop|rise|fall)",
    r"\$\s*\d+\s*(?:million|billion|thousand|k|M|B)?\s*(?:revenue|savings|budget|income|profit|sales|funding|investment|worth)",
]


def detect_quantified_achievements(text: str) -> list:
    """
    Extract bullet points or sentences that contain quantifiable results.
    Returns list of strings.
    """
    achievements = []
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        for pattern in QUANT_PATTERNS:
            if re.search(pattern, stripped, re.IGNORECASE):
                achievements.append(stripped)
                break
    return achievements