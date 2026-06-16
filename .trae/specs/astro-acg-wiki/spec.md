# Astro ACG 知识库 - 产品需求文档 (PRD)

## Overview
- **Summary**: 基于最新版 Astro 构建的纯静态 ACG 作品知识库站点，通过 Content Collections 实现作品组块化管理，支持多种布局模板与多主题调色板，集成 View Transitions、Pagefind 内联弹窗搜索和 GitHub Pages 自动化部署，并精心设计首页以提升访问体验，为内容创作者提供"零代码新增作品"的协作体验。
- **Purpose**: 解决传统单文件长文维护困难、样式与内容耦合紧密、部署繁琐、阅读体验碎片化的问题，构建一个高性能、易维护、可扩展的 ACG 内容聚合平台。
- **Target Users**: ACG 内容创作者（编辑词条）、前端维护者（维护组件/布局）、最终读者（浏览作品、搜索内容）。

## Goals
- 提供基于 Astro + MDX 的纯静态内容管理系统（SSG）
- 通过 Content Collections + Zod Schema 实现强类型内容元数据管理
- 实现 Doc/Timeline/Gallery 三类通用布局模板与多套 CSS 变量调色板
- 全局启用 View Transitions 带来 SPA 级页面切换体验
- 集成 Pagefind 提供离线索引的内联弹窗站内全文搜索
- 提供智能大纲目录（TOC），带滚动监听与响应式抽屉
- 提供跨作品导航器与章节上下页翻页
- 通过 `<Image/>` 组件与 `client:visible` 实现图像/内容按需加载
- 提供丰富的 MDX 自定义组件白名单（Callout、HeroCard、Card、ImageGallery、TimelineNode、InfoGrid、Quote、Divider 等），避免视觉疲劳
- 提供精心设计的首页（Hero + 作品介绍 + 滚动后出现的作品列表）
- 提供 GitHub Pages 一键部署的 CI/CD 流水线
- 提供 README 与 Code Wiki 文档，降低新作品接入门槛

## Non-Goals (Out of Scope)
- 不实现任何需要服务端运行时（SSR/ISR/Edge）的功能
- 不实现用户账号、登录评论、点赞收藏等动态交互功能
- 不实现独立数据库或后端 API 服务
- 不实现 CMS 后台编辑器；内容通过本地 MDX 管理
- 不实现富文本 WYSIWYG 编辑器；创作采用原生 MDX 文件
- 不提供付费墙、多语言 i18n、RSS 订阅等高级扩展（后续可增量）

## Background & Context
- Astro 是围绕"零 JavaScript by default"设计的静态站点框架，天然适合文档/知识库场景。
- 内容创作者通常不熟悉前端工程，但熟悉 Markdown；将"新建作品"简化为"新增 MDX + 配置 Frontmatter"是关键体验目标。
- 本项目不假定已有代码仓库，所有基础设施需在本次迭代中从零搭建。
- 仓库名 `Knowledge-based_ACG_Astro_Wiki` 已确定，部署 `base` 路径为 `/Knowledge-based_ACG_Astro_Wiki/`。
- Pagefind 通过 postbuild 钩子生成索引，其产物应与 `dist/` 一并发布。
- 搜索体验使用内联弹窗（不引入独立 `/search/` 页）。

## Functional Requirements
- **FR-1 (项目脚手架)**: 使用最新 Astro 创建工程，集成 `@astrojs/mdx`，配置 `site` / `base` 以支持 GitHub Pages（base=`/Knowledge-based_ACG_Astro_Wiki/`）。
- **FR-2 (Content Collections)**: 在 `src/content/` 下建立"作品→章节"层级；定义通用 Zod Schema（`title`, `order`, `layoutType`, `themePalette`, `isDraft`，可选 `tags`, `summary`）。
- **FR-3 (动态路由)**: 基于 `getStaticPaths` 为每个作品集合生成章节详情页；作品列表页枚举所有已发布作品。
- **FR-4 (布局模板)**: 实现 `DocLayout`（三栏：目录/正文/大纲）、`TimelineLayout`（时间线流）、`GalleryLayout`（响应式网格）；均接受 `<slot/>` 内容。
- **FR-5 (主题引擎)**: 在 `theme.css` 中定义多套 CSS Custom Properties 调色板；根据 Frontmatter `themePalette` 动态挂载 `.theme-xxx` 类。
- **FR-6 (View Transitions)**: 在全局布局中插入 `<ViewTransitions/>`；确保跨作品/跨章节路由切换保持局部 DOM 替换、无白屏。
- **FR-7 (动态大纲目录 TOC)**: 解析 MDX `h2/h3/h4` 生成层级；通过 `IntersectionObserver` 实现 ScrollSpy；支持平滑滚动、手风琴折叠、移动端抽屉。
- **FR-8 (Pagefind 搜索)**: 在 postbuild 中生成索引；提供搜索输入框组件；搜索结果以**内联弹窗**展示，点击跳转到对应章节（带 `base` 路径）。
- **FR-9 (WorkNavigator / Pagination)**: 在作品列表中渲染作品切换器；在章节底部依据 `order` 自动渲染"上一章/下一章"翻页。
- **FR-10 (图像管线)**: 使用 Astro `<Image/>` 组件处理 `assets/images/` 下的本地图片；启用 `loading="lazy"` / `decoding="async"` / 自动 AVIF/WebP。
- **FR-11 (按需加载)**: 对长内容分段使用 `client:visible` 或 `IntersectionObserver` 占位组件；保证首屏不阻塞。
- **FR-14 (首页)**: 精心设计 `src/pages/index.astro`：首屏 Hero 区 + 作品介绍/特色卡片；向下滚动后作品列表区进入视图。
- **FR-15 (MDX 组件白名单)**: 提供丰富的 MDX 自定义组件（`Callout`, `HeroCard`, `Card`, `ImageGallery`, `TimelineNode`, `InfoGrid`, `Quote`, `Divider`, `TagList`, `Aside`），在 `src/components/mdx/` 目录中实现，并在 MDX 配置里显式注册，禁止创作期使用未注册组件。
- **FR-12 (部署流水线)**: `.github/workflows/deploy.yml` 使用 `actions/upload-pages-artifact` + `actions/deploy-pages`；Push 到 `main` 即发布。
- **FR-13 (文档)**: 提供 `README.md`（简介/徽章/启动/目录结构/5分钟作者指南）与 Code Wiki（架构、Schema、组件 API（含 MDX 白名单）、状态生命周期、部署排错）。

## Non-Functional Requirements
- **NFR-1 (性能)**: 首屏无明显阻塞资源；LCP ≤ 2.5s；CLS ≈ 0（由 `<Image/>` 显式尺寸保证）。
- **NFR-2 (可访问性)**: 侧栏 TOC 支持键盘 Tab 导航与回车激活；配色对比度满足 WCAG AA。
- **NFR-3 (可维护性)**: 新增作品不需要修改组件/路由代码，仅需新增 MDX 集合与 Frontmatter。
- **NFR-4 (构建产物)**: `npm run build` 零错误，MDX 元数据违反 Schema 时构建失败（fail-fast）。
- **NFR-5 (工程规范)**: 目录结构遵循 Astro 官方惯例；MDX 组件通过显式白名单暴露。

## Constraints
- **Technical**: Astro（最新稳定版）、TypeScript、`@astrojs/mdx`、`astro:assets`、Pagefind CLI；不引入 React/Vue 等前端 UI 框架（Astro Islands 足够）。
- **Business**: 仓库名 `Knowledge-based_ACG_Astro_Wiki`；`base: /Knowledge-based_ACG_Astro_Wiki/`；所有内容通过 Git 提交管理。
- **Dependencies**: `@astrojs/mdx`, `zod`, `pagefind`（devDependency），`astro` 内置 Image 组件；可能需要 `sharp` 作为可选图像处理依赖。

## Assumptions
- 创作流程默认在本地 `npm run dev` 中完成，再提交 Git。
- 每个作品至少包含 1 个章节；空集合将被过滤。
- Pagefind 生成的静态索引体积对于中小规模知识库（< 500 条）完全可接受。
- MDX 自定义组件在构建期通过统一 MDXComponents 映射暴露给 MDX 文件使用。

## Acceptance Criteria

### AC-1: 项目脚手架与 Astro 配置
- **Given**: 空仓库 `/workspace`
- **When**: 执行 `npm install` 与 `npm run build`
- **Then**: 构建成功，输出静态站点到 `dist/`，`astro.config.*` 中定义了正确的 `site` 与 `base=/Knowledge-based_ACG_Astro_Wiki/` 以及 `@astrojs/mdx` 集成
- **Verification**: `programmatic`

### AC-2: Content Collections 与 Zod Schema
- **Given**: `src/content/config.ts` 已创建并导出集合；至少存在 `dr-stone/`, `maoyuu/` 两个作品，各含若干章节 MDX
- **When**: 执行 `npm run build`
- **Then**: 构建能从各作品集合中按 `order` 升序渲染章节；带 `isDraft: true` 的条目在生产构建中被过滤；Schema 字段缺失时构建失败
- **Verification**: `programmatic`

### AC-3: 作品与章节路由
- **Given**: 已定义两个作品集合
- **When**: 访问 `/<work>/` 与 `/<work>/<slug>/`
- **Then**: 返回 200，页面内容正确；不存在章节返回 404
- **Verification**: `programmatic`

### AC-4: 三套布局模板解耦
- **Given**: Frontmatter 中分别声明 `layoutType: 'document' | 'gallery' | 'timeline'`
- **When**: 渲染不同章节
- **Then**: 页面结构对应切换（三栏 / 网格 / 时间线）；样式无交叉污染；新增作品时无需新增 CSS 或布局文件
- **Verification**: `human-judgment`

### AC-5: CSS 变量调色板动态挂载
- **Given**: Frontmatter 中声明 `themePalette: 'ocean' | 'crimson' | 'amber'`
- **When**: 渲染章节
- **Then**: `<body>` 或根容器自动挂载 `.theme-ocean` 等类；全局变量 `--bg-color / --text-main / --accent-primary` 随主题变化
- **Verification**: `programmatic`（DOM class 检查）+ `human-judgment`（视觉观感）

### AC-6: View Transitions 无白屏切换
- **Given**: 在站点内点击跨章节或跨作品链接
- **When**: 浏览器支持 View Transitions
- **Then**: 路由切换为局部 DOM 替换，无整页刷新白屏；滚动位置在合理范围内保留
- **Verification**: `human-judgment`

### AC-7: 动态大纲目录与 ScrollSpy
- **Given**: 章节内容含多个 `h2/h3/h4`
- **When**: 滚动页面或点击 TOC 条目
- **Then**: 当前标题在 TOC 中高亮；点击后平滑滚动至锚点；`h3/h4` 支持手风琴折叠；移动端自动收缩为抽屉菜单
- **Verification**: `programmatic`（`IntersectionObserver` 存在）+ `human-judgment`（交互体验）

### AC-8: Pagefind 站内搜索（内联弹窗）
- **Given**: 构建完成并生成 Pagefind 索引
- **When**: 在顶部搜索输入框输入关键字
- **Then**: 以遮罩弹窗形式展示搜索结果；点击结果跳转到正确 URL（含 `base` 路径）；索引包含标题、标签、正文片段
- **Verification**: `programmatic`

### AC-9: WorkNavigator 与 Pagination 组件
- **Given**: 当前位于某章节页
- **When**: 查看顶部/底部组件
- **Then**: WorkNavigator 列出可切换作品；Pagination 显示"上一章/下一章"；`order` 边界时首/尾按钮禁用
- **Verification**: `programmatic`

### AC-10: Image 渲染管线
- **Given**: `src/assets/images/` 下存在若干图片；章节内容通过 Astro `<Image/>` 或 MDX 自定义组件引用
- **When**: 构建与渲染
- **Then**: 图片有显式 `width/height`（防 CLS），`loading="lazy"`，`decoding="async"`，且生成 AVIF/WebP 响应式 `<source>`
- **Verification**: `programmatic`（DOM 属性检查）

### AC-11: 按需加载（Scroll-based Lazy Sections）
- **Given**: 页面内包含长内容分段，使用 `client:visible` 或 IntersectionObserver 占位组件
- **When**: 滚动使分段进入视口
- **Then**: 该分段懒挂载，首屏仅渲染可见部分；无首次加载时的网络瀑布阻塞
- **Verification**: `human-judgment` + 网络面板观察

### AC-12: GitHub Pages 自动化部署
- **Given**: 仓库存在 `.github/workflows/deploy.yml`，使用 `actions/upload-pages-artifact` 与 `actions/deploy-pages`
- **When**: 向 `main` 分支 Push
- **Then**: CI 成功，站点在 `https://<user>.github.io/Knowledge-based_ACG_Astro_Wiki/` 可访问；CSS/JS/图片路径包含正确 `base`
- **Verification**: `programmatic`（CI 绿）+ `human-judgment`（站点可访问检查）

### AC-13: README 与 Code Wiki
- **Given**: 项目根目录与 `docs/` 目录
- **When**: 新成员克隆并阅读文档
- **Then**: 5 分钟内理解如何新增作品集合与 Frontmatter；Code Wiki 覆盖架构、Schema、组件 API（含 MDX 白名单）、状态生命周期、部署排错
- **Verification**: `human-judgment`

### AC-14: 精心设计的首页
- **Given**: 访问 `/`
- **When**: 查看首页
- **Then**: 首屏显示 Hero 区（标题 + 副标题 + CTA 按钮 + 渐变背景）+ 特色亮点；向下滚动后进入作品列表区，作品卡片可点击跳转
- **Verification**: `human-judgment` + `programmatic`（DOM 存在 hero 与 works-list 两节）

### AC-15: MDX 自定义组件白名单
- **Given**: 在章节 MDX 中使用白名单组件
- **When**: 构建与渲染
- **Then**: `Callout`, `HeroCard`, `Card`, `ImageGallery`, `TimelineNode`, `InfoGrid`, `Quote`, `Divider`, `TagList`, `Aside` 等至少 10 个组件正常渲染且视觉多样；未在白名单中的组件会导致构建期警告或未知组件错误
- **Verification**: `programmatic`（组件源码存在 + MDXComponents 映射）+ `human-judgment`（视觉多样）

## Open Questions（已解决）
- [x] 仓库名：`Knowledge-based_ACG_Astro_Wiki`；部署 `base=/Knowledge-based_ACG_Astro_Wiki/`
- [x] 首页：精心设计的 Hero + 滚动后作品列表
- [x] 搜索：内联弹窗（无独立 `/search/` 页）
- [x] MDX 自定义组件：提供丰富白名单（≥10 个组件），防视觉疲劳与误写
