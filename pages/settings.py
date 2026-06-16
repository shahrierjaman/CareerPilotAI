"""Settings Page — API keys, preferences, session management."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def show():
    st.markdown("""
    <h1 style="font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               background-clip:text">⚙️ Settings</h1>
    <p style="color:#94a3b8;margin-top:-8px">Configure API keys and preferences for Career Pilot AI.</p>
    """, unsafe_allow_html=True)

    api_keys = st.session_state.get("api_keys", {})

    # ── API Keys Section ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="cp-card">
        <div class="cp-section-title">🔑 Job API Keys</div>
        <p style="color:#64748b;font-size:0.88rem;margin-bottom:0">
            Add free API keys to fetch real job listings. Without keys, demo jobs are shown.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Adzuna
    with st.expander("🔷 Adzuna API (Recommended — 250 free calls/month)", expanded=True):
        st.markdown("""
        <div style="color:#94a3b8;font-size:0.85rem;margin-bottom:12px">
            1. Register free at <a href="https://developer.adzuna.com/signup" target="_blank"
               style="color:#6366f1">developer.adzuna.com/signup</a><br>
            2. Create an app and copy your <b>App ID</b> and <b>App Key</b><br>
            3. Paste them below
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            adzuna_id = st.text_input(
                "Adzuna App ID",
                value=api_keys.get("adzuna_app_id", ""),
                type="password",
                placeholder="e.g. a1b2c3d4",
            )
        with col2:
            adzuna_key = st.text_input(
                "Adzuna App Key",
                value=api_keys.get("adzuna_app_key", ""),
                type="password",
                placeholder="e.g. abc123xyz...",
            )

    # Jooble
    with st.expander("🔶 Jooble API (Fallback — free tier available)"):
        st.markdown("""
        <div style="color:#94a3b8;font-size:0.85rem;margin-bottom:12px">
            1. Request a free API key at <a href="https://jooble.org/api/about" target="_blank"
               style="color:#6366f1">jooble.org/api/about</a><br>
            2. Paste your key below — used as fallback when Adzuna returns no results
        </div>
        """, unsafe_allow_html=True)
        jooble_key = st.text_input(
            "Jooble API Key",
            value=api_keys.get("jooble_key", ""),
            type="password",
            placeholder="e.g. abc123def456...",
        )

    # JSearch (RapidAPI)
    with st.expander("🟢 JSearch API (via RapidAPI — 100 free calls/month)"):
        st.markdown("""
        <div style="color:#94a3b8;font-size:0.85rem;margin-bottom:12px">
            1. Sign up free at <a href="https://rapidapi.com/letscrape-6bRBa3QguO6/api/jsearch" target="_blank"
               style="color:#6366f1">RapidAPI (JSearch)</a><br>
            2. Subscribe to the <b>free Basic plan</b> (100 requests/month)<br>
            3. Copy your <b>X-RapidAPI-Key</b> and paste it below
        </div>
        """, unsafe_allow_html=True)
        jsearch_key = st.text_input(
            "JSearch API Key (X-RapidAPI-Key)",
            value=api_keys.get("jsearch_key", ""),
            type="password",
            placeholder="e.g. 1a2b3c4d5e...",
        )

    if st.button("💾 Save API Keys", use_container_width=True):
        st.session_state["api_keys"] = {
            "adzuna_app_id": adzuna_id.strip(),
            "adzuna_app_key": adzuna_key.strip(),
            "jooble_key": jooble_key.strip(),
            "jsearch_key": jsearch_key.strip(),
        }
        st.session_state["keys_saved"] = True
        st.success("✅ API keys saved for this session!")
        st.rerun()

    # Show persistent status if keys were saved
    if st.session_state.get("keys_saved"):
        st.info("🔑 API keys are active — real job search enabled!")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Default Preferences ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="cp-card">
        <div class="cp-section-title">🎯 Default Preferences</div>
    </div>
    """, unsafe_allow_html=True)

    from services.career_engine import get_available_roles
    from services.job_recommender import COUNTRY_MAP
    roles = get_available_roles()

    col1, col2 = st.columns(2)
    with col1:
        default_role = st.selectbox(
            "Default Target Role",
            roles,
            index=roles.index(st.session_state.get("target_role", roles[0])),
        )
    with col2:
        default_country = st.selectbox(
            "Default Job Country",
            list(COUNTRY_MAP.keys()),
            index=0,
        )

    if st.button("💾 Save Preferences"):
        st.session_state["target_role"] = default_role
        st.session_state["default_country"] = default_country
        st.success("✅ Preferences saved!")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Session / Reset ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="cp-card" style="border-color:rgba(239,68,68,0.3)">
        <div class="cp-section-title" style="color:#ef4444">🗑️ Session Management</div>
        <p style="color:#64748b;font-size:0.85rem">Clear all uploaded resume data and results from the current session.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🗑️ Clear Session Data", type="secondary", use_container_width=True):
            keys_to_clear = [
                "resume_text", "resume_sections", "tech_skills", "soft_skills",
                "ats_result", "contact_info", "years_exp", "jobs", "job_matches",
                "gap_data", "learning_path", "career_readiness",
            ]
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.success("✅ Session cleared. Upload a new resume to start fresh.")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── About Section ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="cp-card" style="background:rgba(99,102,241,0.05)">
        <div class="cp-section-title">ℹ️ About Career Pilot AI</div>
        <div style="color:#94a3b8;font-size:0.88rem;line-height:1.8">
            <b style="color:#f1f5f9">Career Pilot AI</b> is an open-source AI-powered career assistant.<br><br>
            <b style="color:#a5b4fc">Tech Stack:</b>
            Python · Streamlit · spaCy · Sentence Transformers · RapidFuzz ·
            Scikit-learn · Plotly · Adzuna API · Jooble API · JSearch API<br><br>
            <b style="color:#a5b4fc">Data Sources:</b>
            ESCO Skills Framework · O*NET Skills Database · Adzuna Jobs API<br><br>
            <b style="color:#a5b4fc">Version:</b> 1.0.0 &nbsp;·&nbsp;
            <b style="color:#a5b4fc">License:</b> MIT<br><br>
            <a href="https://github.com" target="_blank" style="color:#6366f1">⭐ Star on GitHub</a>
            &nbsp;&nbsp;
            <a href="https://linkedin.com" target="_blank" style="color:#6366f1">🔗 Connect on LinkedIn</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Status Panel ──────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Session Status")

    status_items = [
        ("Resume Loaded", bool(st.session_state.get("resume_text"))),
        ("Skills Extracted", bool(st.session_state.get("tech_skills"))),
        ("ATS Score Computed", bool(st.session_state.get("ats_result"))),
        ("Jobs Fetched", bool(st.session_state.get("job_matches"))),
        ("Gap Analysis Done", bool(st.session_state.get("gap_data"))),
        ("Learning Path Generated", bool(st.session_state.get("learning_path"))),
        ("Adzuna API Key Set", bool(st.session_state.get("api_keys", {}).get("adzuna_app_id"))),
        ("Jooble API Key Set", bool(st.session_state.get("api_keys", {}).get("jooble_key"))),
        ("JSearch API Key Set", bool(st.session_state.get("api_keys", {}).get("jsearch_key"))),
    ]

    cols = st.columns(4)
    for i, (label, status) in enumerate(status_items):
        with cols[i % 4]:
            icon = "✅" if status else "⭕"
            color = "#22c55e" if status else "#64748b"
            st.markdown(f"""
            <div style="padding:10px 14px;background:#16213e;border-radius:10px;
                        border:1px solid {'rgba(34,197,94,0.25)' if status else '#1e293b'};
                        margin-bottom:10px">
                <span style="font-size:1rem">{icon}</span>
                <span style="color:{color};font-size:0.82rem;margin-left:8px;font-weight:500">{label}</span>
            </div>
            """, unsafe_allow_html=True)