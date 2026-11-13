from app.models import Segment
from app.services.rules import matches


def is_member(segment: Segment, context: dict) -> bool:
    """Whether this user's attributes put them in this segment."""
    return matches(segment.operator, context.get(segment.attribute), segment.value)


def any_segment_matches(segments: list[Segment], context: dict) -> bool:
    """A flag targeted at segments applies to a user in all of them."""
    if not segments:
        return True
    return any(is_member(segment, context) for segment in segments)
