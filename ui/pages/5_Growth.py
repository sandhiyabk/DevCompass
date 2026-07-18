# ui/pages/5_Growth.py

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)))

import streamlit as st
import requests
import plotly.graph_objects as go

API_URL = os.getenv("API_URL") or st.secrets.get("API_URL", "http://localhost:8000")

if not st.session_state.get("logged_in"):
    st.warning("Please login first")
    st.stop()

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

st.title("📈 Growth Dashboard")
st.caption("Your engineering journey in numbers")

# Weekly report button
col1, col2 = st.columns(2)

with col1:
    if st.button(
        "📊 Generate Weekly Report", type="primary",
        use_container_width=True
    ):
        with st.spinner("Generating your report..."):
            try:
                response = requests.get(
                    f"{API_URL}/reports/weekly",
                    headers=get_headers(),
                    timeout=30
                )
                if response.status_code == 200:
                    st.session_state.weekly_report = response.json()
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col2:
    if st.button(
        "📚 View Report History", use_container_width=True
    ):
        try:
            response = requests.get(
                f"{API_URL}/reports/history",
                headers=get_headers()
            )
            if response.status_code == 200:
                st.session_state.report_history = response.json()
        except:
            pass

# Weekly report display
if "weekly_report" in st.session_state:
    report = st.session_state.weekly_report

    st.divider()
    st.subheader("This Week's Report")

    headline = report.get("headline", "")
    if headline:
        st.markdown(f"### {headline}")

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Tasks Completed", report.get("tasks_completed", 0))
    c2.metric("Reflections Written", report.get("reflections_count", 0))
    c3.metric(
        "Growth Score",
        f"{report.get('growth_score', 0):.1f}/10"
    )

    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=report.get("growth_score", 0),
        title={"text": "Weekly Growth Score"},
        gauge={
            "axis": {"range": [0, 10]},
            "bar": {"color": "#6366f1"},
            "steps": [
                {"range": [0, 4], "color": "#ef4444"},
                {"range": [4, 7], "color": "#f59e0b"},
                {"range": [7, 10], "color": "#10b981"}
            ]
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        what_you_did = report.get("what_you_did", [])
        if what_you_did:
            st.markdown("### ✅ What You Did")
            for item in what_you_did:
                st.write(f"→ {item}")

        learned = report.get("what_you_learned", [])
        if learned:
            st.markdown("### 🧠 What You Learned")
            for item in learned:
                st.write(f"→ {item}")

    with col2:
        assessment = report.get("honest_assessment", "")
        if assessment:
            st.markdown("### 🔍 Honest Assessment")
            st.info(assessment)

        next_week = report.get("next_week_focus", [])
        if next_week:
            st.markdown("### 🎯 Next Week Focus")
            for item in next_week:
                st.write(f"→ {item}")

    close = report.get("motivational_close", "")
    if close:
        st.success(f"💪 {close}")

# History chart
if "report_history" in st.session_state:
    history = st.session_state.report_history

    if len(history) > 1:
        st.divider()
        st.subheader("Growth Over Time")

        weeks = [r.get("week_start", "") for r in history]
        scores = [r.get("growth_score", 0) for r in history]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weeks[::-1],
            y=scores[::-1],
            mode="lines+markers",
            name="Growth Score",
            line=dict(color="#6366f1", width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title="Weekly Growth Score Trend",
            xaxis_title="Week",
            yaxis_title="Score (0-10)",
            template="plotly_dark",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)