# 本地 Git 仓库

本仓库保存工作流代码、prompts、兼容性补丁、文档、结构化笔记和 npm 锁文件。

以下数据保留在电脑上，但不纳入 Git 提交：

- `state/`：账号专辑配置、已处理账本、采集响应与本机验收报告。
- `interview-kb/raw/`：原始正文、字幕、图片和 OCR。
- `interview-kb/_fav2kb/`：本机 fav2kb 配置和偏好。
- `vendor/` 内的运行时、浏览器及第三方仓库；只提交 rednote 的依赖声明和锁文件。
- 环境密钥、Cookie、SQLite 数据库和缓存。

结构化笔记和 Demo 的原始材料链接指向本地未提交的数据，新克隆的仓库不会包含这些素材。首次在其他电脑运行时，需要重新配置知识库与收藏夹并完成平台登录；本机验收测试依赖本机数据。

在 GitHub Desktop 中选择 **File → Add Local Repository**，选择此项目目录即可。当前只做本地初始化；如需上传，由 GitHub Desktop 的 **Publish repository** 完成。建议保留 **Keep this code private**。
