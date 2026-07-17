# api/routes/reflections.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database import crud
from core.reflection import summarize_reflection
from api.routes.auth import get_current_user

router = APIRouter(prefix="/reflect", tags=["reflections"])


class ReflectionInput(BaseModel):
    task_worked_on: str
    what_confused: str
    new_concept: str
    confidence_score: int  # 1-5


@router.post("/submit")
def submit_reflection(
    data: ReflectionInput,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if crud.has_reflected_today(db, str(current_user.id)):
        raise HTTPException(
            status_code=400,
            detail="Already reflected today"
        )

    user_data = {
        "name": current_user.name,
        "role": current_user.role,
        "days_at_company": current_user.days_at_company
    }

    ai_result = summarize_reflection(
        task_worked_on=data.task_worked_on,
        what_confused=data.what_confused,
        new_concept=data.new_concept,
        confidence_score=data.confidence_score,
        user_data=user_data
    )

    reflection = crud.create_reflection(
        db, str(current_user.id), data.dict(), ai_result
    )

    # Add to knowledge base
    for concept in ai_result.get("concepts", []):
        if concept:
            crud.add_to_knowledge_base(
                db=db,
                user_id=str(current_user.id),
                concept=concept,
                learned_from="work task",
                confidence=data.confidence_score
            )

    return {
        "reflection_id": str(reflection.id),
        **ai_result
    }


@router.get("/knowledge")
def get_knowledge(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = crud.get_all_knowledge(db, str(current_user.id))
    due_today = crud.get_concepts_due_today(
        db, str(current_user.id)
    )

    return {
        "total_concepts": len(items),
        "due_for_revision": [i.concept for i in due_today],
        "knowledge_base": [
            {
                "concept": i.concept,
                "confidence": i.confidence,
                "learned_from": i.learned_from,
                "next_revision": str(i.next_revision)
            }
            for i in items
        ]
    }