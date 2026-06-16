"""Learning Roadmap Page — personalized step-by-step skill-building plan with free resources."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.career_engine import (
    analyze_skill_gap, generate_learning_path, get_available_roles
)


def show():
    st.markdown("""
    <h1 style="font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               background-clip:text">🗺️ Learning Roadmap</h1>
    <p style="color:#94a3b8;margin-top:-8px">Your personalized step-by-step plan to bridge skill gaps — with free learning resources.</p>
    """, unsafe_allow_html=True)

    tech_skills = st.session_state.get("tech_skills", [])
    if not tech_skills:
        st.warning("⚠️ No resume loaded. Go to **Resume Analysis** first.")
        return

    # ── Role & Preference Selection ─────────────────────────────────────────────
    roles = get_available_roles()
    col1, col2 = st.columns([2, 1])
    with col1:
        target_role = st.selectbox(
            "🎯 Target Role",
            roles,
            index=roles.index(st.session_state.get("target_role", roles[0])),
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        gen_btn = st.button("🗺️ Generate Roadmap", use_container_width=True)

    if gen_btn or st.session_state.get("learning_path"):
        if gen_btn:
            with st.spinner("🧠 Building your personalized roadmap..."):
                gap_data = analyze_skill_gap(tech_skills, target_role)
                learning_path = generate_learning_path(tech_skills, target_role, gap_data)
            st.session_state["gap_data"] = gap_data
            st.session_state["learning_path"] = learning_path
            st.session_state["target_role"] = target_role
        else:
            gap_data = st.session_state.get("gap_data", {})
            learning_path = st.session_state.get("learning_path", [])
            target_role = st.session_state.get("target_role", target_role)

        if not learning_path:
            gap_data_check = analyze_skill_gap(tech_skills, target_role)
            if not gap_data_check.get("core_missing") and not gap_data_check.get("advanced_missing"):
                st.balloons()
                st.success(f"🎉 You already have all the skills for **{target_role}**! Your profile is complete.")
                _render_current_skills(tech_skills)
                return

        _render_roadmap(learning_path, target_role, gap_data, tech_skills)


def _render_roadmap(learning_path, target_role, gap_data, tech_skills):
    coverage = gap_data.get("coverage_pct", 0)
    total_steps = len(learning_path)

    # ── Header ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="cp-card" style="background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(168,85,247,0.12));
                                border-color:rgba(99,102,241,0.3);margin-bottom:24px">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px">
            <div>
                <div style="color:#94a3b8;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em">Your Path To</div>
                <div style="font-size:1.5rem;font-weight:800;color:#f1f5f9">{target_role}</div>
                <div style="color:#64748b;font-size:0.88rem;margin-top:4px">
                    Current skill coverage: <span style="color:#6366f1;font-weight:600">{coverage:.0f}%</span>
                    &nbsp;·&nbsp; {total_steps} learning steps
                </div>
            </div>
            <div style="text-align:right">
                <div style="font-size:0.8rem;color:#94a3b8">Already have</div>
                <div style="font-size:1.2rem;font-weight:700;color:#22c55e">{len(gap_data.get('matching_core',[]))} core skills</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not learning_path:
        st.success("🎉 No skill gaps found for this role! You're ready to apply.")
        return

    # ── Total time estimate ──────────────────────────────────────────────────────
    essential = [s for s in learning_path if "Essential" in s.get("priority", "")]
    important = [s for s in learning_path if "Important" in s.get("priority", "")]
    nice = [s for s in learning_path if "Nice" in s.get("priority", "")]

    st.markdown(f"""
    <div style="display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap">
        <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:10px;
                    padding:10px 16px;font-size:0.85rem;color:#fca5a5">
            🔴 Essential: <b>{len(essential)}</b> skills
        </div>
        <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:10px;
                    padding:10px 16px;font-size:0.85rem;color:#fcd34d">
            🟡 Important: <b>{len(important)}</b> skills
        </div>
        <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:10px;
                    padding:10px 16px;font-size:0.85rem;color:#86efac">
            🟢 Nice-to-Have: <b>{len(nice)}</b> skills
        </div>
        <div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);border-radius:10px;
                    padding:10px 16px;font-size:0.85rem;color:#a5b4fc">
            ⏱️ Estimated: <b>2–8 months</b> total
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Roadmap Steps ────────────────────────────────────────────────────────────
    st.markdown("### 📍 Step-by-Step Roadmap")

    for step in learning_path:
        _render_step_card(step)

    # ── Currently Have ───────────────────────────────────────────────────────────
    if gap_data.get("matching_core"):
        st.markdown("<br>")
        st.markdown("### ✅ Skills You Already Have")
        tags = "".join(f'<span class="cp-tag cp-tag-match">{s}</span>' for s in gap_data["matching_core"])
        st.markdown(f'<div style="line-height:2.5;margin-bottom:16px">{tags}</div>', unsafe_allow_html=True)

    # ── Platform recommendations ─────────────────────────────────────────────────
    st.markdown("<br>")
    st.markdown("### 🎓 Top Free Learning Platforms")
    platforms = [
        ("freeCodeCamp", "https://freecodecamp.org", "Full-stack, Python, data science — completely free", "🆓"),
        ("Kaggle Learn", "https://www.kaggle.com/learn", "ML, data science, SQL with free notebooks", "📊"),
        ("CS50 / Harvard", "https://cs50.harvard.edu", "World-class CS fundamentals — 100% free", "🏛️"),
        ("fast.ai", "https://course.fast.ai", "Practical deep learning — free & beginner-friendly", "🤖"),
        ("The Odin Project", "https://theodinproject.com", "Complete web dev curriculum — free & open source", "⚔️"),
        ("Coursera (Audit)", "https://coursera.org", "Audit most courses for free — certificates optional", "📜"),
    ]
    cols = st.columns(3)
    for i, (name, url, desc, icon) in enumerate(platforms):
        with cols[i % 3]:
            st.markdown(f"""
            <a href="{url}" target="_blank" style="text-decoration:none">
                <div class="cp-card" style="text-align:center;cursor:pointer;min-height:130px">
                    <div style="font-size:1.8rem;margin-bottom:8px">{icon}</div>
                    <div style="color:#a5b4fc;font-weight:700;margin-bottom:6px">{name}</div>
                    <div style="color:#64748b;font-size:0.78rem;line-height:1.4">{desc}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)


def _render_step_card(step: dict):
    step_num = step.get("step", "?")
    skill = step.get("skill", "")
    priority = step.get("priority", "")
    reason = step.get("reason", "")
    est_time = step.get("estimated_time", "")
    resources = step.get("resources", [])

    # Priority colors
    if "Essential" in priority:
        border_color = "#ef4444"
        badge_bg = "rgba(239,68,68,0.15)"
        badge_color = "#fca5a5"
    elif "Important" in priority:
        border_color = "#f59e0b"
        badge_bg = "rgba(245,158,11,0.15)"
        badge_color = "#fcd34d"
    else:
        border_color = "#22c55e"
        badge_bg = "rgba(34,197,94,0.15)"
        badge_color = "#86efac"

    # Resource links HTML
    res_links = ""
    for r in resources[:3]:
        type_icon = {"Course": "🎓", "YouTube": "▶️", "Documentation": "📚", "Interactive": "⚡", "Book": "📖", "Platform": "🌐"}.get(r.get("type", ""), "🔗")
        res_links += f"""
        <a href="{r.get('url','#')}" target="_blank"
           style="display:inline-flex;align-items:center;gap:6px;background:rgba(99,102,241,0.12);
                  border:1px solid rgba(99,102,241,0.25);border-radius:8px;padding:5px 12px;
                  text-decoration:none;color:#a5b4fc;font-size:0.78rem;margin:3px;
                  font-weight:500;transition:all 0.2s">
            {type_icon} {r.get('title','Resource')}
        </a>"""

    st.markdown(f"""
    <div style="display:flex;gap:16px;margin-bottom:16px">
        <!-- Step number circle -->
        <div style="min-width:44px;height:44px;border-radius:50%;
                    background:linear-gradient(135deg,#6366f1,#a855f7);
                    display:flex;align-items:center;justify-content:center;
                    font-weight:800;font-size:1rem;color:white;
                    flex-shrink:0;margin-top:4px">
            {step_num}
        </div>
        <!-- Card -->
        <div style="flex:1;background:#16213e;border:1px solid {border_color}44;
                    border-left:4px solid {border_color};border-radius:0 12px 12px 0;
                    padding:16px 20px">
            <div style="display:flex;align-items:center;justify-content:space-between;
                        gap:12px;flex-wrap:wrap;margin-bottom:8px">
                <div>
                    <h3 style="margin:0;color:#f1f5f9;font-size:1rem;font-weight:700">{skill}</h3>
                    <div style="color:#64748b;font-size:0.8rem;margin-top:2px">{reason}</div>
                </div>
                <div style="display:flex;gap:8px;align-items:center">
                    <span style="background:{badge_bg};color:{badge_color};font-size:0.72rem;
                                 padding:3px 10px;border-radius:10px;font-weight:600">{priority}</span>
                    <span style="background:rgba(99,102,241,0.1);color:#a5b4fc;font-size:0.72rem;
                                 padding:3px 10px;border-radius:10px">⏱️ {est_time}</span>
                </div>
            </div>
            <div style="margin-top:10px">
                <div style="color:#64748b;font-size:0.75rem;text-transform:uppercase;
                            letter-spacing:0.07em;margin-bottom:6px">Free Resources</div>
                <div style="line-height:2">{res_links}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_current_skills(tech_skills):
    st.markdown("### ✅ Your Current Skills")
    tags = "".join(f'<span class="cp-tag cp-tag-match">{s}</span>' for s in tech_skills)
    st.markdown(f'<div style="line-height:2.5">{tags}</div>', unsafe_allow_html=True)