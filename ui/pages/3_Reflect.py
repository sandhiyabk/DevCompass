# ui/pages/3_Reflect.py

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

st.title("📔 Daily Reflection")
st.caption("3 minutes. Builds your knowledge base.")

st.subheader("End of day check-in")

task_worked = st.text_area(
    "What task did you work on today?",
    placeholder="Fixed the authentication timeout bug...",
    height=80
)

what_confused = st.text_area(
    "What confused you most today?",
    placeholder="I didn't understand why the token was expiring...",
    height=80
)

new_concept = st.text_input(
    "One new concept you encountered today",
    placeholder="JWT refresh tokens"
)

confidence = st.slider(
    "Confidence score — how well do you understand today's work?",
    min_value=1, max_value=5, value=3,
    help="1=Very confused, 3=Getting there, 5=Got it completely"
)

confidence_labels = {
    1: "😰 Very confused",
    2: "😕 Somewhat confused",
    3: "🙂 Getting there",
    4: "😊 Pretty good",
    5: "😄 Got it!"
}
st.write(confidence_labels.get(confidence, ""))

if st.button(
    "📝 Submit Reflection", type="primary", use_container_width=True
):
    if task_worked.strip() and new_concept.strip():
        with st.spinner("Processing your reflection..."):
            try:
                response = requests.post(
                    f"{API_URL}/reflect/submit",
                    json={
                        "task_worked_on": task_worked,
                        "what_confused": what_confused,
                        "new_concept": new_concept,
                        "confidence_score": confidence
                    },
                    headers=get_headers(),
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.reflect_result = result
                elif response.status_code == 400:
                    st.warning("Already reflected today!")
                else:
                    st.error("Error submitting reflection")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please fill in the task and new concept fields")

if "reflect_result" in st.session_state:
    result = st.session_state.reflect_result
    st.divider()
    st.subheader("✨ Today's Learning Summary")
    st.info(result.get("summary", ""))
    st.success(result.get("encouragement", ""))

    concepts = result.get("concepts", [])
    if concepts:
        st.markdown("**Stored in your knowledge base:**")
        for c in concepts:
            st.write(f"→ {c}")

    if result.get("revision_reminder"):
        st.markdown(
            f"**Reminder in 7 days:** Revise "
            f"*{result['revision_reminder']}*"
        )

# Knowledge base
st.divider()
with st.expander("🧠 Your Knowledge Base"):
    try:
        response = requests.get(
            f"{API_URL}/reflect/knowledge",
            headers=get_headers()
        )
        if response.status_code == 200:
            data = response.json()
            st.metric(
                "Total Concepts Learned",
                data.get("total_concepts", 0)
            )

            due = data.get("due_for_revision", [])
            if due:
                st.warning(
                    f"Due for revision today: {', '.join(due)}"
                )

            for item in data.get("knowledge_base", [])[:10]:
                col1, col2 = st.columns([3, 1])
                col1.write(f"→ {item['concept']}")
                col2.write(f"⭐ {item['confidence']}/5")
    except:
        st.write("Could not load knowledge base")