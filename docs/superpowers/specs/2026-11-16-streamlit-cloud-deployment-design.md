# Streamlit Community Cloud 公网部署设计

## 目标

为“知错睿析”生成一个可通过公网 HTTPS 地址访问的比赛演示环境。部署使用 Streamlit Community Cloud，源代码托管在 GitHub 私有仓库，入口为根目录 `app.py`。

## 方案选择

- 已选择：Streamlit Community Cloud，适合比赛展示、自动构建和持续更新。
- 未选择临时隧道：依赖本机持续运行，网址与稳定性不适合正式演示。
- 未选择 Render/Railway：配置和持久化成本更高，当前演示原型不需要常驻服务。

## 安全与数据

- GitHub仓库默认创建为私有仓库；Community Cloud获得该仓库的部署权限。
- 不上传本地 `data/mistakes.db`，云端首次启动自动创建空数据库。
- `.env`、`.streamlit/secrets.toml`、学生照片、测试缓存和虚拟环境不得进入GitHub。
- 新增基于 Streamlit Secrets 的演示访问口令 `DEMO_ACCESS_CODE`；通过验证后仅在当前浏览器会话放行。
- 模型密钥通过Community Cloud Advanced settings的Secrets填写：`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`、`OPENAI_VISION_MODEL`。
- 页面明确提示：云端SQLite为临时演示数据，重启可能清空；不得上传真实学生敏感材料。

## 云端兼容修改

- 删除 `.streamlit/config.toml` 中固定的 `server.address = "127.0.0.1"`，让平台负责监听地址。
- `.gitignore` 增加 `data/*.db` 和 `.streamlit/secrets.toml`；保留 `data/.gitkeep`。
- `app.py` 在初始化数据库和渲染业务页面前执行访问口令校验。
- `requirements.txt` 继续作为唯一依赖文件，Python版本选择3.12。
- README增加公网演示、Secrets格式、数据临时性和重新部署说明。

## 发布流程

1. 在本地建立部署分支并运行全量测试。
2. 创建GitHub私有仓库 `learning-agent-public-demo`，只推送安全审计后的文件。
3. 用户在浏览器登录 `share.streamlit.io` 并连接GitHub私有仓库权限。
4. 创建应用：仓库 `learning-agent-public-demo`、分支 `main`、入口 `app.py`、Python 3.12。
5. 在Advanced settings填写Secrets，不在聊天、代码或Git提交中回显真实密钥。
6. 部署后验证首页、访问口令、图像上传入口和健康状态，返回最终 `streamlit.app` 地址。

## 边界

- Community Cloud免费环境不作为持久数据库或生产教学平台。
- 多个获准访问者仍共享同一运行实例和临时SQLite；演示后应删除数据或重启应用。
- 图像识别依赖所配置模型及其网络、额度和数据处理条款。
- 如果用户尚未登录GitHub或Community Cloud，最终授权步骤需要用户在浏览器中完成。
