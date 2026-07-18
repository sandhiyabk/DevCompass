# ui/pages/1_Daily_Task.py

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

st.title("🎯 Daily Task")
st.caption(f"Welcome, {st.session_state.get('user_name', '')}!")

st.subheader("What's your work task today?")
task_input = st.text_area(
    "Paste your Jira ticket, task description, or bug report",
    height=150,
    placeholder="""Fix authentication timeout when user refreshes token.
                   
JIRA-4521: Users are getting logged out randomly..."""
)

if st.button("🔍 Explain This Task", type="primary",
             use_container_width=True):
    if task_input.strip():
        with st.spinner("Analyzing your task..."):
            try:
                response = requests.post(
                    f"{API_URL}/tasks/explain",
                    json={"task_text": task_input},
                    headers=get_headers(),
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.task_result = result
                else:
                    st.error("Error analyzing task")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter your task first")

# Display result
if "task_result" in st.session_state:
    result = st.session_state.task_result

    st.divider()
    st.subheader("📋 Task Breakdown")

    st.markdown("### 💡 What Is This Asking?")
    st.info(result.get("what_is_this", ""))

    col1, col2 = st.columns(2)

    with col1:
        skills_needed = result.get("skills_needed", [])
        if skills_needed:
            st.markdown("### 🎯 Skills This Needs")
            for skill in skills_needed:
                st.write(f"→ {skill}")

    with col2:
        gaps = result.get("skill_gaps", [])
        if gaps:
            st.markdown("### ⚠️ Your Skill Gaps")
            for gap in gaps:
                st.error(f"❌ {gap}")

        have = result.get("skills_they_have", [])
        if have:
            st.markdown("### ✅ You Already Have")
            for skill in have:
                st.success(f"✅ {skill}")

    reading = result.get("reading_order", [])
    if reading:
        st.markdown("### 📖 Where To Start Reading")
        for i, file in enumerate(reading, 1):
            st.write(f"{i}. {file}")

    checklist = result.get("before_touching_code", [])
    if checklist:
        st.markdown("### ✅ Before Touching Code")
        for item in checklist:
            st.checkbox(item, key=f"check_{item[:20]}")

    hours = result.get("estimated_hours")
    if hours:
        st.metric("⏱ Estimated Time", f"{hours} hours")

    learn = result.get("what_youll_learn", "")
    if learn:
        st.markdown("### 🚀 What You'll Learn")
        st.success(learn)

st.divider()

# Recent tasks
with st.expander("📚 Recent Tasks"):
    try:
        response = requests.get(
            f"{API_URL}/tasks/recent",
            headers=get_headers()
        )
        if response.status_code == 200:
            tasks = response.json()
            for task in tasks:
                st.write(f"**{task['task_date']}:** "
                        f"{task['task_input'][:80]}...")
    except:
        st.write("Could not load recent tasks")