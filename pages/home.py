"""Home page — hero, feature overview, quick start."""

import streamlit as st


def show():
    # Hero section
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px 0">
        <div style="font-size:4rem;margin-bottom:12px">🚀</div>
        <h1 style="font-size:3rem;font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   background-clip:text;margin:0">Career Pilot AI</h1>
        <p style="font-size:1.2rem;color:#94a3b8;margin-top:12px;max-width:560px;margin-left:auto;margin-right:auto">
            Your AI-powered career navigator. Upload your resume and get instant 
            ATS scoring, skill extraction, real job matches, and a personalized learning roadmap.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # CTA
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Analyze My Resume →", use_container_width=True):
            st.session_state["current_page"] = "📄 Resume Analysis"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    st.markdown("""
    <h2 style="text-align:center;color:#f1f5f9;font-weight:700;margin-bottom:8px">
        Everything you need to land your next role
    </h2>
    <p style="text-align:center;color:#64748b;margin-bottom:32px">
        9 intelligent modules — all in one platform
    </p>
    """, unsafe_allow_html=True)

    features = [
        ("📄", "Resume Analyzer", "Extract text, detect sections, identify strengths and weaknesses in seconds.", "#6366f1"),
        ("🎯", "ATS Score Checker", "Get a 0–100 ATS score with a detailed section-by-section breakdown.", "#a855f7"),
        ("🧠", "Skill Extraction", "Automatically identify 50+ technical and soft skills from your resume.", "#ec4899"),
        ("💼", "Real Job Finder", "Match real job listings to your skills using live job APIs.", "#f59e0b"),
        ("📊", "Match Scoring", "See exactly which skills you have and which you're missing for each job.", "#22c55e"),
        ("🔍", "Skill Gap Analysis", "Compare your skills to your target role with radar charts.", "#3b82f6"),
        ("🗺️", "Learning Roadmap", "Get a step-by-step plan with free courses to close your skill gaps.", "#8b5cf6"),
        ("⭐", "Career Readiness", "A composite score across ATS, skills, experience, and job fit.", "#f97316"),
        ("📈", "Analytics Dashboard", "Visual overview of all your scores and metrics in one place.", "#06b6d4"),
    ]

    for i in range(0, len(features), 3):
        cols = st.columns(3)
        for col, feat in zip(cols, features[i:i+3]):
            icon, title, desc, color = feat
            with col:
                st.markdown(f"""
                <div class="cp-card" style="text-align:center;min-height:160px">
                    <div style="font-size:2.2rem;margin-bottom:10px">{icon}</div>
                    <div style="font-weight:700;color:{color};font-size:1rem;margin-bottom:8px">{title}</div>
                    <div style="color:#94a3b8;font-size:0.85rem;line-height:1.5">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # How it works
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h2 style="text-align:center;color:#f1f5f9;font-weight:700;margin-bottom:32px">
        How it works
    </h2>
    """, unsafe_allow_html=True)

    steps = [
        ("1", "Upload Resume", "PDF or DOCX — we extract everything automatically.", "#6366f1"),
        ("2", "Instant Analysis", "ATS score, skills, contact info in under 3 seconds.", "#a855f7"),
        ("3", "Find Jobs", "Real listings matched to your extracted skills.", "#22c55e"),
        ("4", "Close the Gap", "Get your personalized roadmap with free resources.", "#f59e0b"),
    ]

    step_cols = st.columns(4)
    for col, (num, title, desc, color) in zip(step_cols, steps):
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:20px 10px">
                <div style="width:48px;height:48px;border-radius:50%;
                            background:linear-gradient(135deg,{color}44,{color}22);
                            border:2px solid {color};display:flex;align-items:center;
                            justify-content:center;font-weight:800;font-size:1.2rem;
                            color:{color};margin:0 auto 12px auto">{num}</div>
                <div style="font-weight:700;color:#f1f5f9;margin-bottom:8px">{title}</div>
                <div style="color:#64748b;font-size:0.83rem;line-height:1.5">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Tech stack note
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="cp-card" style="text-align:center;background:rgba(99,102,241,0.05)">
        <div style="color:#64748b;font-size:0.85rem;margin-bottom:8px">POWERED BY</div>
        <div style="color:#94a3b8;font-size:0.9rem">
            🐍 Python &nbsp;·&nbsp; 🤖 Sentence Transformers &nbsp;·&nbsp; 
            📊 Plotly &nbsp;·&nbsp; 🔍 spaCy &nbsp;·&nbsp; ⚡ RapidFuzz &nbsp;·&nbsp;
            📦 Scikit-learn &nbsp;·&nbsp; 🌐 Adzuna API
        </div>
    </div>
    """, unsafe_allow_html=True)