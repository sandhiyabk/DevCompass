# ui/pages/2_Im_Stuck.py

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)))

import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

if not st.session_state.get("logged_in"):
    st.warning("Please login first")
    st.stop()

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

st.title("🆘 I'm Stuck")
st.caption("Tell me about your situation. I'll tell you what to do.")

st.subheader("How stuck are you?")

time_stuck = st.slider(
    "How many minutes have you been stuck?",
    min_value=5, max_value=180, value=30, step=5
)

approaches = st.text_area(
    "What have you already tried?",
    placeholder="I tried changing the timeout value...\nI also tried...",
    height=120
)

next_idea = st.text_area(
    "What's your next idea?",
    placeholder="I was thinking maybe I should try...",
    height=80
)

if st.button("🤔 Should I Ask or Keep Trying?",
             type="primary", use_container_width=True):
    if approaches.strip():
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/stuck/decide",
                    json={
                        "time_stuck_minutes": time_stuck,
                        "approaches_tried": approaches,
                        "next_idea": next_idea
                    },
                    headers=get_headers(),
                    timeout=20
                )
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.stuck_result = result
                else:
                    st.error("Error getting decision")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please describe what you've tried")

if "stuck_result" in st.session_state:
    result = st.session_state.stuck_result
    decision = result.get("decision", "")

    st.divider()

    if decision == "ask_senior":
        st.error("## 🙋 Ask Your Senior")
    else:
        st.success("## 💪 Keep Trying")

    st.markdown("### Why?")
    st.write(result.get("reasoning", ""))

    if decision == "ask_senior" and result.get("how_to_ask"):
        st.markdown("### 💬 Exactly What To Say:")
        st.code(result["how_to_ask"], language=None)

    if result.get("next_step"):
        st.markdown("### ➡️ Your Next Action:")
        st.info(result["next_step"])