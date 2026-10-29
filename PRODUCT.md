# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

四类读者，优先级按用户给出的顺序：

1. **站主自己** — 主要读者。写完后回头查阅笔记、投资复盘、简报。站点同时是个人知识库。
2. **同学和朋友** — 看近况、资源分享、闲聊内容。
3. **陌生访客** — 从 GitHub、简历或分享链接进入。第一需求是「这个人是谁、在做什么」。
4. **同行技术读者** — 看具体内容：学习笔记、计算器工具、投资分析。

## Product Purpose

peago（管云哲）的个人主页，兼个人知识库。四个栏目各自记录一类长期内容：

- `learning/` — 学习 · 资源、笔记
- `investing/` — 投资 · 记录与复盘
- `horizon/` — 简报 · 每晚 9 点
- `prattling/` — 发电 · 空想家的自我修养

用户确认的成功标准，三条同时成立：

- 持续产出不断线。
- 陌生访客能顺畅读完，愿意分享或联系。
- 笔记和工具真有使用价值，站主会回头复用。

## Positioning

内容不是静态的自我介绍，而是持续运转的记录：简报每日自动生成，估值快照每日更新，部分页面是可交互的工具而非文章。这一点是同类个人主页常见形态里没有的。

> 本段由仓库证据推导（`.github/workflows/horizon-daily.yml`、`update-valuation.yml`、`layouts/learning/calculator.html`）。用户未逐句确认。

## Operating Context

- 写作环境：本地。可用 `python tools/editor.py` 启动 Markdown 编辑器（`http://127.0.0.1:8765/`），GitHub 凭据取自 `gh auth token`，页面不存凭据。
- 简报流程：`.github/workflows/horizon-daily.yml` 每晚生成。主路径是外部 cron 服务触发 `workflow_dispatch`；GitHub 自带的 schedule 只作 21:45 / 23:45（北京）兜底，且当天已存在时跳过。
- 估值数据：`.github/workflows/update-valuation.yml` 每日写入 `static/data/valuation.json`。
- 构建发布：`build.yml` 在推送后构建，产物提交到 `docs/`，由 GitHub Pages 提供。

## Capabilities and Constraints

**技术栈（现状，不是用户声明的固定约束）**

Hugo 静态站，`publishDir = 'docs'`，中文内容，`disableKinds = ['taxonomy', 'term']`（不使用标签与分类归档）。

**固定约束（用户确认）**

- 四个栏目的划分与命名必须保留：`learning` / `investing` / `horizon` / `prattling`。

**可替换部分（用户未列为必须保留）**

- 视觉语言（当前为 ASCII banner、分区 ascii 动图、等宽排版）。
- 构建栈与部署链路（Hugo、GitHub Pages、`docs/` 发布）。
- Horizon 每日自动简报流程。

**已知陷阱**

- Hugo 按 UTC 解析 front matter 日期。北京时间早上写「今天」作日期，文章会被当成未来时间，静默不构建。
- `content/` 下文章 `draft` 默认 `true`，见 `archetypes/default.md`。

**本地工具目录 `tools/`**

`editor.html` + `editor.py`（本地写作页）、`yq-replace.html`、`频域复数计算器.html`。这些是工作副本，发布出去的是 `layouts/` 与 `content/` 里的版本。

## Brand Commitments

- 名称固定：`peago · 空想家`。
- 身份事实：浙江大学，电子科学与技术，大二在读。
- 联系方式：`peago@foxmail.com`、`github.com/peagothedreamer`、微信 `peagothedreamer`。
- 用户未对语气、字体、配色作出约束性声明。

## Evidence on Hand

真实内容，可直接引用，不需要编造：

- 23 篇 `content/` 文章，其中 10 篇 Horizon 每日简报。
- 投资分析 3 篇：`marks-ruminating-on-asset-allocation.md`、`storage-cycle-pe-trap.md`、`valuation-percentile.md`。
- 学习页 4 篇，含可交互的频域复数计算器（`layouts/learning/calculator.html`）。
- 本地资产：banner 为 `static/banner/peago.svg` 与 `peago.dark.svg`（浅/深色各一）；音乐播放器与专辑音频在 `static/audio/`；Giscus 评论主题在 `static/giscus/`。
- 归档包 `static/Phy_lab.zip`。

不得编造：客户、用户量、奖项、合作方、商业数据。

## Product Principles

1. **内容优先。** 判断改动价值时，先看它是否让「持续写」更容易，还是只让外观更好看。
2. **四类读者都要能读。** 首页必须让陌生人三秒内知道这个人是谁、在做什么；栏目页要能直接进入内容。
3. **结构稳，表现可变。** 栏目划分不动；其余视觉与实现可以整体替换。
4. **工具要真能用。** 交互页面按工具标准做，不按展示品做：输入合法、结果正确、出错有说明。
