# 大模型算法工程师面试收藏夹 Workflow

把抖音和小红书固定收藏夹中的内容增量同步为可检索、可复习、Obsidian 兼容的 Markdown 知识库。

当前进度：

- 阶段一已完成：抖音采集 10 条，7 条本地 Whisper 转写、3 条图文正文。
- 阶段二已完成首批验证：10 条轻量过滤，3 条相关内容生成结构化笔记。
- 阶段三已完成：小红书 `knowledge` 专辑 5 篇、全部 20 张正文图片已 OCR，生成 5 篇统一格式条目。
- 阶段四尚未开始。

## 目录

```text
interview-kb/
├── by-company/         # 结构化面经，每个作品只保留一篇主笔记
├── by-topic/           # Obsidian 双链主题索引
├── raw/douyin/         # 采集器原始 Markdown，不手工修改
├── _fav2kb/            # fav2kb 配置与偏好
└── index.md            # 总索引
prompts/                # 过滤、总结和 Agent 补充规则
src/interview_kb/       # 提取、过滤、校验编排代码
state/                  # 过滤结果和已处理 ID 账本
vendor/                 # 指定的抖音 fallback 工具
```

## 环境与安装

已验证环境：macOS ARM64、Python 3.12、uv、ffmpeg。

项目编排层没有第三方 Python 依赖：

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e .
```

抖音主方案 `fav2kb` 已安装，但本机访问收藏页时被抖音返回 HTTP 403。当前使用用户指定的 fallback：

```bash
cd vendor/douyin-favorites-to-knowledge
uv venv --python 3.12 .venv
.venv/bin/python -m pip install ".[local-asr]"
.venv/bin/douyin-favorites-knowledge setup \
  --knowledge-dir ../../interview-kb/raw/douyin \
  --transcription local \
  --skip-login
.venv/bin/douyin-favorites-knowledge login --source collection
```

本仓库将 `local-asr` 额外固定为 `av<19`，避免 `faster-whisper 1.2.1` 与 PyAV 19 的解码冲突。

## 小红书安装与首次登录

本机项目中已安装官方 Apple Silicon Node 22.23.4（已核对官方 SHA-256）和 Chromium；另外需要 `/Applications/Google Chrome.app`。Node 位于 `vendor/node-runtime/`，不要求全局安装。使用锁文件重装 npm 依赖：

```bash
PATH="$PWD/vendor/node-runtime/bin:$PATH" \
PLAYWRIGHT_BROWSERS_PATH="$PWD/vendor/playwright-browsers" \
  vendor/node-runtime/bin/npm ci --prefix vendor/rednote-runtime
sh scripts/apply_rednote_patch.sh
```

运行登录工具：

```bash
vendor/node-runtime/bin/node scripts/rednote_mcp_client.mjs login '{}'
```

首次登录可能需要“扫码 → 手机号验证 → 再次扫码并确认”。请在工具打开的同一个 Chrome 窗口中完成全部步骤。登录工具允许等待 10 分钟，客户端等待 11 分钟；期间不要手动关闭窗口。手机号和验证码仅在小红书页面中输入。工具自行保存登录态到 `~/.mcp/rednote/`，请勿将凭证文件复制到项目或提交到版本库。

本机安装包进行了兼容性修正：使用正式版 Chrome、允许更长登录等待、容忍页面跳转期间的检测异常、在浏览器上下文中检查会话状态、限定专辑范围，并修正批处理用户 ID。补丁保存在 `patches/rednote-mind-mcp-0.3.0.patch`。重装依赖后运行 `sh scripts/apply_rednote_patch.sh`；脚本检查版本，并能识别已应用的补丁。

验证登录：

```bash
vendor/node-runtime/bin/node scripts/rednote_mcp_client.mjs check_login_status '{}'
```

读取目标专辑（默认 `knowledge`，可用 `REDNOTE_FAVORITE_FOLDER` 环境变量更改）：

```bash
MCP_RESULT_PATH="$PWD/state/rednote-private/favorites.json" \
  vendor/node-runtime/bin/node scripts/rednote_mcp_client.mjs \
  get_favorites_list '{"limit":5}'
MCP_RESULT_PATH="$PWD/state/rednote-private/batch-5.json" \
  vendor/node-runtime/bin/node scripts/rednote_mcp_client.mjs \
  get_batch_notes_from_favorites '{"limit":5,"includeImages":true}'
```

上游没有专辑参数，本地补丁使用已从 `knowledge` 页面确认的专辑 ID（`state/rednote-folder.json`）限定范围；没有固定 ID 时按名称查找，找不到或存在同名不同链接时停止。变更专辑时同步更新该配置。批量上限为 20，本项目首次验证使用 5，笔记之间随机等待 3–6 秒。私有响应可能含临时访问 URL 和图片 Base64，放在已忽略的 `state/rednote-private/` 中。新批次会逐条写入 `.checkpoint.json`，中途失败时保留已经采集的内容。

编译并运行本地 OCR（需要 macOS Command Line Tools）：

```bash
swiftc -module-cache-path /private/tmp/interview-kb-swift-cache \
  scripts/ocr_images.swift -o /private/tmp/interview-kb-ocr
PYTHONPATH=src python3 -m interview_kb.rednote \
  state/rednote-private/batch-5.json \
  --ocr-binary /private/tmp/interview-kb-ocr \
  --report state/rednote-extraction-report.json
```

使用 Apple Vision 在本地识别每张图片，采集图片（MCP 工具压缩版）和 OCR 一并保存到 `interview-kb/raw/xiaohongshu/`。公式、图表可能识别不全，必须对照图片，不将 OCR 当作技术正确性验证。该路径不使用上游内置测试 API Key，也不产生云端 OCR 费用。

如果 Apple Vision 在受限执行环境中返回 `nilError`，需允许 OCR 进程在本机环境运行；不应以空 OCR 结果代替成功。调用失败、空批次或 OCR 失败均返回非零退出码，并保留原始响应用于排查。

### 已验证产物

- [知识库索引](interview-kb/index.md)：3 篇抖音 + 5 篇小红书结构化条目。
- [3+3 端到端 Demo](demo/README.md)。
- [5 篇小红书提取报告](state/rednote-extraction-report.json)：20 张图片的 OCR 字数、完整性及 SHA-256。
- [过滤判断](state/rednote-filter-decisions.json)、[已处理账本](state/processing-ledger.json)。

重新生成公司/主题索引：

```bash
PYTHONPATH=src python3 -m interview_kb.indexing --kb-dir interview-kb
```

### 小红书故障排查

- 登录要依次完成扫码、手机号验证、再次扫码；已留出 10 分钟。凭证过期仍须本人完成平台验证，不能保证永远无需重新授权。
- 上游遗漏专辑 `/board/…/笔记ID` 链接的访问参数；补丁保留页面实际提供的参数。遇到登录异常或验证要求会停止后续请求。
- 上游全页面图片选择器会混入推荐区；补丁从当前笔记数据/正文容器提取图片。缺少 `imageScope=current_note` 的旧图片响应被入库模块拒绝。已发现的旧批次记录在 `state/rednote-quarantine.json`。
- 图片按 SHA-256 去重；网络缺图会保留数量差异并返回失败状态。先检查报告，再仅重试失败条目。
- 收藏时间未从平台取得，统一写 `unknown`；采集时间单独保留，不将发布时间冒充收藏时间。

## 阶段二运行方式

生成轻量过滤包：

```bash
PYTHONPATH=src python3 -m interview_kb.cli prepare-filter \
  --raw-dir interview-kb/raw/douyin \
  --output state/filter-candidates.json
```

Agent 按以下顺序处理：

1. 使用 `prompts/relevance-filter.md` 复核快速过滤结果。
2. 只对 `relevant` 和选定的 `low_confidence` 条目读取完整原始材料。
3. 使用 `prompts/structured-summary.md` 生成笔记。
4. 使用 `prompts/agent-supplement-rules.md` 检查补充标注。
5. 更新 `state/processing-ledger.json` 和主题索引。

校验结构化笔记：

```bash
PYTHONPATH=src python3 -m interview_kb.cli validate --kb-dir interview-kb
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## 每日同步

定时任务将在阶段四创建和验证。当前不要把下列命令直接加入 cron，因为抖音登录态仍需观察：

```bash
cd vendor/douyin-favorites-to-knowledge
HF_HUB_DISABLE_XET=1 .venv/bin/douyin-favorites-knowledge sync \
  --source collection --no-login-prompt --headed
```

## 故障排查

- fav2kb 显示 HTTP 403：不要复制 Cookie 或绕过验证；当前使用 fallback 独立浏览器 profile。
- fallback 返回 `login_required`：运行 `douyin-favorites-knowledge login --source collection` 后扫码。
- `open() got an unexpected keyword argument 'metadata_errors'`：确认虚拟环境中的 `av` 版本小于 19。
- Hugging Face 模型下载长期停在 0B：设置 `HF_HUB_DISABLE_XET=1` 后重试，会复用已下载缓存。
- 图文显示 `skipped_image`：阶段一 fallback 只保留正文，图片 OCR 将在阶段三接入视觉链路。
- 原始内容不相关：在账本中标记 `skipped_irrelevant`，不要生成空洞总结。
