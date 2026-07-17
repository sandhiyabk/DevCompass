# core/reflection.py

import os
from groq import Groq
from dotenv import load_dotenv
from string import Template
from core.task_explainer import load_prompt, parse_json_safely

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def summarize_reflection(
    task_worked_on: str,
    what_confused: str,
    new_concept: str,
    confidence_score: int,
    user_data: dict
) -> dict:
    """
    Process end-of-day reflection.
    Extract concepts and create encouraging summary.
    """
    template = Template(load_prompt("reflection_summary.txt"))



    prompt = template.substitute(
        name=user_data.get("name", ""),
        role=user_data.get("role", ""),
        days_at_company=user_data.get("days_at_company", 0),
        task_worked_on=task_worked_on,
        what_confused=what_confused,
        new_concept=new_concept,
        confidence_score=confidence_score
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a warm, encouraging mentor. "
                               "Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )
        raw = response.choices[0].message.content
        return parse_json_safely(raw)

    except Exception as e:
        return {
            "summary": "Great job reflecting today!",
            "concepts": [new_concept] if new_concept else [],
            "encouragement": "Every day you learn something new.",
            "revision_reminder": new_concept or ""
        }
if __name__ == "__main__":
    import json

    print("Testing Reflection Summarizer...")

    test_user = {
        "name": "Sandhiya",
        "role": "Software Engineer",
        "days_at_company": 23
    }

    # Test different reflection scenarios
    test_reflections = [
        {
            "task_worked_on": "Fixed JWT authentication timeout bug",
            "what_confused": "How refresh tokens work vs access tokens",
            "new_concept": "JWT token lifecycle",
            "confidence_score": 3,
            "label": "Medium confidence day"
        },
        {
            "task_worked_on": "Wrote unit tests for payment module",
            "what_confused": "Mocking external API calls in tests",
            "new_concept": "Mockito framework for Java unit testing",
            "confidence_score": 2,
            "label": "Confused but learning day"
        },
        {
            "task_worked_on": "Optimized SQL query — reduced load time by 60%",
            "what_confused": "Nothing major today",
            "new_concept": "Database indexing strategies",
            "confidence_score": 5,
            "label": "High confidence day"
        }
    ]

    for test in test_reflections:
        label = test.pop("label")
        print(f"\n📔 Testing: {label}")

        try:
            result = summarize_reflection(
                task_worked_on=test["task_worked_on"],
                what_confused=test["what_confused"],
                new_concept=test["new_concept"],
                confidence_score=test["confidence_score"],
                user_data=test_user
            )

            required_keys = [
                "summary", "concepts",
                "encouragement", "revision_reminder"
            ]
            missing = [k for k in required_keys if k not in result]

            if missing:
                print(f"  ⚠️  Missing keys: {missing}")
            else:
                print(f"  ✅ Summary: {result['summary'][:100]}...")
                print(f"  📚 Concepts: {result['concepts']}")
                print(f"  💪 Encouragement: {result['encouragement']}")
                print(f"  🔄 Revise: {result['revision_reminder']}")

        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n✅ Reflection test complete")