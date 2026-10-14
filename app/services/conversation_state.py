"""Short-term conversation memory and structured analytics query state."""

import re
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from threading import RLock


@dataclass
class StructuredQueryState:
    """The reusable analytical intent for a single browser session."""

    metrics: list[str] = field(default_factory=list)
    time_range: str | None = None
    dimensions: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)
    sort: str | None = None
    limit: int | None = None


@dataclass
class ConversationSnapshot:
    session_id: str
    turns: deque[str] = field(default_factory=lambda: deque(maxlen=6))
    query_state: StructuredQueryState = field(default_factory=StructuredQueryState)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationStateStore:
    """Small in-process store; replace with Redis when deploying multiple replicas."""

    _metric_terms = ("收入", "利润", "利润率", "成本", "业务量", "客户数", "转化率", "流失率", "活跃用户数")
    _dimension_terms = ("区域", "部门", "渠道", "产品线", "业务单元", "客户类型", "时间", "月份", "季度")
    _filter_terms = ("华东", "华北", "华南", "华中", "北京", "上海", "重点客户", "新客户", "存量客户")

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationSnapshot] = {}
        self._lock = RLock()

    def hydrate(self, session_id: str, query: str) -> dict:
        with self._lock:
            snapshot = self._sessions.setdefault(session_id, ConversationSnapshot(session_id))
            state = snapshot.query_state
            # An omitted concept in a follow-up inherits the previous analytical intent.
            self._replace_or_merge(state.metrics, query, self._metric_terms)
            self._replace_or_merge(state.dimensions, query, self._dimension_terms)
            self._replace_or_merge(state.filters, query, self._filter_terms)
            time_range = self._extract_time(query)
            if time_range:
                state.time_range = time_range
            limit = self._extract_limit(query)
            if limit is not None:
                state.limit = limit
            sort = self._extract_sort(query)
            if sort:
                state.sort = sort
            context = list(snapshot.turns)
            snapshot.turns.append(query)
            snapshot.updated_at = datetime.now(timezone.utc)
            structured_query = asdict(state)
            return {
                "conversation_context": context,
                "structured_query": structured_query,
                "analysis_query": self._build_analysis_query(query, structured_query),
                "correction_attempts": 0,
            }

    def get(self, session_id: str) -> dict:
        with self._lock:
            snapshot = self._sessions.get(session_id)
            if not snapshot:
                return {"conversation_context": [], "structured_query": asdict(StructuredQueryState())}
            return {"conversation_context": list(snapshot.turns), "structured_query": asdict(snapshot.query_state)}

    @staticmethod
    def _replace_or_merge(target: list[str], query: str, candidates: tuple[str, ...]) -> None:
        matches = [item for item in candidates if item.lower() in query.lower()]
        if not matches:
            return
        if any(marker in query for marker in ("改成", "改为", "换成", "替换为")):
            target[:] = matches
            return
        for candidate in matches:
            if candidate not in target:
                target.append(candidate)

    @staticmethod
    def _extract_time(query: str) -> str | None:
        markers = ("年", "月", "季度", "本月", "本季度", "今年", "去年", "最近", "近")
        return query if any(marker in query for marker in markers) else None

    @staticmethod
    def _extract_limit(query: str) -> int | None:
        match = re.search(r"(?:前|top)\s*([0-9一二三四五六七八九十]+)\s*(?:名|个|条)?", query, re.IGNORECASE)
        if not match:
            return None
        value = match.group(1)
        if value.isdigit():
            return int(value)
        numerals = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
        if value == "十":
            return 10
        if "十" in value:
            tens, _, ones = value.partition("十")
            return numerals.get(tens, 1) * 10 + numerals.get(ones, 0)
        return numerals.get(value)

    @staticmethod
    def _extract_sort(query: str) -> str | None:
        if any(token in query for token in ("最低", "最小", "升序", "从低到高")):
            return "ascending"
        if any(token in query for token in ("最高", "最大", "降序", "从高到低")):
            return "descending"
        return None

    @staticmethod
    def _build_analysis_query(query: str, state: dict) -> str:
        """Give retrieval the complete inherited intent, while preserving the raw user text."""

        constraints = []
        for key, label in (("metrics", "指标"), ("time_range", "时间"), ("dimensions", "维度"), ("filters", "筛选")):
            value = state.get(key)
            if value:
                constraints.append(f"{label}：{', '.join(value) if isinstance(value, list) else value}")
        if state.get("sort"):
            constraints.append(f"排序：{state['sort']}")
        if state.get("limit"):
            constraints.append(f"Top-N：{state['limit']}")
        return f"{query}\n继承的完整分析意图：{'；'.join(constraints)}" if constraints else query


conversation_state_store = ConversationStateStore()
