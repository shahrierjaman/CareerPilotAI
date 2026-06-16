"""
Career Pilot AI — Main Application Entry Point
"""

import streamlit as st
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

# ── Page Config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="Career Pilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Global CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Root theme */
:root {
    --bg-primary: #0f0f1a;
    --bg-secondary: #1a1a2e;
    --bg-card: #16213e;
    --accent-primary: #6366f1;   /* Indigo */
    --accent-secondary: #a855f7; /* Purple */
    --accent-green: #22c55e;
    --accent-amber: #f59e0b;
    --accent-red: #ef4444;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border: #1e293b;
    --gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.stApp {
    background: var(--bg-primary);
    color: var(--text-primary);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text-primary) !important;
}

/* Radio buttons as nav */
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.15s;
    font-weight: 500;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(99, 102, 241, 0.15);
}

/* Cards */
.cp-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    transition: border-color 0.2s;
}

.cp-card:hover {
    border-color: var(--accent-primary);
}

/* Metric badge */
.cp-metric {
    background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.15) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.cp-metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.cp-metric-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}

/* Tags / pills */
.cp-tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 3px;
}

.cp-tag-tech {
    background: rgba(99,102,241,0.2);
    color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.3);
}

.cp-tag-soft {
    background: rgba(168,85,247,0.2);
    color: #d8b4fe;
    border: 1px solid rgba(168,85,247,0.3);
}

.cp-tag-missing {
    background: rgba(239,68,68,0.15);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,0.3);
}

.cp-tag-match {
    background: rgba(34,197,94,0.15);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.3);
}

/* Section headers */
.cp-section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Job cards */
.cp-job-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.2s;
}

.cp-job-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}

/* Progress bar override */
.stProgress .st-bo {
    background: var(--gradient);
}

/* Buttons */
.stButton > button {
    background: var(--gradient);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    transition: opacity 0.2s;
}

.stButton > button:hover {
    opacity: 0.85;
    border: none;
}

/* Upload area */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(99,102,241,0.4) !important;
    border-radius: 14px !important;
    background: rgba(99,102,241,0.05) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
}

/* Alert boxes */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 10px;
}

/* Selectbox */
[data-baseweb="select"] {
    background: var(--bg-card) !important;
}

/* Tabs */
.stTabs [role="tab"] {
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    border-bottom: 2px solid var(--accent-primary);
}

/* Step card for learning path */
.cp-step-card {
    background: var(--bg-card);
    border-left: 4px solid var(--accent-primary);
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 12px;
}

/* Logo header */
.cp-logo {
    text-align: center;
    padding: 20px 0 10px 0;
}

.cp-logo-title {
    font-size: 1.5rem;
    font-weight: 800;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Score ring */
.cp-score-ring {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: 800;
    margin: 0 auto;
}

code, .cp-mono {
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ── Session State Init ─────────────────────────────────────────────────────────
defaults = {
    "resume_text": None,
    "resume_sections": {},
    "tech_skills": [],
    "soft_skills": [],
    "ats_result": None,
    "contact_info": {},
    "years_exp": 0,
    "jobs": [],
    "job_matches": [],
    "gap_data": None,
    "learning_path": [],
    "career_readiness": None,
    "current_page": "🏠 Home",
    "target_role": "Data Scientist",
    "api_keys": {
        "adzuna_app_id": "",
        "adzuna_app_key": "",
        "jooble_key": "",
    },
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar Navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="cp-logo">
        <div style="font-size:2.5rem">🚀</div>
        <div class="cp-logo-title">Career Pilot AI</div>
        <div style="color:#64748b;font-size:0.75rem;margin-top:4px">Your AI Career Navigator</div>
    </div>
    <hr style="border-color:#1e293b;margin:10px 0 20px 0">
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=[
            "🏠 Home",
            "📄 Resume Analysis",
            "💼 Job Recommendations",
            "🔍 Skill Gap Analysis",
            "🗺️ Learning Roadmap",
            "📊 Dashboard",
            "⚙️ Settings",
        ],
        label_visibility="collapsed",
    )
    st.session_state["current_page"] = page

    # Resume status indicator
    if st.session_state.get("resume_text"):
        st.markdown("---")
        st.markdown("**Resume Status**")
        tech_count = len(st.session_state.get("tech_skills", []))
        ats_score = st.session_state.get("ats_result")
        ats_val = ats_score.total_score if ats_score else 0

        st.markdown(f"""
        <div style="font-size:0.82rem;color:#94a3b8;line-height:2">
            ✅ Resume loaded<br>
            🎯 ATS Score: <b style="color:#6366f1">{ats_val:.0f}/100</b><br>
            💡 Skills: <b style="color:#a855f7">{tech_count} extracted</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.82rem;color:#64748b">
            ⬆️ Upload your resume in<br><b>Resume Analysis</b> to begin
        </div>
        """, unsafe_allow_html=True)

# ── Route to pages ─────────────────────────────────────────────────────────────
if page == "🏠 Home":
    from pages.home import show
    show()
elif page == "📄 Resume Analysis":
    from pages.resume_analysis import show
    show()
elif page == "💼 Job Recommendations":
    from pages.job_recommendations import show
    show()
elif page == "🔍 Skill Gap Analysis":
    from pages.skill_gap import show
    show()
elif page == "🗺️ Learning Roadmap":
    from pages.learning_roadmap import show
    show()
elif page == "📊 Dashboard":
    from pages.dashboard import show
    show()
elif page == "⚙️ Settings":
    from pages.settings import show
    show()