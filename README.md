# ACG 知识手册库

[![Deploy](https://github.com/wudioql/Knowledge-based_ACG_works/actions/workflows/deploy.yml/badge.svg)](https://github.com/wudioql/Knowledge-based_ACG_works/actions/workflows/deploy.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://wudioql.github.io/Knowledge-based_ACG_works/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> 从动漫与游戏中挖掘真实世界知识，建立「虚构作品内容 ↔ 学术理论 ↔ 真实历史」的三方对照体系。

---

## 项目概览

### 核心理念

本项目试图回答一个问题：**一部优秀的 ACG 作品，除了娱乐价值，还能带给我们什么？**

许多作品在虚构叙事中融入了真实的知识体系——经济学原理、政治制度、料理科学、历史事件。本项目将这些隐藏的知识脉络梳理出来，建立三方对照，让作品成为通往真实知识世界的入口。

```mermaid
graph LR
    A[虚构作品内容] --> B[学术理论]
    A --> C[真实历史]
    B --> C
```

### 设计哲学

#### 一作一貌原则

本项目坚持「一作一貌」的设计理念：每部 ACG 作品的知识手册都应拥有独立的视觉个性，反映原作的内容气质。我们刻意避免所有作品使用相同的页面骨架、字体和布局模式。

#### 差异化维度

每部作品在以下维度上必须有意识地做出差异化选择：

- **字体组合**：标题字体 + 正文字体，需匹配作品气质（参见 [字体政策](docs/CODE_WIKI.md#字体政策)）
- **色彩体系**：主色、辅色、背景色需反映作品世界观
- **页面骨架**：不强制统一的 header → hero → main → footer 结构
- **布局模式**：卡片网格、列表、时间线、双栏对照等，按内容特点选择
- **交互模式**：筛选、折叠、标签页、轮播等，按用户浏览场景选择

#### 共享与独立

- **共享层**（`_shared/`）：仅包含「返回主页按钮」等跨作品通用功能
- **独立层**（`doc/作品名/_shared/`）：每部作品的 CSS/JS 完全独立编写，不要求遵循统一的变量命名或组件结构

### 在线访问

**[https://wudioql.github.io/Knowledge-based_ACG_works/](https://wudioql.github.io/Knowledge-based_ACG_works/)**

### 作品总览

| 作品 | 知识领域 | 内容类型 | 视觉风格 | 状态 |
|------|----------|----------|----------|------|
| [魔王勇者](doc/maoyuu/) | 政治经济学 | 手册 | 学术冷色调 · Lora + WorkSans · 卷卡网格 | 已完成 |
| [食戟之灵](doc/shokugeki_no_soma/) | 料理学 | 全鉴 | 料理暖色调 · Lora + WorkSans · 篇章卡片 | 已完成 |
| *(预留)* | | | | |

---

## 快速开始

### 在线浏览

直接访问 **[GitHub Pages 站点](https://wudioql.github.io/Knowledge-based_ACG_works/)** 即可浏览所有内容，无需安装任何依赖。

### 本地预览

```bash
git clone https://github.com/wudioql/Knowledge-based_ACG_works.git
cd Knowledge-based_ACG_works
# 直接用浏览器打开 index.html，或用任意静态服务器
python3 -m http.server 8080
```

本项目为纯静态网站，**零依赖、零构建步骤**。

---

## 项目特性

- **三方对照体系**：每部作品的内容都与学术理论和真实历史建立对照
- **一作一貌**：每部作品拥有独立视觉设计，反映原作气质
- **纯静态架构**：HTML + CSS + JavaScript，无需构建工具，长期可维护
- **自动部署**：推送至 GitHub 后自动部署到 GitHub Pages
- **响应式设计**：适配桌面端与移动端阅读
- **内容拆分**：按章节 / 卷 / 篇章独立成页，保持单文件可控（参见 [内容拆分政策](docs/CODE_WIKI.md#内容拆分政策)）
- **知识可视化**：合理使用 Mermaid 图表、SVG 图示优化知识呈现（参见 [可视化规范](docs/CODE_WIKI.md#可视化规范)）

---

## 技术架构

| 类别 | 技术 | 说明 |
|------|------|------|
| 页面结构 | HTML5 | 原生，无框架 |
| 样式 | CSS3 | 原生，无预处理器 |
| 交互 | Vanilla JavaScript | 原生，无框架 |
| 部署 | GitHub Actions + GitHub Pages | 自动触发 |
| 字体 | Google Fonts（在线引入） | 每部作品独立选择，参见 [字体政策](docs/CODE_WIKI.md#字体政策) |

详细架构说明请参阅 [docs/CODE_WIKI.md](docs/CODE_WIKI.md)。

---

## 内容体系

### 按知识领域分类

| 领域 | 现有作品 | 潜在方向 |
|------|----------|----------|
| 政治经济学 | 魔王勇者 | 国际关系、制度经济学 |
| 料理科学 | 食戟之灵 | 食品化学、营养学 |
| 历史学 | — | 军事史、科技史 |
| 自然科学 | — | 物理学、生物学 |

### 按内容类型分类

| 类型 | 说明 | 推荐视觉模式 | 示例 |
|------|------|-------------|------|
| 手册 | 按章节系统梳理知识点，附学术对照 | 学术风格，双栏对照表，侧边目录 | 魔王勇者 |
| 全鉴 | 逐条目详解，附技术拆解 | 图文并茂，卡片流，沉浸式排版 | 食戟之灵 |
| 年表 | 按时间线整理事件与史实对照 | 垂直时间线，节点式布局 | *(预留)* |
| 地图 | 地理设定与真实地理 / 历史对照 | 交互式地图，标注式信息卡 | *(预留)* |

---

## 参与贡献

欢迎提交新的 ACG 知识整理！无论是新增作品、补充现有内容，还是修正错误，都可以通过以下方式参与：

- **提交 Issue**：报告内容错误或提出新作品建议
- **提交 Pull Request**：按照 [添加新作品指南](docs/CODE_WIKI.md#添加新作品指南) 添加新作品
- **内容讨论**：在 Issue 区讨论知识点的准确性与深度

> **重要**：添加新作品前，请务必阅读 [视觉身份差异化指南](docs/CODE_WIKI.md#视觉身份差异化指南)，确保新作品的视觉设计与已有作品存在显著差异。

---

## 文档导航

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 本文档，项目概览与设计哲学 |
| [docs/CODE_WIKI.md](docs/CODE_WIKI.md) | 开发者文档：架构规范、视觉身份差异化、字体政策、内容拆分、可视化规范、扩展指南 |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | 内容贡献指南（待完善） |

---

## 许可证与免责声明

本项目采用 [MIT License](LICENSE) 开源。

本站为粉丝自发整理的非官方内容。所有资料基于原作及公开学术资源整理，仅供学习交流使用。作品版权归原作者及出版社所有。
