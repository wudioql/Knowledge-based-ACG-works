# Astro ACG 知识库 - 实现计划 (tasks.md)

## [ ] Task 1: 项目脚手架与 Astro 配置
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 初始化 Astro 工程，生成 `package.json`、`astro.config.mjs`、`tsconfig.json`、`.gitignore`。
  - 安装并配置 `@astrojs/mdx` 集成；启用 `astro:assets` 支持。
  - 在 `astro.config.mjs` 中配置 `site` 与 `base`（默认 `/Knowledge-based_ACG_Astro_Wiki/`，由 `BASE_PATH` 环境变量覆盖）。
  - 添加 `pagefind` 的 `postbuild` 脚本与开发脚本 `npm run dev`。
- **Acceptance Criteria Addressed**: AC-1, AC-12
- **Test Requirements**:
  - `programmatic` TR-1.1: 在工作目录执行 `npm install` / `npm run build` 成功，`dist/index.html` 存在。
  - `programmatic` TR-1.2: `astro.config.mjs` 中存在 `integrations: [mdx()]` 配置项。
  - `programmatic` TR-1.3: `astro.config.mjs` 中 `base` 默认指向 `/Knowledge-based_ACG_Astro_Wiki/` 且可被环境变量覆盖。

## [ ] Task 2: Content Collections 与示例内容
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 创建 `src/content/config.ts`：定义通用 `chapterSchema`（`title: string`, `order: number`, `layoutType: enum('document' | 'gallery' | 'timeline')`, `themePalette: enum('ocean' | 'crimson' | 'amber')`, `isDraft: boolean`, 可选 `tags: string[]`, `summary: string`）。
  - 在 `src/content/<work>/` 目录中至少提供两个作品示例（`dr-stone/`, `maoyuu/`），每个作品包含 2+ 章节 MDX，覆盖三种 `layoutType`。
  - 将内容写入 `src/content/works-index.json` 或通过函数在 `config.ts` 中自动遍历作品子目录。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: `src/content/config.ts` 可被 Astro 正常导入；构建无 Schema 错误。
  - `programmatic` TR-2.2: 构建日志显示正确解析了 `dr-stone` 与 `maoyuu` 的章节。
  - `programmatic` TR-2.3: 故意删除某章节的 `title` 或 `order` 将导致 `npm run build` 失败。
  - `human-judgment` TR-2.4: 审阅示例 MDX 内容可读，Frontmatter 字段清晰。

## [ ] Task 3: 动态路由与页面生成
- **Priority**: P0
- **Depends On**: Task 2
- **Description**:
  - `src/pages/index.astro` 改为入口跳转或保留空壳（真正首页由 Task 14 设计）。
  - 创建 `src/pages/[work]/index.astro`（作品首页）：展示作品介绍 + 章节列表（按 `order` 升序），过滤草稿。
  - 创建 `src/pages/[work]/[...slug].astro`（章节详情页）：通过 `getStaticPaths` 生成所有章节；使用 `layoutType` 动态选择布局模板；基于 `themePalette` 挂载主题类。
  - 提供 `src/pages/404.astro`。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: `dist/` 下对每个作品生成 `index.html` 与对应章节 HTML 文件。
  - `programmatic` TR-3.2: 章节详情页的 `<body>` 上存在 `.theme-<palette>` 类。
  - `programmatic` TR-3.3: `dist/404.html` 存在。

## [ ] Task 4: 主题调色板与全局样式 (theme.css)
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 在 `src/styles/theme.css` 中定义基础变量与三套调色板（`ocean`, `crimson`, `amber`）：`--bg-color`, `--text-main`, `--text-muted`, `--accent-primary`, `--accent-secondary`, `--border-color`, `--code-bg`, `--shadow`, `--radius` 等。
  - 提供基础排版样式（行高、字体栈、代码块、blockquote、表格、列表）。
  - 在全局布局中导入 `theme.css`，并根据 Frontmatter `themePalette` 挂载对应类。
- **Acceptance Criteria Addressed**: AC-5, NFR-2
- **Test Requirements**:
  - `programmatic` TR-4.1: `theme.css` 存在且定义核心变量；`.theme-ocean/.theme-crimson/.theme-amber` 三套类存在。
  - `human-judgment` TR-4.2: 浏览器检查三种主题色彩对比度与可读性。

## [ ] Task 5: 三套布局模板组件
- **Priority**: P0
- **Depends On**: Task 3, Task 4
- **Description**:
  - `src/layouts/BaseLayout.astro`: 通用外壳（`<html><head>` + `<ViewTransitions/>` + 全局 CSS；通过 `theme` prop 挂载主题类）。
  - `src/layouts/DocLayout.astro`: 三栏：左侧章节总目录 / 中间正文 `<slot />` / 右侧动态大纲 TOC。
  - `src/layouts/TimelineLayout.astro`: 垂直时间线流式布局；为 `<TimelineNode>` 组件提供插槽/容器。
  - `src/layouts/GalleryLayout.astro`: CSS Grid 响应式网格，展示卡片。
  - 章节详情页按 Frontmatter 动态选择布局。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 三种布局组件文件存在；`DocLayout` 渲染时 DOM 含 `nav / main / aside` 三列。
  - `human-judgment` TR-5.2: 分别访问三种布局章节肉眼确认结构差异与响应式行为。

## [ ] Task 6: View Transitions 集成
- **Priority**: P0
- **Depends On**: Task 5
- **Description**:
  - 在 `BaseLayout` 中使用 `<ViewTransitions/>`。
  - 对跨章节链接确保都使用 Astro 原生 `<a>`（默认即可被 View Transitions 劫持）。
  - 配置简单 fade 过渡样式；对 `WorkNavigator` 与 `Pagination` 跳转同样生效。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: `BaseLayout.astro` 中出现 `<ViewTransitions />` 引用。
  - `human-judgment` TR-6.2: 浏览站点跨页切换无白屏，视觉平滑。

## [ ] Task 7: 动态大纲目录 TOC + ScrollSpy
- **Priority**: P0
- **Depends On**: Task 5
- **Description**:
  - 在 `src/utils/toc.ts` 编写从 Markdown 渲染头生成 `{ depth, text, slug }[]` 的函数。
  - 编写 `src/components/TableOfContents.astro`：渲染层级链接；支持手风琴折叠 `h3/h4`。
  - 编写 Island 组件 `src/components/toc.ts`：使用 `IntersectionObserver` 监听；高亮当前项；处理 View Transitions 重建。
  - 提供 CSS 使桌面端侧栏固定，移动端收缩为汉堡按钮+抽屉。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: `TableOfContents.astro` 生成层级结构 DOM，每条目带 `href="#<slug>"`。
  - `programmatic` TR-7.2: `toc.ts` Island 内使用 `new IntersectionObserver(...)` 注册。
  - `programmatic` TR-7.3: 构建产物中不存在未清理 observer 的 console 错误。
  - `human-judgment` TR-7.4: 桌面端 TOC 始终固定；窄屏显示汉堡按钮+抽屉；滚动高亮正常。

## [ ] Task 8: WorkNavigator 与 Pagination 组件
- **Priority**: P1
- **Depends On**: Task 3
- **Description**:
  - `src/components/WorkNavigator.astro`: 作品标签切换器，接收作品列表，高亮当前作品。
  - `src/components/Pagination.astro`: 接收当前章节的 `order`，按作品内排序结果生成"上一章/下一章"；首章禁用上一章、尾章禁用下一章。
  - 两组件都使用 `import.meta.env.BASE_URL` 处理路径。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-8.1: `Pagination` 渲染出前后两章的 `<a>` 带正确 `href`。
  - `programmatic` TR-8.2: `WorkNavigator` 渲染的作品列表包含全部非空作品。
  - `programmatic` TR-8.3: 首章节 `Pagination` 上一章按钮 `disabled` 或不渲染。

## [ ] Task 9: 图像渲染管线 (Astro Image)
- **Priority**: P1
- **Depends On**: Task 1
- **Description**:
  - 创建 `src/components/MdxImage.astro`（或等价封装）：使用 Astro `<Image/>`；`loading="lazy"`, `decoding="async"`, `width/height` 取自原始文件；输出 AVIF/WebP/JPEG。
  - 在 MDX 配置里通过 MDXComponents 替换 `<img>` 为 `MdxImage`。
  - 提供少量示例图片到 `src/assets/images/`（可用生成的占位图片或小文件）。
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-9.1: 渲染 HTML 中图片元素包含 `loading="lazy"` 与 `decoding="async"` 与显式 `width/height`。
  - `programmatic` TR-9.2: `<picture>` 元素含 AVIF/WebP `<source>`（或类似响应式替代）。

## [ ] Task 10: 按需加载组件 (Scroll-based Lazy Sections)
- **Priority**: P2
- **Depends On**: Task 5
- **Description**:
  - 提供 `src/components/LazySection.astro`：接收 `title`，以 `client:visible` 渲染其子内容块；首屏仅渲染占位。
  - 在示例章节中使用 `LazySection` 包裹长内容段，演示效果。
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `programmatic` TR-10.1: `LazySection.astro` 使用 `client:visible` 指令。
  - `human-judgment` TR-10.2: 浏览器网络面板在滚动到未视口段时才出现额外请求。

## [ ] Task 11: Pagefind 站内搜索（内联弹窗）
- **Priority**: P1
- **Depends On**: Task 3
- **Description**:
  - 将 `pagefind` 加入 `devDependencies`；`package.json` 的 `"postbuild": "pagefind --site dist"`。
  - 创建 `src/components/SearchModal.astro`（静态外壳）+ `src/components/search.ts`（Island，负责打开/关闭弹窗、挂载 Pagefind UI 到弹窗内）。
  - 在全局头部添加"搜索"按钮（`search-trigger`），点击打开遮罩弹窗。
  - 处理 Pagefind UI 的 basePath 以匹配 Astro 的 `base`，确保结果链接可导航。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-11.1: `postbuild` 执行后 `dist/pagefind/` 目录存在。
  - `programmatic` TR-11.2: 构建产物中可访问搜索组件，搜索关键字能返回命中项。
  - `programmatic` TR-11.3: 搜索结果 URL 前缀为 `${BASE_URL}`，不因 `base` 丢失而 404。
  - `human-judgment` TR-11.4: 搜索弹窗支持 Esc 关闭与点击遮罩关闭。

## [ ] Task 12: GitHub Pages 部署流水线
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 创建 `.github/workflows/deploy.yml`：`on: push: branches: [main]`；`permissions: pages: write, id-token: write`；jobs: `build`（Node 20+、`npm ci`、设置 `BASE_PATH=Knowledge-based_ACG_Astro_Wiki`、`npm run build`）→ `actions/upload-pages-artifact` → `actions/deploy-pages`。
  - 在 `astro.config.mjs` 中读取 `process.env.BASE_PATH` 作为 `base`。
- **Acceptance Criteria Addressed**: AC-12
- **Test Requirements**:
  - `programmatic` TR-12.1: `.github/workflows/deploy.yml` 存在并包含 `actions/upload-pages-artifact` 与 `actions/deploy-pages`。
  - `programmatic` TR-12.2: `astro.config.mjs` 使用环境变量拼接 `base`。
  - `human-judgment` TR-12.3: 文档中说明 Pages 配置步骤。

## [ ] Task 14: 首页 Landing Page（精心设计）
- **Priority**: P0
- **Depends On**: Task 2, Task 4, Task 8
- **Description**:
  - 重写 `src/pages/index.astro`：
    - Section 1 Hero：大标题、副标题、CTA 按钮（滚动到作品列表 + 搜索入口），背景使用渐变或装饰元素。
    - Section 2 特色亮点：2–4 张 `HeroCard`（基于组件）说明站点的核心能力（组块化管理、多主题、离线索引搜索、SPA 级体验等）。
    - Section 3 作品列表：在滚动到视口后进入视图；使用 `Card` 网格展示每个作品（封面、标题、summary、tag、章节数、跳转链接）。
  - 确保使用 `<ViewTransitions/>` 过渡，并可切换主题。
- **Acceptance Criteria Addressed**: AC-14
- **Test Requirements**:
  - `programmatic` TR-14.1: `dist/index.html` 包含 `hero` 与 `works-list` 两个区。
  - `human-judgment` TR-14.2: 首页视觉精致，渐变/动画/交互正常；CTA 点击可滚动或跳转。
  - `human-judgment` TR-14.3: 作品卡片网格响应式（桌面 3 列、平板 2 列、手机 1 列）。

## [ ] Task 15: MDX 自定义组件白名单与实现
- **Priority**: P1
- **Depends On**: Task 1, Task 9
- **Description**:
  - 在 `src/components/mdx/` 下实现以下组件，全部作为 MDX 自定义元素：
    1. `Callout.astro`：便签/提示块（`type: info|warning|success|note`、`title`、`body via slot`）。
    2. `HeroCard.astro`：带图标/渐变背景的功能卡片。
    3. `Card.astro`：通用作品/内容卡片（封面、标题、摘要、标签）。
    4. `ImageGallery.astro`：图片瀑布流/网格，内部用 `<Image/>`。
    5. `TimelineNode.astro`：时间线节点（日期、标题、描述）。
    6. `InfoGrid.astro`：键值对信息网格（如角色介绍数据）。
    7. `Quote.astro`：带署名的引用块。
    8. `Divider.astro`：带文字的装饰分割线。
    9. `TagList.astro`：标签云/标签列表。
    10. `Aside.astro`：侧栏式提示（内容旁的注释型块）。
  - 在 `astro.config.mjs` 的 `mdx()` 集成里通过统一 MDXComponents 映射（或在布局中通过 slot 上下文注入）暴露这些组件；同时将默认的 `img` 映射为 `MdxImage`。
- **Acceptance Criteria Addressed**: AC-15
- **Test Requirements**:
  - `programmatic` TR-15.1: `src/components/mdx/` 下至少存在上述 10 个组件文件。
  - `programmatic` TR-15.2: 构建配置/布局源码中存在显式 MDXComponents 映射。
  - `human-judgment` TR-15.3: 在示例章节中使用各组件渲染，视觉多样且无冲突。

## [ ] Task 13: README 与 Code Wiki 文档
- **Priority**: P1
- **Depends On**: Task 2–12、14、15
- **Description**:
  - `README.md`: 项目简介、技术徽章、本地开发指令、目录结构树、5 分钟作者指南、常见问题。
  - `docs/code-wiki.md`: 架构分层设计思想、Zod Schema 字段表、核心组件 API（含 10+ MDX 组件）、状态与生命周期（TOC IntersectionObserver 清理与 View Transitions 钩子）、部署排错指南（base 路径、Pagefind 索引缺失、MDX Schema 错误）。
- **Acceptance Criteria Addressed**: AC-13
- **Test Requirements**:
  - `human-judgment` TR-13.1: 新成员 5 分钟内理解"如何新增一个作品集合"。
  - `human-judgment` TR-13.2: Code Wiki 至少列出 10 个 MDX 组件的 props。
