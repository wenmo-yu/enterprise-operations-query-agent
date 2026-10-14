"""
数仓 MySQL 仓储

这一层对应文档里的 DW Repository，职责是到真实数仓中补齐配置文件里
没有显式维护的信息，例如字段类型和字段示例值。Service 层只关心
“需要哪些信息”，具体怎样查数仓由仓储层统一封装
SQL 生成闭环中的数据库环境读取 SQL 校验和最终查询执行也集中放在这里
"""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlglot import exp, parse


class UnsafeSQL(Exception):
    """Raised when a generated statement is not one safe read-only query."""


class DWMySQLRepository:
    """负责查询数仓真实表结构和字段样例值"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        """查询整张表的字段类型，作为 ColumnInfo.type 的真实来源"""
        sql = f"show columns from {table_name}"
        result = await self.session.execute(text(sql))
        result_dict = result.mappings().fetchall()
        return {row["Field"]: row["Type"] for row in result_dict}

    async def get_column_values(
        self, table_name: str, column_name: str, limit: int = 10
    ) -> list:
        """抽样查询字段示例值，供元数据入库和后续检索链路复用"""
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        return [row[0] for row in result.fetchall()]

    async def get_db_info(self):
        """读取当前数仓数据库的方言和版本，供 SQL 生成提示词使用"""

        sql = "select version()"
        result = await self.session.execute(text(sql))
        version = result.scalar()

        # dialect 来自 SQLAlchemy 当前绑定的数据库方言，例如 mysql
        dialect = self.session.bind.dialect.name
        return {"dialect": dialect, "version": version}

    async def validate(self, sql: str):
        """用 EXPLAIN 让数据库提前解析 SQL，发现语法 表名 字段名等错误"""
        safe_sql = self._ensure_read_only(sql)
        await asyncio.wait_for(
            self.session.execute(text(f"explain {safe_sql}")),
            timeout=self.query_timeout_seconds,
        )

    async def run(self, sql: str) -> list[dict]:
        """Execute a parser-validated read query with timeout and row cap."""
        safe_sql = self._ensure_read_only(sql)
        result = await asyncio.wait_for(
            self.session.execute(text(safe_sql)), timeout=self.query_timeout_seconds
        )
        rows = result.mappings().fetchmany(self.max_rows)
        return [dict(row) for row in rows]

    @staticmethod
    def _ensure_read_only(sql: str) -> str:
        """Allow exactly one SELECT/CTE query and reject all executable side effects."""

        try:
            statements = parse(sql, read="mysql")
        except Exception as exc:
            raise UnsafeSQL("SQL 解析失败，仅允许单条只读查询") from exc
        if len(statements) != 1 or not isinstance(statements[0], exp.Query):
            raise UnsafeSQL("仅允许执行一条 SELECT 或 WITH 查询")
        statement = statements[0]
        forbidden = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Create,
            exp.Drop,
            exp.Alter,
            exp.Command,
        )
        if any(isinstance(node, forbidden) for node in statement.walk()):
            raise UnsafeSQL("检测到非只读 SQL 操作")
        if any(token in sql.lower() for token in ("into outfile", "into dumpfile", "load_file(")):
            raise UnsafeSQL("不允许文件读写相关 SQL")
        return statement.sql(dialect="mysql")
    max_rows = 1_000
    query_timeout_seconds = 15
