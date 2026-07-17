# core/weekly_report.py

import os
from string import Template
from datetime import date, timedelta
from groq import Groq
from dotenv import load_dotenv
from sqlalchemy.orm import Session, DeclarativeBase
from core.task_explainer import load_prompt, parse_json_safely
from database import crud

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_weekly_report(
    db: Session,
    user_id: str
) -> dict:
    """Generate weekly growth report for a user."""

    user = crud.get_user_by_id(db, user_id)
    if not user:
        return {}

    week_start = date.today() - timedelta(days=7)
    week_end = date.today()

    # Gather this week's data
    recent_tasks = crud.get_recent_tasks(db, user_id, limit=20)
    week_tasks = [
        t for t in recent_tasks
        if t.task_date and t.task_date >= week_start
    ]

    recent_reflections = crud.get_recent_reflections(
        db, user_id, days=7
    )

    all_knowledge = crud.get_all_knowledge(db, user_id)
    new_concepts = [
        k.concept for k in all_knowledge
        if k.created_at.date() >= week_start
    ] if all_knowledge else []

    # Build metrics
    metrics = {
        "tasks_completed": len(week_tasks),
        "reflections_count": len(recent_reflections),
        "stuck_sessions": 0,
        "concepts_learned": new_concepts,
        "skills_grown": new_concepts[:5],
        "growth_score": min(
            10.0,
            (len(week_tasks) * 1.5) +
            (len(recent_reflections) * 2.0) +
            (len(new_concepts) * 1.0)
        )
    }

    # Generate AI report
    concepts_str = ", ".join(new_concepts) if new_concepts else "General skills"

    template = load_prompt("weekly_report.txt")
    prompt = Template(template).safe_substitute(
        name=user.name,
        role=user.role or "Software Engineer",
        days_at_company=user.days_at_company,
        personal_goal=user.personal_goal or "Grow as an engineer",
        tasks_completed=metrics["tasks_completed"],
        reflections_count=metrics["reflections_count"],
        stuck_sessions=metrics["stuck_sessions"],
        concepts_learned=concepts_str
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a career mentor. "
                               "Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        raw = response.choices[0].message.content
        ai_result = parse_json_safely(raw)

    except Exception as e:
        ai_result = {
            "headline": f"Week {user.days_at_company // 7} complete.",
            "what_you_did": [f"Completed {metrics['tasks_completed']} tasks"],
            "what_you_learned": new_concepts[:3],
            "honest_assessment": "Keep building momentum.",
            "next_week_focus": ["Continue current pace"],
            "growth_score": metrics["growth_score"],
            "motivational_close": "You're doing well."
        }

    # Save to database
    crud.create_weekly_report(
        db=db,
        user_id=user_id,
        week_start=week_start,
        week_end=week_end,
        ai_report=str(ai_result),
        metrics=metrics
    )

    return {**ai_result, **metrics}


def generate_all_weekly_reports(db: Session):
    """Called by APScheduler every Sunday."""
    users = crud.get_all_users(db)
    for user in users:
        try:
            generate_weekly_report(db, str(user.id))
            print(f"Report generated for {user.name}")
        except Exception as e:
            print(f"Failed for {user.name}: {e}")

if __name__ == "__main__":
    from database.connection import SessionLocal, init_db
    from database import crud
    from datetime import date

    print("Testing Weekly Report Generator...")

    init_db()
    db = SessionLocal()

    try:
        # Create test user first (delete if exists from previous run)
        existing = crud.get_user_by_email(db, "report_test@test.com")
        if existing:
            uid = str(existing.id)
            db.query(crud.KnowledgeBase).filter(crud.KnowledgeBase.user_id == uid).delete(synchronize_session=False)
            db.query(crud.WeeklyReport).filter(crud.WeeklyReport.user_id == uid).delete(synchronize_session=False)
            db.query(crud.Reflection).filter(crud.Reflection.user_id == uid).delete(synchronize_session=False)
            db.query(crud.StuckSession).filter(crud.StuckSession.user_id == uid).delete(synchronize_session=False)
            db.query(crud.DailyTask).filter(crud.DailyTask.user_id == uid).delete(synchronize_session=False)
            db.query(crud.UserSkill).filter(crud.UserSkill.user_id == uid).delete(synchronize_session=False)
            db.query(crud.User).filter(crud.User.email == "report_test@test.com").delete(synchronize_session=False)
            db.commit()

        user = crud.create_user(db, {
            "name": "Report Test User",
            "email": "report_test@test.com",
            "password": "test123",
            "company_type": "service",
            "role": "Software Engineer",
            "personal_goal": "Switch to product company",
            "joined_company_date": date(2026, 6, 1)
        })

        # Add some test data
        crud.add_to_knowledge_base(
            db, str(user.id), "JWT tokens",
            "work task", confidence=3
        )
        crud.add_to_knowledge_base(
            db, str(user.id), "SQL indexing",
            "work task", confidence=4
        )

        print("Generating weekly report...")
        report = generate_weekly_report(db, str(user.id))

        if report:
            print(f"✅ Headline: {report.get('headline', '')}")
            print(f"✅ Growth score: {report.get('growth_score', 0)}")
            print(f"✅ Learned: {report.get('what_you_learned', [])}")
            print(f"✅ Assessment: {report.get('honest_assessment', '')[:100]}...")
        else:
            print("⚠️  Empty report returned")

        print("\n✅ Weekly report test complete")

    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        try:
            db.rollback()
            existing = crud.get_user_by_email(db, "report_test@test.com")
            if existing:
                uid = str(existing.id)
                db.query(crud.KnowledgeBase).filter(crud.KnowledgeBase.user_id == uid).delete(synchronize_session=False)
                db.query(crud.WeeklyReport).filter(crud.WeeklyReport.user_id == uid).delete(synchronize_session=False)
                db.query(crud.Reflection).filter(crud.Reflection.user_id == uid).delete(synchronize_session=False)
                db.query(crud.StuckSession).filter(crud.StuckSession.user_id == uid).delete(synchronize_session=False)
                db.query(crud.DailyTask).filter(crud.DailyTask.user_id == uid).delete(synchronize_session=False)
                db.query(crud.UserSkill).filter(crud.UserSkill.user_id == uid).delete(synchronize_session=False)
                db.query(crud.User).filter(crud.User.email == "report_test@test.com").delete(synchronize_session=False)
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
        print("🧹 Cleaned up")
