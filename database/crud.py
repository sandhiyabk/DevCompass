# database/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, timedelta
from typing import List, Optional
from passlib.context import CryptContext
import uuid

from database.models import (
    User, UserSkill, DailyTask,
    StuckSession, Reflection,
    KnowledgeBase, WeeklyReport
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── USER CRUD ─────────────────────────────────────────────

def create_user(db: Session, data: dict) -> User:
    hashed = pwd_context.hash(data["password"])
    user = User(
        name=data["name"],
        email=data["email"],
        hashed_password=hashed,
        company_name=data.get("company_name"),
        company_type=data.get("company_type"),
        role=data.get("role"),
        tech_stack_at_work=data.get("tech_stack", []),
        personal_goal=data.get("personal_goal"),
        joined_company_date=data.get("joined_company_date")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(
    db: Session, user_id: str
) -> Optional[User]:
    return db.query(User).filter(
        User.id == user_id
    ).first()


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_all_users(db: Session) -> List[User]:
    return db.query(User).all()


# ─── SKILLS CRUD ───────────────────────────────────────────

def add_user_skills(
    db: Session,
    user_id: str,
    skills: List[dict]
) -> List[UserSkill]:
    skill_objects = []
    for skill in skills:
        skill_obj = UserSkill(
            user_id=user_id,
            skill_name=skill["name"],
            proficiency=skill["proficiency"],
            source="self-rated"
        )
        db.add(skill_obj)
        skill_objects.append(skill_obj)
    db.commit()
    return skill_objects


def get_user_skills(
    db: Session, user_id: str
) -> List[UserSkill]:
    return db.query(UserSkill).filter(
        UserSkill.user_id == user_id
    ).all()


def update_skill(
    db: Session,
    user_id: str,
    skill_name: str,
    proficiency: int
):
    skill = db.query(UserSkill).filter(
        UserSkill.user_id == user_id,
        UserSkill.skill_name == skill_name
    ).first()
    if skill:
        skill.proficiency = proficiency
        db.commit()


# ─── DAILY TASK CRUD ───────────────────────────────────────

def create_task(
    db: Session,
    user_id: str,
    task_input: str,
    ai_result: dict
) -> DailyTask:
    task = DailyTask(
        user_id=user_id,
        task_input=task_input,
        task_date=date.today(),
        what_is_this=ai_result.get("what_is_this", ""),
        skills_needed=ai_result.get("skills_needed", []),
        skill_gaps=ai_result.get("skill_gaps", []),
        skills_they_have=ai_result.get("skills_they_have", []),
        reading_order=ai_result.get("reading_order", []),
        before_touching_code=ai_result.get(
            "before_touching_code", []
        ),
        estimated_hours=ai_result.get("estimated_hours", 2),
        what_youll_learn=ai_result.get("what_youll_learn", "")
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_recent_tasks(
    db: Session,
    user_id: str,
    limit: int = 5
) -> List[DailyTask]:
    return db.query(DailyTask).filter(
        DailyTask.user_id == user_id
    ).order_by(desc(DailyTask.created_at)).limit(limit).all()


def get_todays_task(
    db: Session, user_id: str
) -> Optional[DailyTask]:
    return db.query(DailyTask).filter(
        DailyTask.user_id == user_id,
        DailyTask.task_date == date.today()
    ).first()


# ─── STUCK SESSION CRUD ────────────────────────────────────

def create_stuck_session(
    db: Session,
    user_id: str,
    data: dict,
    ai_result: dict
) -> StuckSession:
    session = StuckSession(
        user_id=user_id,
        task_id=data.get("task_id"),
        time_stuck_minutes=data["time_stuck_minutes"],
        approaches_tried=data["approaches_tried"],
        next_idea=data["next_idea"],
        ai_decision=ai_result.get("decision"),
        ai_reasoning=ai_result.get("reasoning"),
        how_to_ask=ai_result.get("how_to_ask"),
        next_step=ai_result.get("next_step")
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# ─── REFLECTION CRUD ───────────────────────────────────────

def create_reflection(
    db: Session,
    user_id: str,
    data: dict,
    ai_result: dict
) -> Reflection:
    reflection = Reflection(
        user_id=user_id,
        reflection_date=date.today(),
        task_worked_on=data["task_worked_on"],
        what_confused=data["what_confused"],
        new_concept=data["new_concept"],
        confidence_score=data["confidence_score"],
        ai_summary=ai_result.get("summary", ""),
        concepts_learned=ai_result.get("concepts", [])
    )
    db.add(reflection)
    db.commit()
    db.refresh(reflection)
    return reflection


def get_recent_reflections(
    db: Session,
    user_id: str,
    days: int = 7
) -> List[Reflection]:
    since = date.today() - timedelta(days=days)
    return db.query(Reflection).filter(
        Reflection.user_id == user_id,
        Reflection.reflection_date >= since
    ).order_by(desc(Reflection.reflection_date)).all()


def has_reflected_today(
    db: Session, user_id: str
) -> bool:
    return db.query(Reflection).filter(
        Reflection.user_id == user_id,
        Reflection.reflection_date == date.today()
    ).first() is not None


# ─── KNOWLEDGE BASE CRUD ───────────────────────────────────

def add_to_knowledge_base(
    db: Session,
    user_id: str,
    concept: str,
    learned_from: str,
    confidence: int = 3
) -> KnowledgeBase:
    from core.knowledge_base import calculate_next_revision

    existing = db.query(KnowledgeBase).filter(
        KnowledgeBase.user_id == user_id,
        KnowledgeBase.concept == concept
    ).first()

    if existing:
        existing.times_reviewed += 1
        existing.confidence = confidence
        existing.last_revised = date.today()
        existing.next_revision = calculate_next_revision(
            confidence, existing.times_reviewed
        )
        db.commit()
        return existing

    item = KnowledgeBase(
        user_id=user_id,
        concept=concept,
        learned_from=learned_from,
        confidence=confidence,
        times_reviewed=0,
        last_revised=date.today(),
        next_revision=calculate_next_revision(confidence, 0)
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_concepts_due_today(
    db: Session, user_id: str
) -> List[KnowledgeBase]:
    return db.query(KnowledgeBase).filter(
        KnowledgeBase.user_id == user_id,
        KnowledgeBase.next_revision <= date.today()
    ).all()


def get_all_knowledge(
    db: Session, user_id: str
) -> List[KnowledgeBase]:
    return db.query(KnowledgeBase).filter(
        KnowledgeBase.user_id == user_id
    ).order_by(desc(KnowledgeBase.created_at)).all()


# ─── WEEKLY REPORT CRUD ────────────────────────────────────

def create_weekly_report(
    db: Session,
    user_id: str,
    week_start: date,
    week_end: date,
    ai_report: str,
    metrics: dict
) -> WeeklyReport:
    report = WeeklyReport(
        user_id=user_id,
        week_start=week_start,
        week_end=week_end,
        tasks_completed=metrics.get("tasks_completed", 0),
        reflections_count=metrics.get("reflections_count", 0),
        stuck_sessions_count=metrics.get("stuck_sessions", 0),
        skills_grown=metrics.get("skills_grown", []),
        ai_report=ai_report,
        growth_score=metrics.get("growth_score", 0.0)
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_recent_reports(
    db: Session,
    user_id: str,
    limit: int = 8
) -> List[WeeklyReport]:
    return db.query(WeeklyReport).filter(
        WeeklyReport.user_id == user_id
    ).order_by(desc(WeeklyReport.created_at)).limit(limit).all()
if __name__ == "__main__":
    from database.connection import SessionLocal, init_db
    from datetime import date

    print("Testing CRUD operations...")
    init_db()
    db = SessionLocal()

    try:
        # Test 1: Create user
        print("\n1. Creating test user...")
        user = create_user(db, {
            "name": "Sandhiya BK",
            "email": "test_sandhiya@test.com",
            "password": "testpass123",
            "company_name": "Test Company",
            "company_type": "product",
            "role": "AI Engineer",
            "tech_stack": ["Python", "FastAPI", "LangChain"],
            "personal_goal": "Switch to AI roles",
            "joined_company_date": date(2026, 1, 1)
        })
        print(f"✅ User created: {user.name}, ID: {user.id}")
        print(f"   Days at company: {user.days_at_company}")

        # Test 2: Retrieve user
        print("\n2. Retrieving user by email...")
        found = get_user_by_email(db, "test_sandhiya@test.com")
        print(f"✅ Found: {found.name}")

        # Test 3: Verify password
        print("\n3. Verifying password...")
        valid = verify_password("testpass123", found.hashed_password)
        print(f"✅ Password valid: {valid}")

        # Test 4: Add skills
        print("\n4. Adding skills...")
        add_user_skills(db, str(user.id), [
            {"name": "Python", "proficiency": 4},
            {"name": "FastAPI", "proficiency": 3},
            {"name": "LangChain", "proficiency": 3},
            {"name": "SQL", "proficiency": 4}
        ])
        skills = get_user_skills(db, str(user.id))
        print(f"✅ Skills added: {[s.skill_name for s in skills]}")

        # Test 5: Create task
        print("\n5. Creating daily task...")
        task = create_task(
            db=db,
            user_id=str(user.id),
            task_input="Fix authentication timeout bug in Spring Boot",
            ai_result={
                "what_is_this": "Token refresh logic needs fixing",
                "skills_needed": ["JWT", "Spring Security"],
                "skill_gaps": ["JWT lifecycle"],
                "skills_they_have": ["Java basics"],
                "reading_order": ["AuthController.java", "JwtUtil.java"],
                "before_touching_code": [
                    "Run project locally",
                    "Reproduce the bug",
                    "Read error logs"
                ],
                "estimated_hours": 3,
                "what_youll_learn": "JWT is used in 78% of backend jobs"
            }
        )
        print(f"✅ Task created: {task.id}")

        # Test 6: Create reflection
        print("\n6. Creating reflection...")
        reflection = create_reflection(
            db=db,
            user_id=str(user.id),
            data={
                "task_worked_on": "Fixed authentication bug",
                "what_confused": "Token refresh flow",
                "new_concept": "JWT refresh tokens",
                "confidence_score": 3
            },
            ai_result={
                "summary": "Learned JWT token lifecycle today",
                "concepts": ["JWT", "Token refresh", "Spring Security"],
                "encouragement": "Great progress on authentication!",
                "revision_reminder": "JWT refresh tokens"
            }
        )
        print(f"✅ Reflection created: {reflection.id}")

        # Test 7: Knowledge base
        print("\n7. Testing knowledge base...")
        kb = add_to_knowledge_base(
            db=db,
            user_id=str(user.id),
            concept="JWT refresh tokens",
            learned_from="work task",
            confidence=3
        )
        print(f"✅ Knowledge added: {kb.concept}")
        print(f"   Next revision: {kb.next_revision}")

        # Test 8: Get concepts due today
        due = get_concepts_due_today(db, str(user.id))
        print(f"   Concepts due today: {len(due)}")

        print("\n✅ ALL CRUD TESTS PASSED")

    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup test user
        try:
            db.query(User).filter(
                User.email == "test_sandhiya@test.com"
            ).delete()
            db.commit()
            print("\n🧹 Test data cleaned up")
        except:
            pass
        db.close()