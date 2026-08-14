# TESTING.md — Playwright 测试规范

> 配合 MARS_UI.md 使用 | 仅覆盖核心写操作链路，不追求全覆盖率
> 本文档是 Claude Code 的测试执行契约。

---

## 0. 定位

这是内网运维工具，测试目的是**防住HTMX局部刷新失败和高危操作流程出错**，不是为了测试覆盖率指标。原则：

- 只测**有副作用的写操作链路**（批量操作、配置下发、设备重启）
- 不测纯展示页面（日志列表、详情只读页）的样式细节
- 不追求快照测试 / 像素级视觉回归
- 优先测"用户点了按钮之后，状态有没有真的变"，而不是"页面长什么样"

---

## 1. 环境配置

```bash
pip install pytest-playwright --break-system-packages
playwright install chromium  # 只装chromium，不需要装全部浏览器
```

项目结构新增：

```
tests/
  conftest.py           # fixture：启动app、清理测试数据
  e2e/
    test_auth.py
    test_switch_batch_ops.py
    test_config_apply_flow.py
  e2e_helpers.py         # 公共选择器/等待逻辑
```

`pytest.ini` / `pyproject.toml` 里固定只用 chromium，headless 跑：

```ini
[pytest]
addopts = --browser chromium
```

---

## 2. 必须覆盖的核心链路（不可省略）

### 2.1 登录鉴权

确认未登录态访问受保护页面会被重定向，登录后能正常进入列表页。

### 2.2 批量操作确认流程

这是HTMX最容易出隐蔽bug的地方——`hx-target`写错、勾选状态丢失、确认弹窗没拦住误触发,这些坑都要靠这条测试盯住:

```python
def test_batch_reboot_flow(page):
    page.goto("/switches")
    page.check('input[name="selected_ids"][value="1"]')
    page.check('input[name="selected_ids"][value="2"]')
    page.click("text=批量重启")

    # hx-confirm 弹出的是浏览器原生 confirm dialog
    page.once("dialog", lambda dialog: dialog.accept())
    page.click("text=确认执行")

    # 验证状态徽章真的更新了，而不只是页面没报错
    expect(page.locator("#status-1")).to_have_text("重启中", timeout=5000)
```

### 2.3 配置预览→确认→执行 两步流程

这是 MARS_UI.md 第5章强制要求的两步流程，必须验证"预览"和"执行"是两次独立请求，而不是被简化成一次：

```python
def test_config_apply_requires_preview_first(page):
    page.goto("/switches/1")
    page.click("text=下发配置")
    page.fill("#config-textarea", "vlan 100")
    page.click("text=预览变更")

    # 必须先看到 diff 区域才能点确认执行
    expect(page.locator("#config-diff")).to_be_visible()
    expect(page.locator("text=确认执行")).to_be_enabled()

    page.click("text=确认执行")
    expect(page.locator("#apply-result")).to_contain_text("已下发")
```

### 2.4 HTMX swap 完整性兜底检查

写一条通用辅助，凡是涉及`hx-target`的关键操作，断言目标区域内容确实发生了变化（不是空白、不是还在loading态）：

```python
def assert_htmx_swap_succeeded(page, target_selector, timeout=5000):
    locator = page.locator(target_selector)
    expect(locator).not_to_be_empty(timeout=timeout)
    expect(locator.locator(".htmx-indicator")).to_be_hidden()
```

---

## 3. 不需要测的（明确排除，避免过度投入）

- 日志列表的分页/排序样式
- 卡片圆角、间距这类纯CSS细节（人工肉眼检查即可）
- 移动端适配（项目本身不做响应式，见 MARS_UI.md 第0章）
- 第三方依赖（HTMX库本身、Tailwind编译结果）是否正常工作

---

## 4. Claude Code 执行契约

1. **改动触发测试**：任何修改涉及 `hx-post` / `hx-get` / `hx-target` 的模板或路由代码后，必须运行对应的 Playwright 测试，不是可选项。
2. **新增写操作必须配测试**：新增任何有副作用的操作（特别是涉及真实设备的），必须同时补一条覆盖该流程的测试用例，禁止只写功能不写测试。
3. **失败优先于美观**：如果某个UI改动导致已有测试失败，先修复逻辑，不允许为了让测试通过而删测试或放宽断言。
4. **禁止脆弱选择器**：测试里禁止用纯样式class做选择器（如`.bg-primary`），统一用语义化的`text=`、`id`、`name`属性定位，避免UI微调就导致测试全挂。
5. **mock外部设备交互**：测试环境里不允许真的对接真实交换机执行SSH/SNMP命令，`netmiko`相关调用必须在测试环境下被mock，只验证UI→后端这条链路，不验证后端→设备这条链路（后端到设备的部分用单元测试覆盖，不归这个文档管）。

---

## 投喂指令（给 Claude Code）

```
请读取根目录下的 TESTING.md。这份文档定义了本项目的 Playwright 测试规范，
配合 MARS_UI.md 一起执行。请先按第1章配置好 pytest-playwright 环境，
然后按第2章把三条核心链路的测试先搭起来。后续每次修改涉及 HTMX 交互的代码，
必须主动运行对应测试再告诉我结果。
```
