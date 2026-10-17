+++
title = 'AI Agent + 大物实验报告工作流'
date = 2026-10-17
+++

> 目标：用 VS Code + LaTeX + Python + Claude Code + MinerU，完成浙大大物实验的预习报告与实验报告。

---

## 前言

本工作流发展自【学习天地】如何快速完成一篇大物实验报告？ai agent使用分享！（tag：大物实验 实验报告 latex ai codex claude antigravity） https://www.cc98.org/topic/6446291 复制本链接到浏览器或者打开【CC98】微信小程序查看~

本文默认已经完成claude code的安装，若没有，移步【学习天地】你需要的只是claude code与codex，而不是龙虾 https://www.cc98.org/topic/6445388 复制本链接到浏览器或者打开【CC98】微信小程序查看~

原则上不鼓励ai工具生成作业


## 0. 整体技术栈

| 组件 | 作用 |
| --- | --- |
| TeX Live 2026 | LaTeX 发行版，提供 XeLaTeX / latexmk |
| VS Code + LaTeX Workshop | 编辑、保存自动编译、PDF 预览、SyncTeX 跳转 |
| Python venv | 数据处理、拟合、绘图 |
| MinerU 4.x | 把 PDF / PPT / Word / 图片教材转成 Markdown |
| Claude Code（VS Code 扩展） | 按 `Prompt.md` 工作流生成报告、跑脚本、归档 PDF |

工作区根目录：`\PHYLAB`。所有实验共用一个虚拟环境 `PHYLAB\.venv`。

---

## 1. TeX Live：Windows 的 LaTeX 环境

TeX Live 是 Windows 上最省心的 LaTeX 发行版：自带 XeLaTeX、latexmk 和绝大多数宏包，装一次即可长期使用。

### 1.1 下载与镜像

- 官方安装说明：<https://www.tug.org/texlive/acquire-netinstall.html>
- 清华 TUNA 镜像：<https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/Images/>
- 也可使用校内镜像（如 ZJU Mirror 的 CTAN 源），下载更快。

下载 `texlive.iso`，右键 **装载**，运行 `install-tl-windows.bat`。

### 1.2 安装

1. **进入安装界面前先选镜像源**：安装界面里可以指定 CTAN mirror，选国内镜像（清华 TUNA、中科大、ZJU 等），否则下载会很慢。
2. **TeXworks 前端可以不选**：我们只用 VS Code，不需要 TeXworks。
3. 安装位置建议改到大容量磁盘，例如 `F:/texlive/2026`。默认 `scheme-full` 会装全宏包，避免以后缺包。
4. **安装过程比较慢，需要耐心等待**（视网速可能几十分钟到数小时）。不要中途关闭窗口。

### 1.3 配置环境变量

安装完成后，搜索 **“查看高级系统设置”** → **环境变量** → 在 **系统变量** 的 `Path` 中新增：

```text
F:\texlive\2026\bin\windows
```

（按你的实际安装位置调整。）

确定后 **重开 cmd / PowerShell / VS Code**，PATH 才会生效。

### 1.4 验证

在 **cmd**（不是 Git Bash）中依次输入：

```bat
tex -v
latex -v
xelatex -v
bibtex -v
```

每一项都能输出版本号，就说明安装成功。`tex -v` 正常示例：

```text
TeX 3.141592653 (TeX Live 2026)
```

> **必须用 XeLaTeX**：模板使用 `fontspec` / `xeCJK` 处理中文，pdfLaTeX 无法编译。

### 1.5 常见问题

- 装完命令仍找不到 → PATH 没生效，重开终端；确认路径精确到 `bin\windows`。
- 安装中断 → 重新运行安装程序，选择相同安装目录，它会续装。
- 宏包缺失 → `tlmgr install <包名>`。

---

## 2. VS Code 插件与配置

### 2.1 必装插件

| 插件 | ID | 用途 |
| --- | --- | --- |
| Claude Code for VS Code | `anthropic.claude-code` | AI Agent，直接在当前工作区生成报告 |
| LaTeX Workshop | `james-yu.latex-workshop` | 编译、预览、SyncTeX |
| Python | `ms-python.python` | 解释器选择、运行脚本 |
| Pylance | `ms-python.vscode-pylance` | 类型提示（随 Python 插件） |

---

## 3. Python 环境

1. **安装 Python 3.13**（<https://www.python.org/downloads/>），安装时勾选 **Add python.exe to PATH**，然后验证：

   ```bash
   python --version
   ```

2. **创建共享虚拟环境**（在 `文件位置\PHYLAB` 下，所有实验共用）：

   ```bash
   cd 文件位置\PHYLAB
   python -m venv .venv
   ```

3. **安装依赖**（每个实验的 `requirements.txt` 相同，装一次即可）：

   ```bash
   .venv\Scripts\pip.exe install -r "Phy_lab\src\requirements.txt"
   ```

4. **运行脚本**（始终用 venv 里的解释器，不要用全局 `python`）：

   ```bash
   ..\.venv\Scripts\python.exe src\双桥数据处理.py
   ```

5. **不知道怎么做的可以询问ai**

---

## 4. MinerU：教材 / 课件转 Markdown

### 4.0 为什么需要MinerU

md 文件更适合 ai 阅读，**省 token**

### 4.1 安装

在 [mineru.net](https://mineru.net) 进行在线转换或下载

### 4.2 支持格式

| 类型 | 扩展名 |
| --- | --- |
| PDF | `.pdf`（含扫描版） |
| 图片 | `.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp` `.tiff` |
| Word | `.doc` `.docx` |
| PowerPoint | `.ppt` `.pptx` |
| Excel | `.xls` `.xlsx` |
| 其他 | `.rtf` `.odt/.ods/.odp` `.epub` `.ofd` `.html` `.csv` `.tsv` |

`.md` / `.txt` / `.tex` 是纯文本，直接用编辑器或 Agent 读，不走 MinerU。

### 4.3 可以转换的内容

- **实验手册.pdf**
- **课件.ppt**
- **拍摄的实验数据照片**
- **拍摄的思考题**

## 5. 文件结构

```text
PHYLAB/
├── .venv/                  # 所有实验共用的 Python 环境
└── <实验全称>/
    ├── CLAUDE.md / AGENTS.md / Prompt.md   # Agent 工作流定义
    ├── Courseware/         # 教材、课件、课程安排.md、MinerU 转出的 md
    ├── References/         # 优秀报告参考
    ├── data/               # 原始数据（xlsx、照片）
    ├── src/                # 数据处理脚本 + requirements.txt
    ├── Template/           # LaTeX 模板（cls、底板、figures/）
    ├── Rst/                # 最终交付 PDF
    └── .vscode/settings.json   # LaTeX + Python 配置
```

---

## 6. 使用步骤

### 6.1 前置工作

1. **复制母版**

   复制Phy_lab文件夹并改名为实验全称（[下载 Phy_lab.zip](/Phy_lab.zip)）

2. **填写课程安排（可选，不写就每次自己填）**

   编辑 `Courseware/课程安排.md`，至少确认：
   - 实验全称（逐字，用于封面和 PDF 命名）
   - 上课周次（如“第4周”）
   - 任课教师
   - 实验地址 / 日期

3. **放课程资料**

   - 用 MinerU 将文件转成 Markdown
   - 讲义 PDF、课件 PPT 放入 `Courseware/`
   - 扫描的实验数据照片、实验过程照片放入 `data/images/`
   - 原始数据（md 或 excel） 放入 `data/`


4. **在 VS Code 打开实验目录**

   确认左下角 Python 解释器是 `PHYLAB\.venv`；若不是，命令面板 → `Python: Select Interpreter` → 选择 `.venv`。

5. **验证编译环境**

   打开 `Template/Preport底板.tex`，保存一次，确认能生成 PDF。首次编译可能需要十几秒。

### 6.2 写预习报告与实验报告

1. 启动 Agent：在 VS Code 中按 `Ctrl+Esc`（或点侧边栏 Claude 图标）打开 Claude Code 面板。它直接以当前工作区（实验目录）为根，会自动读取 `CLAUDE.md` 和 `Prompt.md`。

2. 给 Agent 的指令示例：

   > 读 `Prompt.md` 和 `Courseware/`，按 `Preport底板.tex` 写第 4 周“直流双臂电桥”的预习报告。实验名称、教师、周次从 `Courseware/课程安排.md` 取，不要臆造。写完编译并把 PDF 归档到 `Rst/`。


   或者
   > 按要求完成预习报告

3. Agent 会：
   - 读 `课程安排.md` 填封面
   - 读 MinerU 转出的 md 写实验原理
   - 按 `功能实例.tex` 的写法插公式、图、表
   - 用 `xelatex` 编译，检查日志
   - 按命名规则把 PDF 放进 `Rst/`

4. 人工检查：
   - 封面信息（姓名、学号、教师、周次、日期）
   - 公式编号与引用
   - 图表是否清晰、编号是否连续
   - 是否有模板指导性注释残留


### 6.4 编译与归档

命令行编译（在 `Template/` 目录下）：

```bash
cd Template
latexmk -xelatex "armbridge.tex"
latexmk -c          # 清理 aux/log/out 等临时文件
```

VS Code：保存自动编译，或 `Ctrl+Alt+B`。

归档到 `Rst/`，命名规则：

```text
预习报告：姓名-学号-实验名称预习报告-第x周.pdf
实验报告：姓名-学号-实验名称实验报告-第x周.pdf
```

示例：

```text
peago-3250100000-直流双臂电桥预习报告-第4周.pdf
peago-3250100000-直流双臂电桥实验报告-第4周.pdf
```

命名注意：

- 实验名称用 `课程安排.md` 里的**全称**，不得简写。
- Windows 不允许半角 `:`，遇到时替换为全角 `：`，并告知用户。
- “迈克尔逊干涉仪的应用G”末尾的 `G` 是类别标记，归档时删掉。
- 姓名/学号未知时先问用户，不要猜。

---



## 8. 常见问题

| 现象 | 原因 / 解决 |
| --- | --- |
| `xelatex: command not found` | TeX Live 的 `bin\windows` 未进 PATH；加完后重启终端和 VS Code |
| 中文变方框 / 乱码 | 用了 pdfLaTeX，或文件不是 UTF-8；改用 XeLaTeX，文件另存为 UTF-8 |
| Python 解释器不对 | 必须打开实验目录作为工作区；手动 `Python: Select Interpreter` 选 `.venv` |
| 其他任何问题 | 问 AI | 
---

## 9. 结语

本人经验有限，如果有问题欢迎评论或者私信我