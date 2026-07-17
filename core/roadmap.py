# core/roadmap.py

import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from core.task_explainer import parse_json_safely

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_roadmap(
    user_data: dict,
    user_skills: list,
    recent_concepts: list
) -> dict:
    """Generate adaptive 90-day roadmap."""

    skills_str = ", ".join([
        f"{s['name']} ({s['proficiency']}/5)"
        for s in user_skills
    ]) if user_skills else "Basic programming"

    recent_str = ", ".join(
        recent_concepts[:10]
    ) if recent_concepts else "None yet"

    prompt = f"""
You are a senior engineer creating a personalized 90-day roadmap.

Profile:
- Role: {user_data.get('role', 'Software Engineer')}
- Company type: {user_data.get('company_type', 'service')}
- Days at company: {user_data.get('days_at_company', 0)}
- Personal goal: {user_data.get('personal_goal', 'grow as engineer')}
- Current skills: {skills_str}
- Recently learned at work: {recent_str}

Create a realistic, balanced roadmap.
Split between work skills (60%) and personal growth (40%).

Return ONLY valid JSON:
{{
    "phase_1": {{
        "title": "Days 1-30: Survive and Observe",
        "work_goals": ["goal1", "goal2"],
        "personal_learning": ["skill1 - 1hr/day", "skill2"],
        "mindset": "one encouraging sentence for this phase"
    }},
    "phase_2": {{
        "title": "Days 31-60: Start Contributing",
        "work_goals": ["goal1", "goal2"],
        "personal_learning": ["skill1", "skill2"],
        "mindset": "one encouraging sentence"
    }},
    "phase_3": {{
        "title": "Days 61-90: Build Your Reputation",
        "work_goals": ["goal1", "goal2"],
        "personal_learning": ["skill1", "skill2"],
        "mindset": "one encouraging sentence"
    }},
    "key_principle": "one overarching principle for first 90 days"
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior engineer mentor. "
                               "Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        raw = response.choices[0].message.content
        return parse_json_safely(raw)

    except Exception as e:
        return {
            "phase_1": {
                "title": "Days 1-30: Survive and Observe",
                "work_goals": ["Learn your codebase", "Fix small bugs"],
                "personal_learning": ["DSA basics", "Your tech stack"],
                "mindset": "Feeling lost is normal and expected."
            },
            "phase_2": {
                "title": "Days 31-60: Start Contributing",
                "work_goals": ["Own a small module", "Suggest improvements"],
                "personal_learning": ["Build one small project"],
                "mindset": "Start having opinions."
            },
            "phase_3": {
                "title": "Days 61-90: Build Your Reputation",
                "work_goals": ["Document things", "Help teammates"],
                "personal_learning": ["Deploy your personal project"],
                "mindset": "Your reputation is built in these months."
            },
            "key_principle": "Every work task is a learning opportunity."
        }
if __name__ == "__main__":
    import json

    print("Testing Roadmap Generator...")

    # Test different user profiles
    test_profiles = [
        {
            "label": "Service company fresher — wants to switch",
            "user_data": {
                "role": "Software Engineer",
                "company_type": "service",
                "days_at_company": 30,
                "personal_goal": "Switch to product company in 12 months"
            },
            "skills": [
                {"name": "Java", "proficiency": 2},
                {"name": "SQL", "proficiency": 3}
            ],
            "recent_concepts": ["Spring Boot basics", "REST APIs"]
        },
        {
            "label": "Product company fresher — wants to grow",
            "user_data": {
                "role": "AI Engineer",
                "company_type": "product",
                "days_at_company": 15,
                "personal_goal": "Grow into senior AI engineer role"
            },
            "skills": [
                {"name": "Python", "proficiency": 4},
                {"name": "LangChain", "proficiency": 3}
            ],
            "recent_concepts": ["RAG systems", "LLM APIs"]
        }
    ]

    for profile in test_profiles:
        label = profile["label"]
        print(f"\n📍 Profile: {label}")

        try:
            roadmap = generate_roadmap(
                user_data=profile["user_data"],
                user_skills=profile["skills"],
                recent_concepts=profile["recent_concepts"]
            )

            required_keys = ["phase_1", "phase_2", "phase_3", "key_principle"]
            missing = [k for k in required_keys if k not in roadmap]

            if missing:
                print(f"  ⚠️  Missing: {missing}")
            else:
                print(f"  ✅ Phase 1: {roadmap['phase_1'].get('title', '')}")
                print(f"  ✅ Phase 2: {roadmap['phase_2'].get('title', '')}")
                print(f"  ✅ Phase 3: {roadmap['phase_3'].get('title', '')}")
                print(f"  💡 Principle: {roadmap['key_principle']}")

                # Check work goals exist
                p1_goals = roadmap['phase_1'].get('work_goals', [])
                print(f"  📋 Phase 1 goals: {len(p1_goals)} items")

        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n✅ Roadmap test complete")