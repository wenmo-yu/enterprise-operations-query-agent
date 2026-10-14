"""Candidate-sizing helpers shared by metadata retrieval nodes."""


def dynamic_top_k(query: str, minimum: int = 6, maximum: int = 20) -> int:
    """Broaden recall for multi-constraint questions while capping prompt noise."""

    constraints = sum(
        query.count(token) for token in ("按", "和", "、", "以及", "同比", "环比")
    )
    return min(maximum, minimum + constraints * 3 + len(query) // 24)
