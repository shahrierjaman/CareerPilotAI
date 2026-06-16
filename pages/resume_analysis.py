"""Resume Analysis Page — upload, parse, ATS score, skill extraction."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.resume_parser import (
    extract_text, detect_sections, extract_contact_info,
    estimate_years_experience, detect_action_verbs, detect_quantified_achievements,
)
from utils.skill_extractor import extract_skills
from services.ats_scorer import run_ats_scoring


def show():
    st.markdown("""
    <h1 style="font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               background-clip:text">📄 Resume Analyzer</h1>
    <p style="color:#94a3b8;margin-top:-8px">Upload your resume to get instant ATS scoring, skill extraction, and improvement suggestions.</p>
    """, unsafe_allow_html=True)

    # ── Upload ──────────────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Drop your resume here — PDF or DOCX",
        type=["pdf", "docx"],
        help="Supports PDF and Microsoft Word (.docx) formats",
    )

    if uploaded is not None:
        file_bytes = uploaded.read()
        ext = uploaded.name.split(".")[-1].lower()

        with st.spinner("🔍 Parsing your resume..."):
            text = extract_text(file_bytes, ext)

        if not text or len(text.strip()) < 50:
            st.error("⚠️ Could not extract text. Please ensure your resume is not image-only or password-protected.")
            return

        # Run full pipeline
        with st.spinner("🧠 Running analysis pipeline..."):
            sections = detect_sections(text)
            contact_info = extract_contact_info(text)
            tech_skills, soft_skills = extract_skills(text)
            ats_result = run_ats_scoring(text, sections, tech_skills)
            years_exp = estimate_years_experience(text) or 0
            action_verbs = detect_action_verbs(text)
            achievements = detect_quantified_achievements(text)

        # Save to session state
        st.session_state["resume_text"] = text
        st.session_state["resume_sections"] = sections
        st.session_state["tech_skills"] = tech_skills
        st.session_state["soft_skills"] = soft_skills
        st.session_state["ats_result"] = ats_result
        st.session_state["contact_info"] = contact_info
        st.session_state["years_exp"] = years_exp

        st.success(f"✅ **{uploaded.name}** analyzed successfully!")
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Top-Level Metrics ───────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            ("🎯 ATS Score", f"{ats_result.total_score:.0f}/100", ats_result.grade),
            ("💡 Tech Skills", str(len(tech_skills)), "Skills extracted"),
            ("🤝 Soft Skills", str(len(soft_skills)), "Soft skills found"),
            ("📅 Experience", f"~{years_exp} yrs" if years_exp else "Not detected", "Estimated"),
        ]
        for col, (label, value, sub) in zip([c1, c2, c3, c4], metrics):
            with col:
                st.markdown(f"""
                <div class="cp-metric">
                    <div style="font-size:0.78rem;color:#94a3b8;text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:4px">{label}</div>
                    <div class="cp-metric-value">{value}</div>
                    <div style="font-size:0.78rem;color:#64748b;margin-top:4px">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tabs ────────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 ATS Score", "💡 Skills", "📋 Sections", "📝 Content Quality", "👤 Contact Info"
        ])

        # TAB 1: ATS Score
        with tab1:
            _render_ats(ats_result)

        # TAB 2: Skills
        with tab2:
            _render_skills(tech_skills, soft_skills)

        # TAB 3: Sections
        with tab3:
            _render_sections(sections)

        # TAB 4: Content Quality
        with tab4:
            _render_quality(text, action_verbs, achievements)

        # TAB 5: Contact
        with tab5:
            _render_contact(contact_info)

    else:
        # Empty state
        if st.session_state.get("resume_text"):
            st.info("✅ A resume is already loaded. Upload a new one to replace it, or navigate to other sections.")
            _show_current_summary()
        else:
            _show_placeholder()


def _render_ats(ats_result):
    import plotly.graph_objects as go

    col1, col2 = st.columns([1, 2])

    with col1:
        score = ats_result.total_score
        color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100", "font": {"size": 28, "color": "#f1f5f9"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748b", "tickfont": {"color": "#64748b"}},
                "bar": {"color": color},
                "bgcolor": "#1a1a2e",
                "bordercolor": "#1e293b",
                "steps": [
                    {"range": [0, 45], "color": "#1a0a0a"},
                    {"range": [45, 75], "color": "#1a1500"},
                    {"range": [75, 100], "color": "#0a1a0a"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.75,
                    "value": score,
                },
            },
            title={"text": "ATS Score", "font": {"color": "#94a3b8", "size": 14}},
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=250,
            margin=dict(t=40, b=10, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"""
        <div style="text-align:center;margin-top:-10px">
            <span style="font-size:1.1rem;font-weight:700;color:{color}">{ats_result.grade}</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📊 Section Breakdown")
        for section, data in ats_result.breakdown.items():
            pct = data["pct"]
            bar_color = "#22c55e" if pct >= 75 else "#f59e0b" if pct >= 50 else "#ef4444"
            st.markdown(f"""
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;
                            font-size:0.85rem;margin-bottom:4px">
                    <span style="color:#e2e8f0;font-weight:500">{section}</span>
                    <span style="color:{bar_color};font-weight:600">{data['score']}/{data['max']} pts ({pct}%)</span>
                </div>
                <div style="background:#1e293b;border-radius:6px;height:8px;overflow:hidden">
                    <div style="width:{pct}%;height:100%;background:{bar_color};
                                border-radius:6px;transition:width 0.5s"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Strengths & Weaknesses
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ✅ Strengths")
        if ats_result.strengths:
            for s in ats_result.strengths:
                st.markdown(f"<div style='color:#86efac;font-size:0.9rem;padding:4px 0'>✓ {s}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#64748b'>No strong sections detected yet.</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("#### ⚠️ Weaknesses")
        if ats_result.weaknesses:
            for w in ats_result.weaknesses:
                st.markdown(f"<div style='color:#fca5a5;font-size:0.9rem;padding:4px 0'>✗ {w}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#64748b'>No major weaknesses found!</div>", unsafe_allow_html=True)

    # Suggestions
    if ats_result.suggestions:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 💡 Improvement Suggestions")
        for i, suggestion in enumerate(ats_result.suggestions[:8], 1):
            st.markdown(f"""
            <div class="cp-card" style="padding:12px 16px;margin-bottom:8px;display:flex;gap:12px;align-items:flex-start">
                <span style="color:#6366f1;font-weight:700;min-width:22px">{i}.</span>
                <span style="color:#cbd5e1;font-size:0.9rem">{suggestion}</span>
            </div>
            """, unsafe_allow_html=True)


def _render_skills(tech_skills, soft_skills):
    import plotly.express as px
    import pandas as pd

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("#### 🔧 Technical Skills")
        if tech_skills:
            tags_html = "".join(f'<span class="cp-tag cp-tag-tech">{s}</span>' for s in tech_skills)
            st.markdown(f'<div style="line-height:2.2">{tags_html}</div>', unsafe_allow_html=True)
        else:
            st.warning("No technical skills detected. Ensure skills are explicitly listed.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🤝 Soft Skills")
        if soft_skills:
            tags_html = "".join(f'<span class="cp-tag cp-tag-soft">{s}</span>' for s in soft_skills)
            st.markdown(f'<div style="line-height:2.2">{tags_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No soft skills detected. Consider adding: communication, leadership, teamwork.")

    with col2:
        if tech_skills:
            # Category distribution pie chart
            cats = {
                "Languages": ["Python", "Java", "Javascript", "Typescript", "C++", "Go", "Rust", "Ruby", "Swift", "Kotlin", "R", "Scala", "Php"],
                "ML/AI": ["Machine Learning", "Deep Learning", "Tensorflow", "Pytorch", "Nlp", "Scikit-Learn", "Keras"],
                "Web/Framework": ["React", "Django", "Flask", "Fastapi", "Node.Js", "Angular", "Vue", "Spring"],
                "Cloud/DevOps": ["Aws", "Docker", "Kubernetes", "Azure", "Gcp", "Terraform", "Jenkins"],
                "Data": ["Sql", "Pandas", "Numpy", "Spark", "Tableau", "Power Bi", "Mongodb", "Postgresql"],
                "Other": [],
            }
            cat_counts = {k: 0 for k in cats}
            for skill in tech_skills:
                matched = False
                for cat, keywords in cats.items():
                    if cat == "Other":
                        continue
                    if any(k.lower() in skill.lower() or skill.lower() in k.lower() for k in keywords):
                        cat_counts[cat] += 1
                        matched = True
                        break
                if not matched:
                    cat_counts["Other"] += 1

            cat_counts = {k: v for k, v in cat_counts.items() if v > 0}
            if cat_counts:
                fig = px.pie(
                    values=list(cat_counts.values()),
                    names=list(cat_counts.keys()),
                    title="Skill Categories",
                    color_discrete_sequence=["#6366f1", "#a855f7", "#ec4899", "#f59e0b", "#22c55e", "#3b82f6"],
                    hole=0.45,
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#94a3b8"},
                    legend={"font": {"color": "#94a3b8"}},
                    title={"font": {"color": "#f1f5f9"}},
                    height=300,
                    margin=dict(t=40, b=10, l=10, r=10),
                )
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cp-card" style="background:rgba(99,102,241,0.08)">
        <b style="color:#a5b4fc">📊 Skill Summary</b><br>
        <span style="color:#94a3b8;font-size:0.9rem">
            Found <b style="color:#6366f1">{len(tech_skills)}</b> technical skills and
            <b style="color:#a855f7">{len(soft_skills)}</b> soft skills.
            {' 🟢 Great coverage!' if len(tech_skills) >= 10 else ' 🟡 Consider expanding your skills section.' if len(tech_skills) >= 5 else ' 🔴 Very few skills detected — list them explicitly.'}
        </span>
    </div>
    """, unsafe_allow_html=True)


def _render_sections(sections):
    all_sections = ["summary", "experience", "education", "skills", "projects", "certifications", "contact", "awards", "languages"]
    detected = set(sections.keys())

    st.markdown("#### 📋 Detected Sections")
    cols = st.columns(3)
    for i, sec in enumerate(all_sections):
        with cols[i % 3]:
            found = sec in detected and sections.get(sec, "").strip()
            icon = "✅" if found else "❌"
            color = "#86efac" if found else "#fca5a5"
            st.markdown(f"<div style='color:{color};padding:6px 0;font-size:0.9rem'>{icon} {sec.title()}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📄 Section Contents")
    for sec_name, sec_text in sections.items():
        if sec_name == "other" or not sec_text.strip():
            continue
        with st.expander(f"📌 {sec_name.title()} ({len(sec_text.split())} words)"):
            st.text(sec_text[:800] + ("..." if len(sec_text) > 800 else ""))


def _render_quality(text, action_verbs, achievements):
    word_count = len(text.split())
    col1, col2, col3 = st.columns(3)

    quality_items = [
        ("📝 Word Count", str(word_count), "300–700 ideal" if 300 <= word_count <= 700 else "⚠️ Outside ideal range"),
        ("⚡ Action Verbs", str(len(action_verbs)), "Found" if action_verbs else "❌ Add action verbs"),
        ("📈 Quantified Results", str(len(achievements)), "Found" if achievements else "❌ Add numbers/metrics"),
    ]
    for col, (label, val, note) in zip([col1, col2, col3], quality_items):
        with col:
            st.markdown(f"""
            <div class="cp-metric">
                <div style="font-size:0.78rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em">{label}</div>
                <div class="cp-metric-value">{val}</div>
                <div style="font-size:0.78rem;color:#64748b">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if action_verbs:
        st.markdown("#### ⚡ Strong Action Verbs Found")
        tags = "".join(f'<span class="cp-tag cp-tag-match">{v.title()}</span>' for v in action_verbs)
        st.markdown(f'<div style="line-height:2.2">{tags}</div>', unsafe_allow_html=True)
    else:
        st.warning("No strong action verbs detected. Start bullet points with verbs like: Built, Led, Designed, Optimized.")

    if achievements:
        st.markdown("<br>")
        st.markdown("#### 📈 Quantified Achievements Detected")
        for a in achievements[:6]:
            st.markdown(f"""
            <div class="cp-card" style="padding:10px 16px;margin-bottom:8px">
                <span style="color:#86efac;font-size:0.88rem">✓ {a}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No quantified achievements found. Add metrics like: 'Improved performance by 35%' or 'Managed a team of 8 engineers'.")


def _render_contact(contact_info):
    fields = [
        ("📧 Email", contact_info.get("email"), "Professional email required"),
        ("📱 Phone", contact_info.get("phone"), "With country code preferred"),
        ("🔗 LinkedIn", contact_info.get("linkedin"), "linkedin.com/in/yourname"),
        ("💻 GitHub", contact_info.get("github"), "github.com/yourname"),
        ("🌐 Portfolio", contact_info.get("portfolio"), "Personal website / portfolio"),
    ]

    for label, value, hint in fields:
        if value:
            st.markdown(f"""
            <div class="cp-card" style="padding:12px 20px;margin-bottom:10px;display:flex;align-items:center;gap:16px">
                <span style="font-size:1.2rem">{label.split()[0]}</span>
                <div>
                    <div style="color:#94a3b8;font-size:0.75rem">{label.split(' ', 1)[1]}</div>
                    <div style="color:#22c55e;font-weight:600;font-size:0.92rem">{value}</div>
                </div>
                <span style="margin-left:auto;color:#86efac;font-size:1.1rem">✅</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="cp-card" style="padding:12px 20px;margin-bottom:10px;display:flex;align-items:center;gap:16px;
                                         border-color:rgba(239,68,68,0.3)">
                <span style="font-size:1.2rem">{label.split()[0]}</span>
                <div>
                    <div style="color:#94a3b8;font-size:0.75rem">{label.split(' ', 1)[1]}</div>
                    <div style="color:#ef4444;font-size:0.88rem">Not detected — {hint}</div>
                </div>
                <span style="margin-left:auto;color:#fca5a5;font-size:1.1rem">❌</span>
            </div>
            """, unsafe_allow_html=True)


def _show_current_summary():
    tech = st.session_state.get("tech_skills", [])
    ats = st.session_state.get("ats_result")
    if ats:
        st.markdown(f"""
        <div class="cp-card">
            <b style="color:#a5b4fc">Current Resume Summary</b><br><br>
            🎯 ATS Score: <b style="color:#6366f1">{ats.total_score:.0f}/100</b> — {ats.grade}<br>
            💡 Tech Skills: <b style="color:#a855f7">{len(tech)}</b> extracted<br>
            📊 Grade: <b>{ats.grade}</b>
        </div>
        """, unsafe_allow_html=True)


def _show_placeholder():
    st.markdown("""
    <div style="text-align:center;padding:60px 20px">
        <div style="font-size:4rem;margin-bottom:16px">📄</div>
        <h3 style="color:#94a3b8;font-weight:600">Upload your resume to get started</h3>
        <p style="color:#64748b">Supports PDF and DOCX formats • Analysis takes under 5 seconds</p>
        <br>
        <div style="display:flex;justify-content:center;gap:24px;flex-wrap:wrap">
            <div style="background:#16213e;border:1px solid #1e293b;border-radius:12px;padding:16px 24px;color:#94a3b8;font-size:0.88rem">
                ✅ ATS Score (0-100)
            </div>
            <div style="background:#16213e;border:1px solid #1e293b;border-radius:12px;padding:16px 24px;color:#94a3b8;font-size:0.88rem">
                🧠 Skill Extraction
            </div>
            <div style="background:#16213e;border:1px solid #1e293b;border-radius:12px;padding:16px 24px;color:#94a3b8;font-size:0.88rem">
                📋 Section Analysis
            </div>
            <div style="background:#16213e;border:1px solid #1e293b;border-radius:12px;padding:16px 24px;color:#94a3b8;font-size:0.88rem">
                💡 Improvement Tips
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)