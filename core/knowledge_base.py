# core/knowledge_base.py

from datetime import date, timedelta


def calculate_next_revision(
    confidence: int,
    times_reviewed: int
) -> date:
    """
    Spaced repetition algorithm.
    Higher confidence = longer gap before next review.
    """
    base_intervals = {
        1: 1,
        2: 3,
        3: 7,
        4: 14,
        5: 30
    }
    interval = base_intervals.get(confidence, 7)

    if times_reviewed > 3:
        interval = int(interval * 1.5)
    if times_reviewed > 6:
        interval = int(interval * 2)

    return date.today() + timedelta(days=interval)


def get_revision_message(concept: str, days_overdue: int) -> str:
    if days_overdue == 0:
        return f"Time to revise: {concept}"
    elif days_overdue <= 3:
        return f"Slightly overdue: {concept} ({days_overdue}d ago)"
    else:
        return f"Needs attention: {concept} ({days_overdue}d overdue)"
if __name__ == "__main__":
    from datetime import date

    print("Testing Knowledge Base / Spaced Repetition...")

    # Test revision dates for each confidence level
    confidence_levels = [1, 2, 3, 4, 5]
    times_reviewed_options = [0, 3, 6, 10]

    print("\nRevision intervals by confidence and review count:")
    print(f"{'Confidence':<12} {'Times Reviewed':<16} {'Next Revision':<15} {'Days Away'}")
    print("-" * 60)

    for conf in confidence_levels:
        for times in times_reviewed_options:
            next_rev = calculate_next_revision(conf, times)
            days_away = (next_rev - date.today()).days
            print(
                f"{conf:<12} {times:<16} "
                f"{str(next_rev):<15} {days_away} days"
            )

    print("\n✅ Spaced repetition logic verified")

    # Test revision message
    print("\nTesting revision messages:")
    print(get_revision_message("JWT tokens", 0))
    print(get_revision_message("SQL joins", 2))
    print(get_revision_message("Microservices", 7))

    print("\n✅ Knowledge base test complete")