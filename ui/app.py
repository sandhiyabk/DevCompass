# ui/app.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests

API_URL = os.getenv("API_URL") or st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="DevCompass",
    page_icon="🧭",
    layout="centered"
)

# Check if already logged in
if st.session_state.get("logged_in"):
    st.switch_page("pages/1_Daily_Task.py")

st.title("🧭 DevCompass")
st.caption("AI Work Companion for IT Freshers")
st.divider()

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    st.subheader("Welcome back")
    email = st.text_input("Email", key="login_email")
    password = st.text_input(
        "Password", type="password", key="login_pass"
    )

    if st.button("Login", type="primary", use_container_width=True):
        if email and password:
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    data={"username": email, "password": password}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user_name = data["user_name"]
                    st.session_state.user_id = data["user_id"]
                    st.session_state.logged_in = True
                    st.success(f"Welcome back, {data['user_name']}!")
                    st.switch_page("pages/1_Daily_Task.py")
                else:
                    st.error("Invalid email or password")
            except Exception as e:
                st.error(f"Cannot connect to API: {str(e)}")

with tab2:
    st.subheader("Create your profile")

    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Email")
            reg_password = st.text_input("Password", type="password")
            reg_company = st.text_input("Company Name")

        with col2:
            reg_company_type = st.selectbox(
                "Company Type",
                ["service", "product", "startup"]
            )
            reg_role = st.text_input(
                "Your Role",
                placeholder="e.g. Software Engineer"
            )
            reg_joined = st.date_input("Date Joined Company")
            reg_goal = st.selectbox(
                "Personal Goal",
                [
                    "Grow at current company",
                    "Switch to product company in 12 months",
                    "Move into AI/ML roles",
                    "Start my own startup eventually"
                ]
            )

        # Skills
        st.subheader("Rate your current skills (1=beginner, 5=advanced)")
        common_skills = [
            "Python", "Java", "SQL", "JavaScript",
            "C++", "Data Structures", "System Design",
            "Git", "Linux", "Docker"
        ]

        skill_cols = st.columns(5)
        skills_inputs = {}
        for i, skill in enumerate(common_skills):
            with skill_cols[i % 5]:
                skills_inputs[skill] = st.selectbox(
                    skill, [0, 1, 2, 3, 4, 5],
                    key=f"skill_{skill}"
                )

        submitted = st.form_submit_button(
            "Create Profile", type="primary", use_container_width=True
        )

    if submitted:
        skills_data = [
            {"name": skill, "proficiency": level}
            for skill, level in skills_inputs.items()
            if level > 0
        ]
        if reg_name and reg_email and reg_password and reg_role:
            try:
                payload = {
                    "name": reg_name,
                    "email": reg_email,
                    "password": reg_password,
                    "company_name": reg_company,
                    "company_type": reg_company_type,
                    "role": reg_role,
                    "personal_goal": reg_goal,
                    "joined_company_date": str(reg_joined),
                    "skills": skills_data
                }
                response = requests.post(
                    f"{API_URL}/auth/register",
                    json=payload
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user_name = data["user_name"]
                    st.session_state.user_id = data["user_id"]
                    st.session_state.logged_in = True
                    st.success("Profile created! Welcome to DevCompass.")
                    st.switch_page("pages/1_Daily_Task.py")
                else:
                    st.error(response.json().get("detail", "Error"))
            except Exception as e:
                st.error(f"Cannot connect to API: {str(e)}")
        else:
            st.warning("Please fill all required fields: Name, Email, Password, and Role are required.")