# Streamlit Community Cloud 公网部署说明

## 部署用途

此方案用于比赛答辩和功能演示，任何获得链接的人都能直接访问。它不是正式教学平台：访客共享同一运行实例与临时 SQLite 数据，应用重启、休眠或重新部署后数据可能清空。

**禁止在公网演示中上传真实学生姓名、作答、试卷或照片。只能使用虚构、脱敏的演示材料。**

## GitHub 发布范围

仓库只应包含源代码、测试、文档和空的 `data/.gitkeep`。以下内容不得上传：

- `data/mistakes.db` 或任何 `*.db` 文件；
- `.env`、`.streamlit/secrets.toml` 或真实 API 密钥；
- 学生照片、真实姓名、作答记录；
- `.venv`、缓存和临时文件。

建议 GitHub 仓库保持私有，由 Streamlit Community Cloud 获得部署权限；应用本身设为公开。

## 创建应用

在 Streamlit Community Cloud 中选择：

- Repository：`learning-agent-public-demo`
- Branch：`main`
- Main file path：`app.py`
- Python version：`3.12`
- App visibility：Public

## Secrets

在应用的 Advanced settings → Secrets 中填写，真实值只在平台页面中输入，不要提交到 Git：

```toml
PUBLIC_DEMO = "true"
OPENAI_API_KEY = "你的模型密钥"
OPENAI_BASE_URL = ""
OPENAI_MODEL = "你的对话模型名称"
OPENAI_VISION_MODEL = "支持图片输入的多模态模型名称"
```

如果暂时不配置模型密钥，应用仍能进入模板演示模式，但拍照识别不可用。`OPENAI_VISION_MODEL` 必须对应支持图片输入的模型。

## 上线检查

1. 打开公开链接，无需登录即可进入。
2. 每个页面顶部都显示匿名公网演示和隐私警告。
3. “错题诊断”页能看到拍照/文件上传入口。
4. 只使用虚构题目完成一次演示流程。
5. GitHub 仓库中不存在数据库、密钥、真实学生材料。

演示后可在 Streamlit Community Cloud 中重启或重新部署应用，以清理临时运行数据。若要长期保存真实教学数据，应另行建设账号体系、访问控制、学生级数据隔离、合规存储与备份机制。
