"""Dashboard Page — unified analytics view with career readiness and all key metrics."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.career_engine import compute_career_readiness
import plotly.graph_objects as go
import plotly.express as px


def show():
    st.markdown("""
    <h1 style="font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               background-clip:text">📊 Analytics Dashboard</h1>
    <p style="color:#94a3b8;margin-top:-8px">Your complete career intelligence overview.</p>
    """, unsafe_allow_html=True)

    tech_skills = st.session_state.get("tech_skills", [])
    if not tech_skills:
        st.warning("⚠️ No resume loaded yet. Upload your resume in **Resume Analysis** first.")
        _show_empty_dashboard()
        return

    ats_result = st.session_state.get("ats_result")
    soft_skills = st.session_state.get("soft_skills", [])
    job_matches = st.session_state.get("job_matches", [])
    gap_data = st.session_state.get("gap_data", {})
    years_exp = st.session_state.get("years_exp", 0)
    target_role = st.session_state.get("target_role", "Data Scientist")
    contact_info = st.session_state.get("contact_info", {})

    ats_score = ats_result.total_score if ats_result else 0
    avg_job_match = sum(j.get("match_pct", 0) for j in job_matches) / len(job_matches) if job_matches else 0
    has_certs = "certifications" in st.session_state.get("resume_sections", {})

    # ── Compute Career Readiness ─────────────────────────────────────────────────
    cr = compute_career_readiness(
        ats_score=ats_score,
        tech_skills=tech_skills,
        soft_skills=soft_skills,
        has_certifications=has_certs,
        years_experience=years_exp,
        avg_job_match=avg_job_match,
    )
    st.session_state["career_readiness"] = cr

    # ── Career Readiness Hero ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="cp-card" style="background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(168,85,247,0.15));
                                border-color:rgba(99,102,241,0.4);margin-bottom:24px">
        <div style="display:flex;align-items:center;gap:32px;flex-wrap:wrap">
            <div style="text-align:center;min-width:140px">
                <div style="font-size:3.5rem;font-weight:900;background:linear-gradient(135deg,#6366f1,#a855f7);
                             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                             background-clip:text">{cr['score']:.0f}</div>
                <div style="font-size:1rem;color:#94a3b8;margin-top:-4px">/ 100</div>
                <div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px">Career Readiness</div>
            </div>
            <div style="flex:1;min-width:200px">
                <div style="font-size:1.4rem;font-weight:800;color:{cr['level_color']};margin-bottom:4px">{cr['level']}</div>
                <div style="background:#1e293b;border-radius:8px;height:12px;overflow:hidden;margin:10px 0">
                    <div style="width:{cr['score']}%;height:100%;background:linear-gradient(90deg,#6366f1,#a855f7);border-radius:8px"></div>
                </div>
                <div style="color:#94a3b8;font-size:0.85rem">Target: <b style="color:#6366f1">{target_role}</b></div>
            </div>
            <div style="min-width:200px">
                {''.join(f'<div style="color:#94a3b8;font-size:0.83rem;padding:3px 0">• {s}</div>' for s in cr['suggestions'][:3])}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 5 Key Metrics ────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    kvs = [
        ("🎯 ATS Score", f"{ats_score:.0f}%", ats_result.grade if ats_result else "—"),
        ("💡 Tech Skills", str(len(tech_skills)), "Extracted"),
        ("🤝 Soft Skills", str(len(soft_skills)), "Identified"),
        ("📅 Experience", f"~{years_exp}yr" if years_exp else "N/A", "Estimated"),
        ("💼 Job Match", f"{avg_job_match:.0f}%" if job_matches else "—", f"{len(job_matches)} jobs"),
    ]
    for col, (label, val, sub) in zip([c1, c2, c3, c4, c5], kvs):
        with col:
            st.markdown(f"""
            <div class="cp-metric">
                <div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em">{label}</div>
                <div class="cp-metric-value" style="font-size:1.8rem">{val}</div>
                <div style="font-size:0.72rem;color:#64748b">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row 1 ─────────────────────────────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 🎯 ATS Score Breakdown")
        if ats_result:
            _ats_breakdown_chart(ats_result.breakdown)
        else:
            st.info("Run Resume Analysis first.")

    with col_r:
        st.markdown("#### ⭐ Career Readiness Breakdown")
        _career_readiness_chart(cr["breakdown"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row 2 ─────────────────────────────────────────────────────────────
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown("#### 💡 Skill Distribution")
        _skill_distribution_chart(tech_skills, soft_skills)

    with col_r2:
        st.markdown("#### 💼 Job Match Scores")
        if job_matches:
            _job_match_chart(job_matches)
        else:
            st.info("Run Job Recommendations first to see match scores.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gap Analysis Summary ─────────────────────────────────────────────────────
    if gap_data:
        st.markdown("#### 🔍 Skill Gap Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="cp-metric">
                <div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase">Core Coverage</div>
                <div style="font-size:2rem;font-weight:800;color:#6366f1">{gap_data.get('coverage_pct',0):.0f}%</div>
                <div style="font-size:0.72rem;color:#64748b">For {target_role}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="cp-metric">
                <div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase">Core Skills Missing</div>
                <div style="font-size:2rem;font-weight:800;color:#ef4444">{len(gap_data.get('core_missing',[]))}</div>
                <div style="font-size:0.72rem;color:#64748b">Essential gaps</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="cp-metric">
                <div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase">Skills Matched</div>
                <div style="font-size:2rem;font-weight:800;color:#22c55e">{len(gap_data.get('matching_core',[]))}</div>
                <div style="font-size:0.72rem;color:#64748b">Core requirements</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Contact Info Status ──────────────────────────────────────────────────────
    st.markdown("#### 👤 Contact Profile Status")
    contact_fields = [
        ("Email", contact_info.get("email")),
        ("Phone", contact_info.get("phone")),
        ("LinkedIn", contact_info.get("linkedin")),
        ("GitHub", contact_info.get("github")),
        ("Portfolio", contact_info.get("portfolio")),
    ]
    contact_cols = st.columns(5)
    for col, (field, val) in zip(contact_cols, contact_fields):
        with col:
            color = "#22c55e" if val else "#ef4444"
            icon = "✅" if val else "❌"
            st.markdown(f"""
            <div style="text-align:center;padding:12px;background:#16213e;
                        border:1px solid {'rgba(34,197,94,0.3)' if val else 'rgba(239,68,68,0.2)'};
                        border-radius:10px">
                <div style="font-size:1.3rem">{icon}</div>
                <div style="font-size:0.75rem;color:{color};font-weight:600;margin-top:4px">{field}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Export Section ───────────────────────────────────────────────────────────
    st.markdown("<br>")
    st.markdown("#### 📥 Export Report")
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("📄 Download PDF Report", use_container_width=True):
            _generate_report(cr, ats_result, tech_skills, soft_skills, gap_data, target_role)


def _ats_breakdown_chart(breakdown: dict):
    labels = list(breakdown.keys())
    pcts = [v["pct"] for v in breakdown.values()]
    colors = ["#22c55e" if p >= 75 else "#f59e0b" if p >= 50 else "#ef4444" for p in pcts]

    fig = go.Figure(go.Bar(
        x=labels,
        y=pcts,
        marker_color=colors,
        text=[f"{p}%" for p in pcts],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 115], gridcolor="#1e293b", tickfont=dict(color="#64748b")),
        xaxis=dict(tickfont=dict(color="#94a3b8", size=10)),
        margin=dict(t=20, b=20, l=10, r=10),
        height=280,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _career_readiness_chart(breakdown: dict):
    labels = [k.split(" (")[0] for k in breakdown.keys()]
    max_vals = [float(k.split("(")[1].replace("%)", "")) for k in breakdown.keys()]
    actual_vals = list(breakdown.values())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Your Score",
        x=labels,
        y=actual_vals,
        marker_color="#6366f1",
        text=[f"{v}" for v in actual_vals],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=10),
    ))
    fig.add_trace(go.Bar(
        name="Max Possible",
        x=labels,
        y=max_vals,
        marker_color="rgba(99,102,241,0.15)",
        text=[f"{v}" for v in max_vals],
        textposition="inside",
        textfont=dict(color="#64748b", size=9),
    ))
    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 35], gridcolor="#1e293b", tickfont=dict(color="#64748b")),
        xaxis=dict(tickfont=dict(color="#94a3b8", size=9)),
        legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=20, b=20, l=10, r=10),
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True)


def _skill_distribution_chart(tech_skills: list, soft_skills: list):
    if not tech_skills and not soft_skills:
        st.info("No skills extracted yet.")
        return

    # Category map
    cats = {
        "Languages": ["Python", "Java", "Javascript", "Typescript", "C++", "Go", "Rust", "R", "Scala", "Swift", "Kotlin"],
        "ML/AI": ["Machine Learning", "Deep Learning", "Nlp", "Tensorflow", "Pytorch", "Scikit-Learn", "Keras"],
        "Web": ["React", "Django", "Flask", "Fastapi", "Node.Js", "Angular", "Vue", "Spring"],
        "Cloud/DevOps": ["Aws", "Docker", "Kubernetes", "Azure", "Gcp", "Terraform", "Jenkins", "Linux"],
        "Data": ["Sql", "Pandas", "Numpy", "Spark", "Tableau", "Power Bi", "Mongodb", "Postgresql"],
        "Soft Skills": soft_skills,
        "Other": [],
    }

    cat_counts = {}
    for skill in tech_skills:
        matched = False
        for cat, keywords in cats.items():
            if cat in ("Other", "Soft Skills"):
                continue
            if any(k.lower() in skill.lower() or skill.lower() in k.lower() for k in keywords):
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
                matched = True
                break
        if not matched:
            cat_counts["Other"] = cat_counts.get("Other", 0) + 1

    if soft_skills:
        cat_counts["Soft Skills"] = len(soft_skills)

    cat_counts = {k: v for k, v in cat_counts.items() if v > 0}

    fig = px.bar(
        x=list(cat_counts.values()),
        y=list(cat_counts.keys()),
        orientation="h",
        color_discrete_sequence=["#6366f1"],
        text=[str(v) for v in cat_counts.values()],
    )
    fig.update_traces(textposition="outside", textfont=dict(color="#94a3b8"))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#1e293b", tickfont=dict(color="#64748b")),
        yaxis=dict(tickfont=dict(color="#94a3b8")),
        margin=dict(t=10, b=10, l=10, r=40),
        height=280,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _job_match_chart(job_matches: list):
    if not job_matches:
        return
    titles = [j.get("title", "")[:28] + ("…" if len(j.get("title", "")) > 28 else "") for j in job_matches[:8]]
    scores = [j.get("match_pct", 0) for j in job_matches[:8]]
    colors = ["#22c55e" if s >= 70 else "#f59e0b" if s >= 45 else "#ef4444" for s in scores]

    fig = go.Figure(go.Bar(
        x=scores,
        y=titles,
        orientation="h",
        marker_color=colors,
        text=[f"{s:.0f}%" for s in scores],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=10),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 115], gridcolor="#1e293b", tickfont=dict(color="#64748b")),
        yaxis=dict(tickfont=dict(color="#94a3b8", size=10)),
        margin=dict(t=10, b=10, l=10, r=50),
        height=280,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _generate_report(cr, ats_result, tech_skills, soft_skills, gap_data, target_role):
    """Generate a downloadable PDF/text career report."""
    try:
        ats_score = ats_result.total_score if ats_result else 0
        report_lines = [
            "=" * 60,
            "         CAREER PILOT AI — CAREER REPORT",
            "=" * 60,
            "",
            f"Career Readiness Score : {cr['score']:.0f}/100 — {cr['level']}",
            f"ATS Score              : {ats_score:.0f}/100 — {ats_result.grade if ats_result else 'N/A'}",
            f"Technical Skills       : {len(tech_skills)}",
            f"Soft Skills            : {len(soft_skills)}",
            f"Target Role            : {target_role}",
            "",
            "-" * 40,
            "TECHNICAL SKILLS",
            "-" * 40,
        ]
        for i, s in enumerate(tech_skills, 1):
            report_lines.append(f"  {i:2}. {s}")

        if gap_data:
            report_lines += [
                "",
                "-" * 40,
                f"SKILL GAP — {target_role.upper()}",
                "-" * 40,
                f"Core Coverage : {gap_data.get('coverage_pct',0):.0f}%",
                "",
                "Skills Matched:",
            ]
            for s in gap_data.get("matching_core", []):
                report_lines.append(f"  ✓ {s}")
            report_lines.append("\nCore Skills Missing:")
            for s in gap_data.get("core_missing", []):
                report_lines.append(f"  ✗ {s}")

        if ats_result and ats_result.suggestions:
            report_lines += [
                "",
                "-" * 40,
                "ATS IMPROVEMENT SUGGESTIONS",
                "-" * 40,
            ]
            for i, s in enumerate(ats_result.suggestions[:8], 1):
                report_lines.append(f"  {i}. {s}")

        report_lines += [
            "",
            "-" * 40,
            "CAREER READINESS SUGGESTIONS",
            "-" * 40,
        ]
        for s in cr.get("suggestions", []):
            report_lines.append(f"  • {s}")

        report_lines += ["", "=" * 60, "Generated by Career Pilot AI", "=" * 60]
        report_text = "\n".join(report_lines)

        st.download_button(
            label="⬇️ Download Report (.txt)",
            data=report_text,
            file_name="career_pilot_report.txt",
            mime="text/plain",
        )
    except Exception as e:
        st.error(f"Could not generate report: {e}")


def _show_empty_dashboard():
    st.markdown("""
    <div style="text-align:center;padding:60px 20px">
        <div style="font-size:4rem;margin-bottom:16px">📊</div>
        <h3 style="color:#94a3b8">Your dashboard is empty</h3>
        <p style="color:#64748b">Upload your resume to start seeing analytics here.</p>
        <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-top:24px">
            <div style="background:#16213e;border:1px dashed #1e293b;border-radius:12px;padding:20px 28px;
                        color:#64748b;font-size:0.85rem;min-width:140px;text-align:center">
                📈<br>ATS Breakdown
            </div>
            <div style="background:#16213e;border:1px dashed #1e293b;border-radius:12px;padding:20px 28px;
                        color:#64748b;font-size:0.85rem;min-width:140px;text-align:center">
                🕸️<br>Skill Radar
            </div>
            <div style="background:#16213e;border:1px dashed #1e293b;border-radius:12px;padding:20px 28px;
                        color:#64748b;font-size:0.85rem;min-width:140px;text-align:center">
                💼<br>Job Match Chart
            </div>
            <div style="background:#16213e;border:1px dashed #1e293b;border-radius:12px;padding:20px 28px;
                        color:#64748b;font-size:0.85rem;min-width:140px;text-align:center">
                ⭐<br>Career Readiness
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)