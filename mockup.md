# Claude Code 提示词：交换机管理工具 UI Mockup

> **Status: completed (v1.2).** All deliverables implemented. See `mars-ui.md` for the live spec and `mockup/` for the source.

请读取根目录下的 `MARS_UI.md`，严格按照其中的设计规范、CSS变量配置（第2章）、组件宏库（第4章）来完成以下任务。

## 任务目标

做一个**纯静态UI Mockup**，不连数据库、不写真实业务逻辑、不接后端API。目的是让我确认页面布局、组件样式、交互手感是否符合预期，确认后才会进入真实项目搭建阶段。

## 具体要求

### 1. 项目结构

```
mockup/
  templates/
    base.html
    components/
      mars_ui.html       # 按MARS_UI.md第4章，把所有宏先建好
    pages/
      switches_list.html
      switch_detail.html
      logs.html
      login.html
  static/
    css/base.css          # 按MARS_UI.md第2章配置CSS变量
  tailwind.config.js       # 按MARS_UI.md第2章配置
  app.py                   # 极简FastAPI，只负责渲染模板+返回假数据，不连数据库
```

`app.py` 用 FastAPI + Jinja2Templates 起一个最小服务，每个页面路由直接返回写死在代码里的假数据（Python list/dict），不需要数据库、不需要真实鉴权逻辑。

### 2. 需要覆盖的页面（每个页面都要做，且要包含真实感的假数据，不要用"占位文字"敷衍）

**登录页 `login.html`**
- 用户名/密码输入框（`ui_input`）
- 登录按钮
- 简单的错误提示状态展示一下（`ui_error_state`），即使不是真的登录失败也要展示这个组件长什么样

**交换机列表页 `switches_list.html`**（核心页面，组件最全）
- 顶部：搜索框 + 状态筛选下拉（`ui_select`：全部/UP/DOWN/WARNING）
- 数据表格（`ui_table_wrapper`），列：勾选框、设备名称、IP地址、型号、状态徽章、最后心跳时间、操作列
- 至少做12条假数据，状态要混合分布（UP/DOWN/WARNING/UNKNOWN都要出现，不要全是UP）
- 表格上方做"全选/批量操作"工具条，包含批量重启按钮（destructive变体 + hx-confirm，虽然mockup阶段点了不会真生效，但样式和confirm弹窗要做出来）
- 用一行注释说明：如果取消所有勾选，工具条应该置灰或隐藏（先不用做真逻辑，留TODO即可）
- 表格下方放一个分页占位组件
- 额外加一个"空状态"演示入口：比如搜索一个不存在的关键词时，模拟展示`ui_empty_state`组件长什么样（可以用一个简单的查询参数触发，比如 `?demo_empty=1`）

**交换机详情页 `switch_detail.html`**
- 顶部：设备基本信息卡片（`ui_card`），展示名称/IP/型号/状态/位置等字段
- 配置下发区域：演示MARS_UI.md第5章的"预览→确认→执行"两步流程UI，用静态方式展示三种状态：
  - 初始状态（只有"预览变更"按钮）
  - 已预览状态（展示一段假的config diff文本，"确认执行"按钮可点）
  - 已执行状态（展示`ui_badge`显示"已下发"+ 时间戳）
  做成三个可以来回切换查看的静态区块即可（比如用普通的纯前端tab切换，不需要真实接口）
- 底部：该设备的操作日志小列表（复用表格组件，4-5条假日志）

**操作日志页 `logs.html`**
- 完整版操作日志表格，字段：操作时间、操作人、目标设备、操作类型、结果状态、备注
- 至少15条假数据，操作类型要多样（重启/配置下发/登录/批量操作等），结果状态用`ui_badge`区分成功/失败
- 顶部加一个日期范围筛选的表单占位（`ui_input` type=date 两个）

### 3. 组件覆盖检查清单

确保mockup中至少出现一次以下每个组件，做完后请在回复里列出清单逐项确认：

- [x] `ui_card` — used on every page (filters, info panels, table wrapper, demo_empty, recent activity)
- [x] `ui_button` — `default` / `destructive` / `outline` / `secondary` / `ghost` / `link` all 6 variants (shadcn-canonical set)
- [x] `ui_badge` — UP / DOWN / WARNING / UNKNOWN all four state badges rendered as **outline** in `switches_list` (12 rows) and `switch_detail`
- [x] `ui_table` family (`ui_table` + `ui_thead` + `ui_tbody` + `ui_tr` + `ui_th` + `ui_td`) — used in 4 tables across 3 pages
- [x] `ui_input` — text type on `switches_list` filters; date type on `logs` filters
- [x] `ui_select` — status filter on `switches_list`; actor + action filters on `logs`
- [x] `ui_empty_state` — shown on `switches_list` `?demo_empty=1` AND on `switches_list` when filter returns zero rows
- [x] `ui_error_state` — login page Alert-family showcase on first load
- [x] `ui_skeleton_row` — static demo at top of `switches_list`

Additional primitives implemented (not in original checklist but required by §4 of the spec):
- [x] `ui_alert` family (`ui_alert` + `ui_alert_title` + `ui_alert_description`) — login page
- [x] `ui_tabs` family — `switch_detail` config-apply flow (Initial / Previewed / Applied)
- [x] `ui_pagination` family — `switches_list` and `logs` pager
- [x] `ui_status_badge` (ops-domain: status pills) and `ui_result_badge` (audit results)
- [x] `ui_checkbox` + `ui_tr_checkbox` — table row selection
- [x] `ui_page_header` + `ui_kv` — page chrome and key/value display
- [x] `ui_theme_toggle` — top-right of nav (and floating on login)
- [x] Inter font loaded via Google Fonts (CSS link, not JS dep)

### 4. 明确不要做的事（避免范围扩散）

- 不要接数据库、不要写真实的SQLAlchemy模型
- 不要做真实的登录鉴权逻辑（session/JWT这些先不做）
- 不要做Playwright测试（这是mockup阶段，TESTING.md的规范等正式项目搭建时再用）
- 不要做响应式/移动端适配（MARS_UI.md第0章已经说明不需要）
- 不要引入除HTMX、Tailwind之外的前端依赖

### 5. 完成后请做的事

1. 启动服务后告诉我访问的本地地址和各页面路径
2. 贴出"组件覆盖检查清单"的勾选结果
3. 如果实现过程中发现MARS_UI.md里某个宏定义不够用或有歧义，直接指出来，不要自己瞎猜决定，等我确认
