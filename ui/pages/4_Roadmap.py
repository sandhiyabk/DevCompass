# ui/pages/4_Roadmap.py

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)))

import streamlit as st
import requests

API_URL = os.getenv("API_URL") or st.secrets.get("API_URL", "http://localhost:8000")

if not st.session_state.get("logged_in"):
    st.warning("Please login first")
    st.stop()

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

st.title("🗺️ Your 90-Day Roadmap")
st.caption("Personalized based on your role, goal, and progress")

if st.button("🔄 Generate My Roadmap", type="primary"):
    with st.spinner("Creating your personalized roadmap..."):
        try:
            response = requests.get(
                f"{API_URL}/reports/roadmap",
                headers=get_headers(),
                timeout=30
            )
            if response.status_code == 200:
                st.session_state.roadmap = response.json()
            else:
                st.error("Error generating roadmap")
        except Exception as e:
            st.error(f"Error: {str(e)}")

if "roadmap" in st.session_state:
    roadmap = st.session_state.roadmap

    principle = roadmap.get("key_principle", "")
    if principle:
        st.info(f"**Core Principle:** {principle}")

    phases = ["phase_1", "phase_2", "phase_3"]
    icons = ["🌱", "🌿", "🌳"]

    for phase_key, icon in zip(phases, icons):
        phase = roadmap.get(phase_key, {})
        if phase:
            st.subheader(f"{icon} {phase.get('title', '')}")

            col1, col2 = st.columns(2)

            with col1:
                work_goals = phase.get("work_goals", [])
                if work_goals:
                    st.markdown("**Work goals:**")
                    for g in work_goals:
                        st.write(f"→ {g}")

            with col2:
                personal = phase.get("personal_learning", [])
                if personal:
                    st.markdown("**Personal learning:**")
                    for p in personal:
                        st.write(f"📚 {p}")

            mindset = phase.get("mindset", "")
            if mindset:
                st.caption(f"💭 {mindset}")

            st.divider()