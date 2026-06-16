"""Skill Gap Analysis Page — radar charts, match bars, missing skills breakdown."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.career_engine import analyze_skill_gap, get_available_roles
import plotly.graph_objects as go
import plotly.express as px


def show():
    st.markdown("""
    <h1 style="font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               background-clip:text">🔍 Skill Gap Analysis</h1>
    <p style="color:#94a3b8;margin-top:-8px">See exactly which skills you have vs. what your target role requires.</p>
    """, unsafe_allow_html=True)

    tech_skills = st.session_state.get("tech_skills", [])
    if not tech_skills:
        st.warning("⚠️ No resume loaded. Go to **Resume Analysis** first.")
        return

    # ── Target Role Selection ───────────────────────────────────────────────────
    roles = get_available_roles()
    col1, col2 = st.columns([2, 1])
    with col1:
        target_role = st.selectbox(
            "🎯 Select your target role",
            roles,
            index=roles.index(st.session_state.get("target_role", roles[0])),
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("Analyze Gap →", use_container_width=True)

    if analyze_btn or st.session_state.get("gap_data"):
        if analyze_btn:
            with st.spinner("🔍 Analyzing skill gap..."):
                gap_data = analyze_skill_gap(tech_skills, target_role)
            st.session_state["gap_data"] = gap_data
            st.session_state["target_role"] = target_role
        else:
            gap_data = st.session_state.get("gap_data")
            target_role = st.session_state.get("target_role", target_role)

        if not gap_data:
            return

        _render_gap_analysis(gap_data, tech_skills, target_role)


def _render_gap_analysis(gap_data, tech_skills, target_role):
    coverage = gap_data.get("coverage_pct", 0)
    matching = gap_data.get("matching_core", [])
    core_missing = gap_data.get("core_missing", [])
    adv_missing = gap_data.get("advanced_missing", [])
    nice_missing = gap_data.get("nice_to_have_missing", [])
    all_core = gap_data.get("all_core", [])

    # ── Top Metrics ─────────────────────────────────────────────────────────────
    total_missing = len(core_missing) + len(adv_missing)
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        ("🎯 Core Coverage", f"{coverage:.0f}%", f"{len(matching)}/{len(all_core)} core skills"),
        ("✅ Skills Matched", str(len(matching)), "Core requirements met"),
        ("❌ Core Missing", str(len(core_missing)), "Must-have skills"),
        ("📈 Advanced Missing", str(len(adv_missing)), "Nice-to-have for senior roles"),
    ]
    for col, (label, val, sub) in zip([c1, c2, c3, c4], metrics):
        color = "#22c55e" if val != "0" and label in ["✅ Skills Matched", "🎯 Core Coverage"] else "#ef4444" if label == "❌ Core Missing" and val != "0" else "#6366f1"
        with col:
            st.markdown(f"""
            <div class="cp-metric">
                <div style="font-size:0.75rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.07em">{label}</div>
                <div style="font-size:2.2rem;font-weight:800;color:{color}">{val}</div>
                <div style="font-size:0.75rem;color:#64748b">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two Column Layout ────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### 🕸️ Skill Coverage Radar")
        _radar_chart(gap_data, tech_skills, target_role)

    with col_right:
        st.markdown("#### 📊 Core Skills Progress")
        _skills_progress_bars(matching, core_missing, all_core)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Skills Breakdown ────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(f"""
        <div class="cp-card">
            <div class="cp-section-title" style="color:#22c55e">✅ Skills You Have</div>
        """, unsafe_allow_html=True)
        if matching:
            for s in matching:
                st.markdown(f'<span class="cp-tag cp-tag-match">{s}</span>', unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#64748b;font-size:0.85rem'>None matched yet.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div class="cp-card">
            <div class="cp-section-title" style="color:#ef4444">🔴 Core Missing Skills</div>
        """, unsafe_allow_html=True)
        if core_missing:
            for s in core_missing:
                st.markdown(f'<span class="cp-tag cp-tag-missing">{s}</span>', unsafe_allow_html=True)
            st.markdown(f"<div style='color:#ef4444;font-size:0.8rem;margin-top:8px'>⚠️ These are essential to get interviews for {target_role}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#86efac'>🎉 All core skills covered!</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_c:
        st.markdown(f"""
        <div class="cp-card">
            <div class="cp-section-title" style="color:#f59e0b">🟡 Advanced / Nice-to-Have</div>
        """, unsafe_allow_html=True)
        all_adv = adv_missing + nice_missing
        if all_adv:
            for s in adv_missing[:5]:
                st.markdown(f'<span style="background:rgba(245,158,11,0.15);color:#fcd34d;border:1px solid rgba(245,158,11,0.3);padding:3px 10px;border-radius:20px;font-size:0.78rem;margin:3px;display:inline-block">{s}</span>', unsafe_allow_html=True)
            for s in nice_missing[:4]:
                st.markdown(f'<span style="background:rgba(59,130,246,0.15);color:#93c5fd;border:1px solid rgba(59,130,246,0.3);padding:3px 10px;border-radius:20px;font-size:0.78rem;margin:3px;display:inline-block">{s}</span>', unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#86efac'>🎉 All advanced skills covered!</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Overall readiness bar ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    readiness_color = "#22c55e" if coverage >= 75 else "#f59e0b" if coverage >= 50 else "#ef4444"
    readiness_label = "🟢 Ready to Apply!" if coverage >= 75 else "🟡 Almost Ready — Fill Core Gaps" if coverage >= 50 else "🔴 Needs Significant Skill Building"

    st.markdown(f"""
    <div class="cp-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <b style="color:#f1f5f9;font-size:1rem">Overall Readiness for <span style="color:#6366f1">{target_role}</span></b>
            <span style="color:{readiness_color};font-weight:700">{readiness_label}</span>
        </div>
        <div style="background:#1e293b;border-radius:8px;height:14px;overflow:hidden">
            <div style="width:{coverage}%;height:100%;background:linear-gradient(90deg,#6366f1,#a855f7);border-radius:8px;transition:width 0.5s"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:0.8rem;color:#64748b">
            <span>0%</span>
            <span style="color:{readiness_color};font-weight:600">{coverage:.0f}% Core Coverage</span>
            <span>100%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Go to Learning Path CTA ─────────────────────────────────────────────────
    if core_missing:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🗺️ Generate My Learning Roadmap →", use_container_width=True):
                st.session_state["current_page"] = "🗺️ Learning Roadmap"
                st.rerun()


def _radar_chart(gap_data, tech_skills, target_role):
    from data.skills_database import JOB_ROLE_SKILLS

    role_data = JOB_ROLE_SKILLS.get(target_role, {})
    all_skills = (role_data.get("core", []) + role_data.get("advanced", []))[:8]

    if not all_skills:
        st.info("Radar chart not available for custom roles.")
        return

    resume_lower = {s.lower() for s in tech_skills}

    def skill_score(skill):
        sl = skill.lower()
        if sl in resume_lower:
            return 100
        from rapidfuzz import fuzz, process
        best = process.extractOne(sl, list(resume_lower), scorer=fuzz.ratio)
        if best and best[1] >= 75:
            return best[1]
        return 10

    scores = [skill_score(s) for s in all_skills]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=all_skills + [all_skills[0]],
        fill="toself",
        name="Your Skills",
        line_color="#6366f1",
        fillcolor="rgba(99,102,241,0.25)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[100] * (len(all_skills) + 1),
        theta=all_skills + [all_skills[0]],
        fill="toself",
        name="Required",
        line_color="#ef4444",
        fillcolor="rgba(239,68,68,0.08)",
        line_dash="dash",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="#1e293b", linecolor="#1e293b",
                tickfont=dict(color="#64748b", size=9),
            ),
            angularaxis=dict(
                gridcolor="#1e293b", linecolor="#1e293b",
                tickfont=dict(color="#94a3b8", size=10),
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#94a3b8")),
        margin=dict(t=30, b=20, l=40, r=40),
        height=320,
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def _skills_progress_bars(matching, core_missing, all_core):
    for skill in all_core:
        has_it = skill in matching
        color = "#22c55e" if has_it else "#ef4444"
        pct = 100 if has_it else 0
        icon = "✅" if has_it else "❌"
        st.markdown(f"""
        <div style="margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:4px">
                <span style="color:#e2e8f0">{icon} {skill}</span>
                <span style="color:{color};font-weight:600">{"Have it" if has_it else "Missing"}</span>
            </div>
            <div style="background:#1e293b;border-radius:5px;height:7px;overflow:hidden">
                <div style="width:{pct}%;height:100%;background:{color};border-radius:5px"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)