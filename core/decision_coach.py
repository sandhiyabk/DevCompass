# core/decision_coach.py

import os
import json
import re
from string import Template
from groq import Groq
from dotenv import load_dotenv
from core.task_explainer import load_prompt, parse_json_safely

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_decision(
    time_stuck_minutes: int,
    approaches_tried: str,
    next_idea: str,
    user_data: dict
) -> dict:
    """
    Tell the fresher: ask senior or keep trying?
    """
    template = Template(load_prompt("decision_coach.txt"))

    prompt = template.substitute(
        role=user_data["role"],
        company_type=user_data["company_type"],
        days_at_company=user_data["days_at_company"],
        time_stuck_minutes=time_stuck_minutes,
        approaches_tried=approaches_tried,
        next_idea=next_idea
    )

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
            temperature=0.1,
            max_tokens=800
        )
        raw = response.choices[0].message.content
        result = parse_json_safely(raw)

        if "decision" not in result:
            result["decision"] = (
                "ask_senior"
                if time_stuck_minutes >= 45
                else "keep_trying"
            )

        return result

    except Exception as e:
        decision = (
            "ask_senior"
            if time_stuck_minutes >= 45
            else "keep_trying"
        )
        return {
            "decision": decision,
            "reasoning": f"Based on {time_stuck_minutes} minutes stuck.",
            "how_to_ask": "",
            "next_step": "Try a different approach."
        }
if __name__ == "__main__":
    import json

    print("Testing Decision Coach...")

    test_user = {
        "role": "Software Engineer",
        "days_at_company": 23,
        "company_type": "service"
    }

    # Test scenarios — should get different decisions
    scenarios = [
        {
            "name": "10 mins, one approach — should KEEP TRYING",
            "time_stuck_minutes": 10,
            "approaches_tried": "I tried restarting the server",
            "next_idea": "Maybe I should check the logs",
            "expected": "keep_trying"
        },
        {
            "name": "60 mins, two approaches — should ASK SENIOR",
            "time_stuck_minutes": 60,
            "approaches_tried": "Tried changing timeout value. Tried clearing cache. Both failed.",
            "next_idea": "Not sure what to try next",
            "expected": "ask_senior"
        },
        {
            "name": "35 mins, architecture question — should ASK SENIOR",
            "time_stuck_minutes": 35,
            "approaches_tried": "Read the existing code. Don't know if I should use microservices or monolith",
            "next_idea": "I think microservices but not sure",
            "expected": "ask_senior"
        },
        {
            "name": "20 mins, good next idea — borderline",
            "time_stuck_minutes": 20,
            "approaches_tried": "Checked the documentation",
            "next_idea": "I think the issue is in the JWT expiry setting in application.yml",
            "expected": "keep_trying"
        }
    ]

    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        try:
            result = get_decision(
                time_stuck_minutes=scenario["time_stuck_minutes"],
                approaches_tried=scenario["approaches_tried"],
                next_idea=scenario["next_idea"],
                user_data=test_user
            )

            decision = result.get("decision", "unknown")
            match = "✅" if decision == scenario["expected"] else "⚠️"

            print(f"  {match} Decision: {decision} (expected: {scenario['expected']})")
            print(f"  💭 Reasoning: {result.get('reasoning', '')[:100]}...")

            if decision == "ask_senior" and result.get("how_to_ask"):
                print(f"  💬 Script: {result['how_to_ask'][:100]}...")

        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n✅ Decision Coach test complete")