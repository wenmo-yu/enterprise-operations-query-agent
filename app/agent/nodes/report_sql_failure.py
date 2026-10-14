"""Emit a final, user-visible failure after the bounded SQL repair attempt."""

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def report_sql_failure(
    state: DataAgentState, runtime: Runtime[DataAgentContext]
):
    runtime.stream_writer(
        {
            "type": "error",
            "message": f"SQL 在一次自动修正后仍未通过预检查：{state['error']}",
        }
    )
