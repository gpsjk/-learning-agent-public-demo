# 图像识别答辩稳定版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将原来的三图单题转写升级为五图多题、可核对、可部分成功和可重试的批量识别诊断流程。

**Architecture:** 多模态模型输出 `PhotoBatchExtraction`，`photo_pipeline.py` 负责纯数据状态转换，`app.py` 只负责 Streamlit 渲染和调用。数据库为每题记录批次号与题号，以数据库唯一约束保证失败重试不重复保存。

**Tech Stack:** Python 3.12、Streamlit 1.x、Pydantic 2、SQLite、OpenAI 兼容多模态接口、pytest。

**Spec:** `docs/superpowers/specs/2026-11-15-image-recognition-upgrade-design.md`

## Global Constraints

- 上传图片总数最多 5 张。
- 不引入 OpenCV 或新的模型服务，继续使用项目现有多模态模型配置。
- 保留手工单题录入和旧数据库兼容。
- 不臆造无法识别的文字或来源图片。
- 每题独立保存，失败题不回滚成功题，重试不得重复成功题。

## Review Focus

- 空图片、伪图片和不支持格式必须在请求模型前失败，并给出可恢复提示（Task 2）。
- 模型返回空题目、重复题号或越界来源编号时必须被标准化而非破坏页面（Task 1）。
- 未知来源和已知来源合并后仍必须保留“来源未完全确认”（Task 1）。
- 连续两次点击合并不得重复追加文本，被消费项不得再次包含（Task 1、Task 3）。
- 第二题失败后重试必须复用原批次号且不重复保存第一题（Task 2、Task 3）。

---

### Task 1: 多题识别模型与批次纯函数

**Files:**
- Create: `photo_pipeline.py`
- Modify: `models.py`
- Modify: `prompts.py`
- Test: `tests/test_photo_batch.py`

**Interfaces:**
- Produces: `PhotoItemExtraction`、`PhotoBatchExtraction`、`normalize_photo_batch(payload, image_count)`、`merge_adjacent_items(items, source_index)`、`included_items(items)`。

- [ ] 写失败测试：多题结构、稳定题号、警告清理、越界来源过滤、未知来源保留、相邻合并幂等和被消费项不可恢复。
- [ ] 运行 `python -m pytest tests/test_photo_batch.py -q`，确认因接口缺失而失败。
- [ ] 实现 Pydantic 模型、批量提示词和无 Streamlit 依赖的状态转换函数。
- [ ] 重跑测试，确认全部通过。

### Task 2: 服务与数据库幂等批量保存

**Files:**
- Modify: `llm_service.py`
- Modify: `database.py`
- Test: `tests/test_photo_batch.py`
- Test: `tests/test_teacher_and_photo.py`

**Interfaces:**
- Consumes: Task 1 的 `PhotoBatchExtraction`。
- Produces: `LLMService.extract_photo_batch(images, subject)`、兼容旧方法 `extract_photo_content(...)`、`save_mistake(..., batch_id='', question_no=0)`、`find_batch_record(batch_id, question_no)`。

- [ ] 写失败测试：五图批量请求、多题响应校验、旧单题包装、数据库迁移、批次唯一性和重试幂等。
- [ ] 运行聚焦测试确认正确失败。
- [ ] 实现批量服务接口与数据库迁移；唯一索引仅约束非空批次。
- [ ] 重跑聚焦测试，确认通过且旧照片读取不回归。

### Task 3: Streamlit 批量识别与逐题诊断界面

**Files:**
- Modify: `app.py`
- Test: `tests/test_photo_flow.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: Task 1 状态函数、Task 2 服务和数据库接口。
- Produces: 五图上传、识别结果卡片、编辑/包含/合并、批量诊断结果和失败题重试。

- [ ] 写 AppTest 失败测试：5图上限文案、多题卡片、编辑与排除、相邻合并、第二题失败但第一题存在、重试不重复。
- [ ] 运行测试确认界面行为尚未实现。
- [ ] 最小修改 `app.py`，保留原手工诊断表单；批次状态仅保存在 `session_state` 和数据库中。
- [ ] 重跑 AppTest 与旧页面测试，确认通过。

### Task 4: 文档、全量验证与桌面打包

**Files:**
- Modify: `README.md`
- Modify: `系统方案.md`
- Create: `图像识别升级说明.md`
- Create: Desktop ZIP `learning_agent_图像识别答辩稳定版.zip`

**Interfaces:**
- Consumes: Tasks 1–3 的完整功能。
- Produces: 可运行的精简交付包。

- [ ] 更新配置、操作路径、失败恢复和能力边界文档。
- [ ] 运行 `python -m pytest -q`，要求 0 failed。
- [ ] 运行 `python -m compileall -q` 覆盖全部项目 Python 文件。
- [ ] 使用临时数据库启动 Streamlit，要求健康端点 HTTP 200 且日志无 traceback。
- [ ] 生成 ZIP，排除 `.venv`、`.env`、`.git`、缓存、临时文件和测试数据库；保留原 `data/mistakes.db`。
- [ ] 解压复验关键文件、路径安全、编译和启动健康检查，再复制到用户桌面。
