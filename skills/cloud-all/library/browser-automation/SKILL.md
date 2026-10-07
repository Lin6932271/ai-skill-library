---
name: browser-automation
description: "统一自动化入口。覆盖浏览器自动化（Playwright）和 Windows 桌面应用自动化（OpenReverse）。\n浏览器场景：打开网页、点击、填表、爬取、截图、自动化登录、渗透页面交互。\n桌面场景：操作 IDA/x64dbg 等 GUI 工具、Windows UI Automation、视觉驱动交互、桌面应用网络抓包。\n触发关键词：浏览器自动化、桌面自动化、打开网页、填表、爬取、截图、自动化登录、Playwright、agent-browser、headless、OpenReverse、UIA、CUA、桌面操作、Windows 自动化。"
---

# Desktop & Browser Automation

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: confirm whether the current task falls within this skill's applicable scope
2. `NOW`: read `../tool-index.md`, verify tool availability and actual paths
3. `NEXT`: when a tool is missing, invoke bootstrap; do not guess paths
4. `ACT`: enter step 1 of the "Workflow" and execute; do not stop at a confirmation state

## Applicable scope

Use this skill when the task belongs to the following scenarios:

### Browser scenarios (Playwright / agent-browser)
- Open a web page and operate page elements (click, fill form, submit)
- Scrape page content or take screenshots
- Automate login flows
- Interact with web pages during penetration testing (submit payloads, trigger XSS)
- Automate CAPTCHA-page handling
- Batch form submission

### Desktop application scenarios (OpenReverse)
- Operate Windows desktop apps (IDA Pro, x64dbg, Wireshark, etc.)
- Need vision-driven interaction (CUA mode)
- Need structured UI operations (UIA mode)
- Desktop-app network traffic observation (built-in mitmproxy)
- Automate the GUI operations of reversing tools
- Black-box testing desktop software

### Division of labor with other tools

| Scenario | What to use |
|------|--------|
| Operate web pages (inside browser) | **Playwright / agent-browser** |
| Operate desktop apps (Windows GUI) | **OpenReverse** |
| Capture and analyze HTTP requests | anything-analyzer or OpenReverse network lane |
| JS breakpoints, Hook, CDP debugging | jshookmcp |
| Locate signature algorithms, reproduce with environment patching | js-reverse |

Quick decision:
- Target is a web page → Playwright
- Target is a Windows desktop app → OpenReverse
- Need both → combine

---

## Part 1: Browser automation (Playwright / agent-browser)

### Core workflow

```bash
# 1. 打开页面
agent-browser open <url>

# 2. 获取可交互元素（返回 @e1, @e2... 引用）
agent-browser snapshot -i

# 3. 用引用操作元素
agent-browser click @e1
agent-browser fill @e2 "text"

# 4. 完成后关闭
agent-browser close
```

### Command reference

```bash
# 导航
agent-browser open <url>
agent-browser close

# 页面快照
agent-browser snapshot        # 完整无障碍树
agent-browser snapshot -i     # 仅可交互元素（推荐）

# 交互操作
agent-browser click @e1
agent-browser fill @e2 "text"
agent-browser type @e2 "text"
agent-browser press Enter
agent-browser scroll down 500

# 获取信息
agent-browser get text @e1
agent-browser get title
agent-browser get url

# 等待
agent-browser wait @e1
agent-browser wait 2000
agent-browser wait --load networkidle
```

### Notes
- You must run `agent-browser close`; otherwise the process leaks
- Always snapshot before operating; don't guess element references
- After submitting a form, use `wait --load networkidle` for the page to stabilize

---

## Part 2: Desktop application automation (OpenReverse)

### Overview

[OpenReverse](https://github.com/zhexulong/openreverse) is a desktop interaction and evidence-collection framework for AI Agents, supporting:
- **UIA mode**: Windows UI Automation, structured desktop control operations
- **CUA mode**: vision-driven interaction (Computer Use Agent), suitable for complex GUIs
- **Network observation**: built-in mitmproxy proxy + local capture

### Interaction mode selection

| Mode | Suitable for | Underlying tech |
|------|---------|------|
| UIA | Target app has standard Windows controls (buttons, textboxes, lists) | Windows UI Automation API |
| CUA | Target app has complex or non-standard controls (IDA disassembly view, custom-rendered UI) | Visual recognition + mouse/keyboard |

### Network observation mode

| Mode | Suitable for |
|------|---------|
| Proxy Lane | Target app can be configured to use a proxy (recommended) |
| Local Lane | Target app cannot go through a proxy; local capture needed |

### Installation and configuration

```bash
# 1. Clone 项目
git clone https://github.com/zhexulong/openreverse.git
cd openreverse

# 2. 安装依赖
npm install

# 3. 接入 Agent 宿主（Claude Code / Codex / Zed）
npm run init:agents -- --target=all /path/to/project

# 4. 安装 CUA runtime（如果需要视觉驱动模式）
npm run install:cua-runtime
npm run doctor:cua-runtime

# 5. 安装网络观察依赖（如果需要抓包）
npm run install:mitmproxy
npm run doctor:network
```

### Common combinations

| Need | Configuration |
|------|------|
| Only operate desktop app | UIA or CUA, no network lane |
| Operate desktop app + packet capture | UIA/CUA + proxy lane |
| Operate desktop app + local capture | UIA/CUA + local lane |

### Reversing scenario examples

```text
场景：自动化操作 IDA Pro 进行批量分析

1. 用 OpenReverse CUA 模式打开 IDA Pro
2. 自动加载目标二进制
3. 等待分析完成
4. 通过 UI 操作导出函数列表
5. 同时用 network lane 观察 IDA 的网络行为（如 Lumina 请求）
```

```text
场景：自动化操作 x64dbg 调试

1. 用 OpenReverse UIA 模式启动 x64dbg
2. 加载目标程序
3. 设置断点
4. 运行并观察寄存器/内存变化
5. 截图保存证据
```

---

## On-Demand Bootstrap

### Automation capability boundary

| Tool | Auto-installable | Install method | Note |
|------|-----------|---------|------|
| Playwright | ✓ | npm + npx playwright install | Browser automation engine |
| agent-browser CLI | ✓ | npm install -g agent-browser | Browser operation CLI |
| Node.js | ✓ | winget | Prerequisite |
| OpenReverse | ✗ | Manual clone + npm install | Experimental stage, heavy dependencies |
| mitmproxy | ✗ | Manual install | OpenReverse network-observation dependency |

### Bootstrap trigger

- Missing Playwright for browser operations → auto bootstrap
- Need OpenReverse for desktop operations → guide the user through manual install (give full steps)

### OpenReverse manual install guide

If the AI detects that desktop automation is needed but OpenReverse is not installed:

```markdown
⚠️ **需要 OpenReverse 进行桌面应用自动化**

**安装步骤**：
1. `git clone https://github.com/zhexulong/openreverse.git`
2. `cd openreverse && npm install`
3. `npm run init:agents -- --target=all <你的项目路径>`
4. 如需视觉模式：`npm run install:cua-runtime`
5. 如需网络观察：`npm run install:mitmproxy`

**验证**：`npm run doctor:cua-runtime` 和 `npm run doctor:network`
```

---

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Applicable**: any task that requires automating browser or desktop application operations
**Downstream exit**:
- Captured requests need analysis → `anything-analyzer` or `js-reverse`
- Need JS debugging/Hook → `jshookmcp`
- Need to recover a signature algorithm → `js-reverse`
- Desktop app is a reversing tool → `ida-reverse/`

**Peer-related module**: `js-reverse` (after browser operations you may need to analyze JS), `ida-reverse` (OpenReverse can automate IDA GUI operations)


## Task-completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step in the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items required by RULES?

<!-- skill-trace:79794ab9513f5aae8edd492521734e7f -->
