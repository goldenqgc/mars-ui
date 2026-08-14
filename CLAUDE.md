# Project Conventions for Claude Code

本文件为本项目下 Claude Code 会话的协作约定。所有规则优先级高于工具默认行为，请 Claude 在生成代码前先 read 一次。

---

## 1. 语言约定（强制）

| 场景 | 使用语言 |
|---|---|
| **与用户的对话**（解释、设计讨论、确认、报错说明、AskUserQuestion 提问） | **中文** |
| **代码注释**（行内 `//` 注释、函数 docstring、TODO 注释） | **英文** |
| **用户可见的 UI 文案**（按钮文字、表头、提示语、错误信息、空状态文案、tooltip、placeholder） | **英文** |
| **代码标识符**（变量名、函数名、class 名、文件路径） | **英文** |
| **git commit message**、分支名、PR 标题 | **英文** |
| **API 路径、URL slug** | **英文**（kebab-case 或 snake_case，按项目既有约定） |

### 例外情况
- 如果用户明确切到英文交流，则跟随用户使用英文——以用户的当前主发言语言为准。
- 如果用户给的种子数据是中文（如 mockup 演示用的 IP 主机名 `sw-core-01` 已是英文没问题；但若是"北京-机房-A"之类），保留用户原始输入。
- `mockup.md`、`mars-ui.md` 等用户原始提供的 spec 文档里若保留中文示例，引用时不要翻译。

---

## 2. 项目技术约束（must read）

完整规范在 `mars-ui.md` 和 `mockup.md`。要点速览：

- 后端：`FastAPI` + `Jinja2Templates`，不要在 Python 里拼 HTML 字符串。
- 前端：`Tailwind` + `HTMX`，不引入除这俩以外的依赖（**Inter via Google Fonts 是已获得显式同意的外部 CSS**，不要继续扩）。
- 模板目录：`templates/{base.html,components/mars_ui.html,pages/*.html}`
- CSS 变量：`static/css/base.css` §2.1 是单一权威，所有色值都从这里取。**禁止**硬编码 HEX/RGB。
- 主题：`<html class="light|dark">` 切换；默认 light（按用户决定，不跟 OS）。`base.html` 在 `<head>` 顶端有 no-flash 脚本；底部有 theme toggle 的全局 delegator。
- 服务端驱动优先；纯客户端 JS 仅用于第 6 章列出的场景：表格全选联动、tab 切换、主题切换、Checkbox/Tabs 的 data-state bridge。
- **组件库已对齐 shadcn/ui 1:1**，覆盖以下 12 个 primitive 家族：`Card / Button / Badge / Table / Input / Select / Label / Checkbox / Alert / Empty / Skeleton / Tabs / Pagination`，外加 Typography（h1-h4 + lead/large/small/muted/inline_code）。详见 `mars-ui.md` §4。任何新页面必须复用宏，不要重新写一遍 div + class。

### 2.1 当前 mockup 阶段的运行时

- 入口：`/opt/mars/mar-ui/mockup/app.py`
- 路由：`/login /switches /switches/{id} /logs`（5 条 UI 路由 + 几个 mockup 写端点 `/switches/{id}/reboot|preview-config|apply-config`、`/switches/bulk-reboot`）
- 假数据：`SWITCHES` 列表（12 台设备，混合 UP/DOWN/WARNING/UNKNOWN）+ `LOGS` 列表（15 条审计记录）
- 启动：`cd /opt/mars/mar-ui/mockup && python3 -m uvicorn app:app --host 0.0.0.0 --port 8765`
- LAN 入口：http://192.168.25.221:8765/；防火墙已开 `tcp/8765` in zone `public`（runtime + permanent）
- 进程：非 systemd 托管（nohup），重启需手动。重启后 tweak 不会丢，但 host 重启后会掉——mockup 阶段不动 systemd，等接真实数据时再起 unit。

---

## 3. 协作风格（强制）

- **不要擅自决定**——任何 MARS_UI/mars-ui.md 里没明说的设计选择，主动 `AskUserQuestion` 等用户定夺，不要自己拍板。
- **不要扩范围**——任务里说"不要做 X"（响应式、Playwright、SQLAlchemy 等）就严格不做；如果觉得有必要做，明示给用户决定。
- **修改规范前先改文再写码**——UI 设计类改动要先更新 `mars-ui.md`，再同步到 `static/css/base.css` 和 `templates/components/mars_ui.html`，**禁止**实现和文档脱钩。
- **前后端日志保留真实错误**——错误不能"消化"成 200 返回。Jinja2 渲染失败必须能看到 traceback。
- **中量改动前先列计划**——新增 component family、替换全局样式、拆页面布局这类改动，**先**输出 affected files + 改动摘要 + 风险点，等用户点头再执行。
- **memory 持久化**——Claude 学到的稳定项目级事实（不是临时上下文里的）写到 `/home/fred/.claude/projects/-opt-mars/memory/`，单 fact 单文件，前置 frontmatter；MEMORY.md 内只放一行指针。

---

## 4. 工作流偏好

- **mockup 阶段**：纯静态 UI，不接数据库、不写 SQLAlchemy 模型、不写真实鉴权。
- **mockup 不做响应式**——桌面内网工具，按 `min-w-[1280px]` 固定宽度。不写 `sm:` `md:` `lg:` 断点类。
- **shadcn-faithful**：所有 UI 组件对照 `https://ui.shadcn.com/docs/components` 1:1 落地，不自由发挥。
- **里程碑后自检组件覆盖**——新增宏后用 `grep` 报表 + 实际渲染抽样，确认每个 primitive 真在页面里出现过。

---

## 5. 不要做的事（持续生效）

- 不要做移动端响应式。
- 不要接数据库 / 写真实 ORM。
- 不要写真实登录鉴权（session/JWT）——mockup 阶段。
- 不要做 Playwright / e2e 测试——mockup 阶段。
- 不要引入除 HTMX / Tailwind 之外的前端依赖（Inter 字体已通过 Google Fonts CSS 引入，算是 CSS link 级别依赖，被用户显式同意；如果未来引入其他 CSS link 也需明示）。
- 不要把 `<table>` / `<thead>` / `<tbody>` 直接写在页面里——必须走 `mars_ui.html` 的 `ui_table` 家族宏。
- 不要在 `<tr>` / `<td>` 上重新声明边框或 hover——边框规则挂在父节点 `<thead>`/`<tbody>` 上。
