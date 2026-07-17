# core/task_explainer.py

import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from string import Template

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_prompt(filename: str) -> str:
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompts", filename
    )
    with open(prompt_path, "r") as f:
        return f.read()


def parse_json_safely(response: str) -> dict:
    clean = re.sub(r'```json|```', '', response).strip()
    match = re.search(r'\{.*\}', clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {
        "what_is_this": response[:300],
        "skills_needed": [],
        "skill_gaps": [],
        "skills_they_have": [],
        "reading_order": [],
        "before_touching_code": [],
        "estimated_hours": 2,
        "what_youll_learn": ""
    }


def explain_task(
    task_input: str,
    user_data: dict,
    user_skills: list
) -> dict:
    """
    Core feature: explain a work task to a fresher.
    """
    template = Template(load_prompt("task_explainer.txt"))

    skills_str = ", ".join([
        f"{s['name']} (level {s['proficiency']}/5)"
        for s in user_skills
    ]) if user_skills else "General programming basics"

    prompt = template.substitute(
    name=user_data["name"],
    role=user_data["role"],
    company_type=user_data["company_type"],
    days_at_company=user_data["days_at_company"],
    skills=skills_str,
    personal_goal=user_data["personal_goal"],
    task_input=task_input
)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software engineer. "
                               "Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        raw = response.choices[0].message.content
        return parse_json_safely(raw)

    except Exception as e:
        return {
            "what_is_this": f"Error analyzing task: {str(e)}",
            "skills_needed": [],
            "skill_gaps": [],
            "skills_they_have": [],
            "reading_order": [],
            "before_touching_code": [],
            "estimated_hours": 2,
            "what_youll_learn": ""
        }
if __name__ == "__main__":
    import json

    print("Testing Task Explainer...")

    # Sample user data
    test_user = {
        "name": "Sandhiya",
        "role": "Software Engineer",
        "company_type": "service",
        "days_at_company": 23,
        "personal_goal": "Switch to product company in 12 months"
    }

    # Sample skills
    test_skills = [
        {"name": "Python", "proficiency": 4},
        {"name": "SQL", "proficiency": 4},
        {"name": "Java", "proficiency": 2},
        {"name": "Spring Boot", "proficiency": 1}
    ]

    # Sample tasks to test
    test_tasks = [
        "Fix authentication timeout when user refreshes token — JIRA-4521",
        "Optimize the SQL query in UserRepository that is causing slow page load",
        "Write unit tests for the payment gateway integration module",
        "Debug null pointer exception in CustomerService.processOrder()"
    ]

    for i, task in enumerate(test_tasks, 1):
        print(f"\nTest {i}: {task[:50]}...")
        try:
            result = explain_task(task, test_user, test_skills)

            # Validate structure
            required_keys = [
                "what_is_this", "skills_needed", "skill_gaps",
                "reading_order", "before_touching_code",
                "estimated_hours", "what_youll_learn"
            ]

            missing = [k for k in required_keys if k not in result]
            if missing:
                print(f"  ⚠️  Missing keys: {missing}")
            else:
                print(f"  ✅ All keys present")
                print(f"  📝 What is this: {result['what_is_this'][:80]}...")
                print(f"  🎯 Skills needed: {result['skills_needed']}")
                print(f"  ⚠️  Skill gaps: {result['skill_gaps']}")
                print(f"  ⏱  Estimated: {result['estimated_hours']} hours")

        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n✅ Task Explainer test complete")