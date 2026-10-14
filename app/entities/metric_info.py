"""
指标元数据业务实体

用于表达一个业务指标的名称 说明 别名以及它依赖的底层字段
后续写入 Meta MySQL 和 Qdrant 时都会复用这份统一的业务对象
"""

from dataclasses import dataclass


@dataclass
class MetricInfo:
    """系统内部统一使用的指标元数据表达"""

    id: str
    name: str
    description: str
    # 指标依赖的底层字段列表，例如收入依赖业务事实表的金额字段
    relevant_columns: list[str]
    alias: list[str]
