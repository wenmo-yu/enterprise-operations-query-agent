# Evaluation

本说明记录 README 中的评测口径，避免将检索质量、SQL 执行准确率和修正收益混为同一指标。

## BIRD Mini-Dev

| Item | Setting |
| --- | --- |
| Model | DeepSeek-V4-Pro |
| Dataset | BIRD Mini-Dev |
| Samples | 500 |
| Primary metric | Execution Accuracy |
| External knowledge | 未使用 BIRD external knowledge |
| Self-Correction | 最多 1 次；修正后必须重新预检查 |

| Pipeline | Execution Accuracy |
| --- | ---: |
| Raw Schema Baseline | 57.4% |
| + Schema RAG | 74.2% |
| + Limited Self-Correction | 77.0% |

**Baseline 定义**：Raw Schema Baseline 仅提供原始表与字段结构，不启用向量检索、字段值召回、Schema Dependency Expansion 或 SQL 修正。

## Schema Retrieval

| Metric | Score |
| --- | ---: |
| Schema Recall@5 | 93.6% |

Recall@5 以问题所需的表/字段是否出现在前 5 个 Schema 候选中计算；它衡量检索覆盖，不等同于 SQL 执行准确率。

## Reproduction Notes

评测时应固定模型版本、数据集版本、随机种子、数仓快照和 SQL scorer。提交新的评测数字前，应同时保存原始结果、失败样例和对应命令，避免将不同数据集、不同样本数或不同 scorer 的结果直接比较。
