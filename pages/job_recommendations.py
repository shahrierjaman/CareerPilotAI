"""Job Recommendations Page — fetch real jobs, score matches, display results."""

import streamlit as st
import sys, os
import html as html_module          # for escaping dynamic text
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.job_recommender import fetch_jobs, compute_job_match, COUNTRY_MAP


def show():
    st.markdown("""
    <h1 style="font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               background-clip:text">💼 Job Recommendations</h1>
    <p style="color:#94a3b8;margin-top:-8px">Real job listings matched to your resume skills — with a compatibility score for each.</p>
    """, unsafe_allow_html=True)

    tech_skills = st.session_state.get("tech_skills", [])
    if not tech_skills:
        st.warning("⚠️ No resume loaded yet. Go to **Resume Analysis** and upload your resume first.")
        return

    # ── Search Controls ─────────────────────────────────────────────────────────
    with st.expander("🔧 Search Settings", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            job_title = st.text_input("Job Title (optional)", placeholder="e.g. Data Scientist, ML Engineer")
        with c2:
            country = st.selectbox("Country", list(COUNTRY_MAP.keys()), index=0)
        with c3:
            location = st.text_input("City / Region (optional)", placeholder="e.g. New York, Bangalore")

        c4, c5 = st.columns(2)
        with c4:
            remote_only = st.checkbox("🌐 Remote Jobs Only")
        with c5:
            max_results = st.slider("Max Results", 4, 10, 6)

        # API keys from session state (unified dict)
        api_keys = st.session_state.get("api_keys", {})
        if not any(api_keys.values()):
            st.info(
                "💡 **Demo Mode** — Showing sample job listings. "
                "Add API keys in **⚙️ Settings** to get real jobs from Adzuna, Jooble, or JSearch."
            )

    if st.button("🔍 Find Matching Jobs", use_container_width=True):
        with st.spinner("🌐 Searching job listings..."):
            jobs = fetch_jobs(
                skills=tech_skills,
                job_title=job_title,
                country_name=country,
                location=location,
                remote_only=remote_only,
                max_results=max_results,
                api_keys=api_keys,                     # pass the unified dict
            )

        if not jobs:
            st.error("No jobs found. Try different search terms or check your API keys in Settings.")
            return

        # Compute match scores for all jobs
        with st.spinner("🧠 Computing match scores..."):
            job_matches = []
            for job in jobs:
                match = compute_job_match(tech_skills, job)
                job_matches.append({**job, **match})

        # Sort by match percentage
        job_matches.sort(key=lambda x: x.get("match_pct", 0), reverse=True)
        st.session_state["jobs"] = jobs
        st.session_state["job_matches"] = job_matches

        st.success(f"✅ Found {len(job_matches)} job listings!")

    # ── Display Jobs ─────────────────────────────────────────────────────────────
    job_matches = st.session_state.get("job_matches", [])
    if not job_matches:
        _show_placeholder(tech_skills)
        return

    # Summary bar
    if job_matches:
        avg_match = sum(j.get("match_pct", 0) for j in job_matches) / len(job_matches)
        best_match = max(j.get("match_pct", 0) for j in job_matches)
        st.markdown(f"""
        <div style="display:flex;gap:16px;margin:16px 0;flex-wrap:wrap">
            <div class="cp-metric" style="flex:1;min-width:140px">
                <div style="font-size:0.78rem;color:#94a3b8;text-transform:uppercase">Jobs Found</div>
                <div class="cp-metric-value">{len(job_matches)}</div>
            </div>
            <div class="cp-metric" style="flex:1;min-width:140px">
                <div style="font-size:0.78rem;color:#94a3b8;text-transform:uppercase">Avg Match</div>
                <div class="cp-metric-value">{avg_match:.0f}%</div>
            </div>
            <div class="cp-metric" style="flex:1;min-width:140px">
                <div style="font-size:0.78rem;color:#94a3b8;text-transform:uppercase">Best Match</div>
                <div class="cp-metric-value">{best_match:.0f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Job cards
    for i, job in enumerate(job_matches):
        _render_job_card(job, i + 1)


def _render_job_card(job: dict, rank: int):
    match_pct = job.get("match_pct", 0)
    bar_color = "#22c55e" if match_pct >= 70 else "#f59e0b" if match_pct >= 45 else "#ef4444"
    source_badge = f'<span style="background:rgba(99,102,241,0.2);color:#a5b4fc;font-size:0.7rem;padding:2px 8px;border-radius:10px;font-weight:600">{html_module.escape(job.get("source",""))}</span>'

    matching = job.get("matching_skills", [])
    missing = job.get("missing_skills", [])

    matching_tags = "".join(f'<span class="cp-tag cp-tag-match">{html_module.escape(s)}</span>' for s in matching[:6])
    missing_tags = "".join(f'<span class="cp-tag cp-tag-missing">{html_module.escape(s)}</span>' for s in missing[:5])

    salary_html = ""
    if job.get("salary"):
        salary_html = f'<span style="color:#f59e0b;font-weight:600">💰 {html_module.escape(job.get("salary",""))}</span> &nbsp;·&nbsp; '

    # Escape all dynamic text fields
    title = html_module.escape(job.get('title',''))
    company = html_module.escape(job.get('company',''))
    location = html_module.escape(job.get('location',''))
    description = html_module.escape(job.get('description',''))
    posted = html_module.escape(job.get('posted','')[:10] if job.get('posted') else '')
    url = html_module.escape(job.get('url','#'))
    # Truncate description safely (after escaping)
    desc_display = description[:160] + ('...' if len(description) > 160 else '')

    st.markdown(f"""
    <div class="cp-job-card">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap">
            <div style="flex:1;min-width:200px">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                    <span style="color:#6366f1;font-weight:800;font-size:1rem">#{rank}</span>
                    <h3 style="margin:0;color:#f1f5f9;font-size:1.05rem;font-weight:700">{title}</h3>
                    {source_badge}
                </div>
                <div style="color:#94a3b8;font-size:0.88rem;margin-bottom:8px">
                    🏢 <b style="color:#cbd5e1">{company}</b> &nbsp;·&nbsp;
                    📍 {location} &nbsp;·&nbsp;
                    {salary_html}
                    <span style="color:#64748b">{posted}</span>
                </div>
                <p style="color:#94a3b8;font-size:0.85rem;margin:0;line-height:1.5">
                    {desc_display}
                </p>
            </div>
            <div style="text-align:center;min-width:90px">
                <div style="font-size:1.8rem;font-weight:800;color:{bar_color}">{match_pct:.0f}%</div>
                <div style="font-size:0.72rem;color:#64748b;text-transform:uppercase">Match</div>
                <div style="background:#1e293b;border-radius:6px;height:6px;width:80px;margin:8px auto 0 auto;overflow:hidden">
                    <div style="width:{match_pct}%;height:100%;background:{bar_color};border-radius:6px"></div>
                </div>
            </div>
        </div>
        <hr style="border-color:#1e293b;margin:14px 0">
        <div style="display:flex;gap:24px;flex-wrap:wrap;font-size:0.82rem">
            <div>
                <div style="color:#64748b;margin-bottom:6px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em">✅ Matching Skills</div>
                <div>{matching_tags if matching_tags else '<span style="color:#64748b">None detected</span>'}</div>
            </div>
            <div>
                <div style="color:#64748b;margin-bottom:6px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em">❌ Missing Skills</div>
                <div>{missing_tags if missing_tags else '<span style="color:#86efac">All skills matched!</span>'}</div>
            </div>
        </div>
        <div style="margin-top:12px">
            <a href="{url}" target="_blank"
               style="background:linear-gradient(135deg,#6366f1,#a855f7);color:white;
                      padding:8px 20px;border-radius:8px;text-decoration:none;
                      font-weight:600;font-size:0.85rem">
                🔗 Apply Now →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _show_placeholder(tech_skills):
    skills_preview = ", ".join(html_module.escape(s) for s in tech_skills[:5])
    st.markdown(f"""
    <div style="text-align:center;padding:50px 20px">
        <div style="font-size:3.5rem;margin-bottom:16px">💼</div>
        <h3 style="color:#94a3b8;font-weight:600">Ready to find your next opportunity</h3>
        <p style="color:#64748b">
            Your top skills: <b style="color:#a5b4fc">{skills_preview}{'...' if len(tech_skills) > 5 else ''}</b>
        </p>
        <p style="color:#64748b">Click <b>Find Matching Jobs</b> above to search real listings.</p>
    </div>
    """, unsafe_allow_html=True)