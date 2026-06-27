from __future__ import annotations

from copy import deepcopy
from math import cos, pi, sin
from pathlib import Path

from .common import (
    CONTENT_PREFIXES,
    DATA_PATH,
    DEFAULT_DOMAIN_ID,
    DEFAULT_DOMAIN_LABEL,
    DEFAULT_MEDIUM_ID,
    DEFAULT_MEDIUM_LABEL,
    DOCS_ROOT,
    HANDBOOKS_PATH,
    METRICS_PATH,
    OUTPUT_PATH,
    ROOT,
    SUPPORT_PREFIXES,
    e,
    load_json,
    render_links,
    save_json,
    unique,
)


# ── Data-processing helpers (unchanged) ──

def discover_html_files(folder: str) -> list[Path]:
    work_dir = DOCS_ROOT / folder
    if not work_dir.exists():
        return []
    return sorted(work_dir.glob("*.html"))


def analyze_handbook_pages(folder: str) -> dict[str, object]:
    files = discover_html_files(folder)
    total = len(files)
    content_pages = 0
    support_pages = 0
    other_pages = 0
    first_content: str | None = None

    for file in files:
        stem = file.stem
        if stem == "index":
            continue
        if stem.startswith(CONTENT_PREFIXES):
            content_pages += 1
            first_content = first_content or file.name
        elif stem.startswith(SUPPORT_PREFIXES) or stem in SUPPORT_PREFIXES:
            support_pages += 1
        else:
            other_pages += 1
            first_content = first_content or file.name

    content_like_pages = content_pages + other_pages
    return {
        "totalPages": total,
        "contentPages": content_pages,
        "contentLikePages": content_like_pages,
        "supportPages": support_pages,
        "otherPages": other_pages,
        "firstContentPage": first_content,
    }


def build_label_maps(data: dict[str, object]) -> tuple[dict[str, str], dict[str, str], dict[str, int]]:
    domain_labels = {domain["id"]: domain["title"] for domain in data["domains"]}
    domain_labels.setdefault(DEFAULT_DOMAIN_ID, DEFAULT_DOMAIN_LABEL)
    domain_order = {domain["id"]: index for index, domain in enumerate(data["domains"])}
    medium_labels = {
        item["value"]: item["label"]
        for item in data["filters"]["medium"]
        if item["value"] != "all"
    }
    medium_labels.setdefault(DEFAULT_MEDIUM_ID, DEFAULT_MEDIUM_LABEL)
    return domain_labels, medium_labels, domain_order


HERO_THEME_COLORS = {
    "life": "#18968b",
    "food": "#d56a1b",
    "micro": "#6a9d32",
    "society": "#c24b6b",
    "history": "#a76a2a",
    "space": "#3f66d8",
    "misc": "#5c687a",
}


def split_title_lines(title: str) -> list[str]:
    if "、" in title:
        left, right = title.split("、", 1)
        return [left + "、", right]
    if "与" in title and len(title) > 6:
        left, right = title.split("与", 1)
        return [left + "与", right]
    if len(title) > 8:
        middle = len(title) // 2
        return [title[:middle], title[middle:]]
    return [title]


DOMAIN_GLYPH = {
    "life": "生", "food": "食", "micro": "菌",
    "society": "政", "history": "史", "space": "航",
}


def normalize_domains(raw_domain: object, domain_labels: dict[str, str]) -> list[str]:
    if raw_domain is None:
        return [DEFAULT_DOMAIN_ID]
    values = [raw_domain] if isinstance(raw_domain, str) else list(raw_domain)
    normalized: list[str] = []
    for value in values:
        domain = str(value).strip()
        if not domain or domain not in domain_labels:
            domain = DEFAULT_DOMAIN_ID
        normalized.append(domain)
    return unique(normalized or [DEFAULT_DOMAIN_ID])


def normalize_mediums(raw_medium: object, medium_labels: dict[str, str]) -> list[str]:
    if raw_medium is None:
        return [DEFAULT_MEDIUM_ID]
    values = [raw_medium] if isinstance(raw_medium, str) else list(raw_medium)
    normalized: list[str] = []
    for value in values:
        medium = str(value).strip()
        if not medium or medium not in medium_labels:
            medium = DEFAULT_MEDIUM_ID
        normalized.append(medium)
    return unique(normalized or [DEFAULT_MEDIUM_ID])


def infer_scale(entry: dict[str, object], page_stats: dict[str, object]) -> str:
    if entry.get("scale"):
        return str(entry["scale"])
    total = int(page_stats["totalPages"])
    content_like = int(page_stats["contentLikePages"])
    support = int(page_stats["supportPages"])
    if total == 0:
        return "已收录页面待补充"
    details: list[str] = []
    if content_like:
        details.append(f"{content_like} 个内容页")
    if support:
        details.append(f"{support} 个辅助页")
    if details:
        return f"共 {total} 个页面（含 {'，'.join(details)}）"
    return f"共 {total} 个页面"


def infer_structure(entry: dict[str, object], page_stats: dict[str, object]) -> str:
    if entry.get("structure"):
        return str(entry["structure"])
    total = int(page_stats["totalPages"])
    content_like = int(page_stats["contentLikePages"])
    support = int(page_stats["supportPages"])
    if total == 0:
        return "目录结构待整理。"
    parts = ["目录页"]
    if content_like:
        parts.append(f"{content_like} 个内容页")
    if support:
        parts.append(f"{support} 个辅助页")
    return " + ".join(parts) + "。"


def infer_start_here(entry: dict[str, object], page_stats: dict[str, object]) -> str:
    if entry.get("startHere"):
        return str(entry["startHere"])
    if page_stats.get("firstContentPage"):
        return "先从作品首页开始，再进入首个内容页。"
    return "先从作品首页开始。"


def normalize_handbooks(data: dict[str, object], registry: list[dict[str, object]]) -> list[dict[str, object]]:
    domain_labels, medium_labels, domain_order = build_label_maps(data)
    works: list[dict[str, object]] = []

    for index, entry in enumerate(registry):
        folder = str(entry["folder"]).strip()
        title = str(entry["title"]).strip()
        raw_domains = entry.get("domains", entry.get("domain"))
        domains = normalize_domains(raw_domains, domain_labels)
        primary_domain = next((domain for domain in domains if domain != DEFAULT_DOMAIN_ID), domains[0])
        medium_codes = normalize_mediums(entry.get("medium"), medium_labels)
        page_stats = analyze_handbook_pages(folder)
        page_count = int(page_stats["totalPages"])
        href = str(entry.get("href") or f"doc/{folder}/index.html")
        tags = [str(tag) for tag in (entry.get("tags") or [])]
        chips = entry.get("chips") or unique([
            *(medium_labels.get(code, DEFAULT_MEDIUM_LABEL) for code in medium_codes),
            *tags,
        ])
        scale = infer_scale(entry, page_stats)
        structure = infer_structure(entry, page_stats)
        start_here = infer_start_here(entry, page_stats)
        summary = str(entry.get("summary") or "进入该作品手册总览。")
        subtitle = str(entry.get("subtitle") or "知识手册")
        cta = str(entry.get("cta") or f"进入《{title}》手册")
        explicit_order = entry.get("order")
        auto_order = domain_order.get(primary_domain, len(domain_order)) * 1000 + index
        sort_order = explicit_order if explicit_order is not None else auto_order
        works.append(
            {
                "folder": folder,
                "title": title,
                "sub": subtitle,
                "summary": summary,
                "domain": primary_domain,
                "domains": domains,
                "domainLabel": entry.get("domainLabel") or domain_labels.get(primary_domain, DEFAULT_DOMAIN_LABEL),
                "medium": medium_codes,
                "chips": chips,
                "meta": [
                    {"term": "规模", "value": scale},
                    {"term": "结构亮点", "value": structure},
                    {"term": "从这里开始", "value": start_here},
                ],
                "href": href,
                "cta": cta,
                "pageCount": page_count,
                "pageStats": page_stats,
                "order": sort_order,
            }
        )

    return sorted(works, key=lambda item: (item["order"], item["title"]))


def build_filters(data: dict[str, object], works: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    domain_labels, medium_labels, _ = build_label_maps(data)
    filters = deepcopy(data["filters"])

    used_domains = {domain for work in works for domain in work["domains"] if domain != "all"}
    known_domain_values = {item["value"] for item in filters["domain"]}
    for value in sorted(used_domains - known_domain_values):
        filters["domain"].append({"label": domain_labels.get(value, DEFAULT_DOMAIN_LABEL), "value": value})

    used_mediums = {medium for work in works for medium in work["medium"] if medium != "all"}
    known_medium_values = {item["value"] for item in filters["medium"]}
    for value in sorted(used_mediums - known_medium_values):
        filters["medium"].append({"label": medium_labels.get(value, DEFAULT_MEDIUM_LABEL), "value": value})

    return filters


def build_domains(data: dict[str, object], works: list[dict[str, object]]) -> list[dict[str, object]]:
    rendered_domains: list[dict[str, object]] = []
    for domain in data["domains"]:
        domain_works = [work for work in works if domain["id"] in work["domains"]]
        entries = [{"label": f"从《{work['title']}》进入", "href": work["href"]} for work in domain_works]
        page_total = sum(work["pageCount"] for work in domain_works)
        count_text = f"{len(entries)} 部作品"
        if page_total:
            count_text += f" · {page_total} 个页面"
        if domain.get("countHint"):
            count_text += f" · {domain['countHint']}"
        rendered = dict(domain)
        rendered["count"] = count_text
        rendered["entries"] = entries
        rendered_domains.append(rendered)

    uncategorized_works = [work for work in works if DEFAULT_DOMAIN_ID in work["domains"]]
    if uncategorized_works:
        page_total = sum(work["pageCount"] for work in uncategorized_works)
        rendered_domains.append(
            {
                "id": DEFAULT_DOMAIN_ID,
                "theme": "misc",
                "code": "DOMAIN 00",
                "title": DEFAULT_DOMAIN_LABEL,
                "summary": "当新手册尚未补充完整领域信息时，会先在这里兜底展示，以保证它仍能进入首页系统。",
                "keywords": ["待补充", "未归类", "低成本接入"],
                "count": f"{len(uncategorized_works)} 部作品 · {page_total} 个页面 · 等待补充领域信息",
                "entries": [{"label": f"从《{work['title']}》进入", "href": work["href"]} for work in uncategorized_works],
            }
        )

    return rendered_domains


def build_project_metrics(works: list[dict[str, object]], domains: list[dict[str, object]]) -> dict[str, object]:
    domain_counts = {domain["id"]: 0 for domain in domains}
    domain_page_counts = {domain["id"]: 0 for domain in domains}
    medium_counts: dict[str, int] = {}
    total_content_like = 0
    total_support = 0
    uncategorized = 0
    fallback_medium = 0
    handbook_summaries = []

    for work in works:
        page_stats = work["pageStats"]
        for domain in work["domains"]:
            if domain in domain_counts:
                domain_counts[domain] += 1
                domain_page_counts[domain] += work["pageCount"]
        if DEFAULT_DOMAIN_ID in work["domains"]:
            uncategorized += 1
        if DEFAULT_MEDIUM_ID in work["medium"]:
            fallback_medium += 1
        for medium in work["medium"]:
            medium_counts[medium] = medium_counts.get(medium, 0) + 1
        total_content_like += int(page_stats["contentLikePages"])
        total_support += int(page_stats["supportPages"])
        handbook_summaries.append(
            {
                "folder": work["folder"],
                "title": work["title"],
                "domain": work["domain"],
                "domains": work["domains"],
                "medium": work["medium"],
                "pageCount": work["pageCount"],
                "contentLikePages": int(page_stats["contentLikePages"]),
                "supportPages": int(page_stats["supportPages"]),
            }
        )

    return {
        "totalHandbooks": len(works),
        "totalPages": sum(work.get("pageCount", 0) for work in works),
        "totalDomains": len(domains),
        "totalContentLikePages": total_content_like,
        "totalSupportPages": total_support,
        "uncategorizedHandbooks": uncategorized,
        "fallbackMediumHandbooks": fallback_medium,
        "domainCounts": domain_counts,
        "domainPageCounts": domain_page_counts,
        "mediumCounts": medium_counts,
        "registeredFolders": [work["folder"] for work in works],
        "handbooks": handbook_summaries,
    }


def sync_hero_stats(site: dict[str, object], metrics: dict[str, object]) -> dict[str, object]:
    hero = deepcopy(site["hero"])
    auto_values = {
        "AUTO_WORKS": str(metrics["totalHandbooks"]),
        "AUTO_PAGES": str(metrics["totalPages"]),
        "AUTO_DOMAINS": str(metrics["totalDomains"]),
        "AUTO_CONTENT_PAGES": str(metrics["totalContentLikePages"]),
        "AUTO_SUPPORT_PAGES": str(metrics["totalSupportPages"]),
    }
    for item in hero.get("stats", []):
        value = str(item.get("value", ""))
        if value in auto_values:
            item["value"] = auto_values[value]
    site = dict(site)
    site["hero"] = hero
    return site


def build_runtime_data() -> tuple[dict[str, object], list[dict[str, object]], dict[str, list[dict[str, object]]], list[dict[str, object]], dict[str, object]]:
    data = load_json(DATA_PATH)
    registry = load_json(HANDBOOKS_PATH)
    works = normalize_handbooks(data, registry)
    filters = build_filters(data, works)
    domains = build_domains(data, works)
    metrics = build_project_metrics(works, domains)
    return data, works, filters, domains, metrics


# ── v5 Rendering functions ──

def render_header(site: dict[str, object]) -> str:
    nav_links = render_links(site["nav"])
    return f"""<header class="atlas-header" id="top">
  <div class="atlas-shell atlas-header__inner">
    <a class="atlas-brand" href="index.html" aria-label="回到 ACG 知识手册库首页">
      <span class="atlas-brand__mark" aria-hidden="true">◎</span>
      <div class="atlas-brand__text">
        <strong>{e(site['brandTitle'])}</strong>
        <small>{e(site['brandSubtitle'])}</small>
      </div>
    </a>

    <div class="atlas-nav-wrap">
      <button class="atlas-nav-toggle" id="atlas-nav-toggle" type="button" aria-expanded="false" aria-controls="atlas-nav">菜单</button>

      <nav class="atlas-nav" id="atlas-nav" aria-label="主导航">
        {nav_links}
      </nav>
    </div>
  </div>
</header>"""


def render_hero(data: dict[str, object], works: list[dict[str, object]], metrics: dict[str, object]) -> str:
    site = data["site"]
    hero = site["hero"]
    # Domain pills
    domain_pills = [f'<button class="atlas-domain-pill is-active" data-domain="all">全部领域</button>']
    for d in data["domains"]:
        did = d["id"]
        color = HERO_THEME_COLORS.get(did, "#5c687a")
        domain_pills.append(
            f'<button class="atlas-domain-pill" data-domain="{e(did)}">'
            f'<span class="dot" style="background:{color}"></span>{e(d["title"])}</button>'
        )
    domain_bar = '\n          '.join(domain_pills)

    # Medium chips
    medium_chips = []
    for m in data["filters"]["medium"]:
        active_cls = " is-active" if m.get("active") else ""
        medium_chips.append(
            f'<button class="atlas-medium-chip{active_cls}" data-medium="{e(m["value"])}">{e(m["label"])}</button>'
        )

    total_works = metrics["totalHandbooks"]
    total_pages = metrics["totalPages"]
    total_domains = metrics["totalDomains"]
    stats_text = f"{total_works} 部 · {total_pages} 页 · {total_domains} 个领域"

    return f"""<section class="atlas-hero">
    <div class="atlas-hero-orbs" aria-hidden="true"><div class="atlas-hero-orb o1"></div><div class="atlas-hero-orb o2"></div></div>
    <div class="atlas-shell atlas-hero__grid">
      <div class="atlas-hero__copy">
        <p class="atlas-eyebrow">{e(hero['eyebrow'])}</p>
        <h1>{e(hero['title'])}</h1>
        <p class="atlas-hero__lede">ACG 作品 → 现实知识。<span class="nobr">{stats_text}</span></p>
        <p class="atlas-hero__hint">点击书脊展开摘要，或用领域标签筛选，底部媒介标签可进一步缩小范围。</p>
      </div>

      <div class="atlas-rack-area">
        <div class="atlas-domain-bar" id="atlas-domain-bar" role="group" aria-label="按领域筛选">
          {domain_bar}
        </div>

        <div class="atlas-rack-wrap">
          <div class="atlas-rack" id="atlas-rack" aria-label="档案书架"></div>
          <div class="atlas-rack-detail" id="atlas-rack-detail" aria-live="polite">
            <div>
              <div class="atlas-rack-detail__title" id="atlas-detail-title">把鼠标移到一本书脊上</div>
              <p class="atlas-rack-detail__summary" id="atlas-detail-summary">或用 Tab 键聚焦。点击领域 / 媒介标签可筛选书架。</p>
              <ul class="atlas-rack-detail__tags" id="atlas-detail-tags"></ul>
            </div>
            <a id="atlas-detail-cta" class="atlas-rack-detail__cta" href="#" style="visibility:hidden">进入手册 →</a>
          </div>
        </div>

        <div class="atlas-medium-row">
          <span class="atlas-medium-label">媒介</span>
          <div class="atlas-medium-chips" id="atlas-medium-chips" role="group" aria-label="按媒介筛选">
            {'\n            '.join(medium_chips)}
          </div>
          <span class="atlas-rack-meta" id="atlas-rack-meta">{stats_text}</span>
        </div>
      </div>
    </div>
  </section>"""


def render_works_json(works: list[dict[str, object]]) -> str:
    """Output works data as JSON for JS consumption."""
    items = []
    for w in works:
        items.append({
            "folder": w["folder"],
            "title": w["title"],
            "subtitle": w["sub"],
            "domains": w["domains"],
            "medium": w["medium"],
            "tags": w["chips"],
            "summary": w["summary"],
            "startHere": w["meta"][2]["value"] if len(w["meta"]) > 2 else "",
            "scale": w["meta"][0]["value"] if len(w["meta"]) > 0 else "",
            "structure": w["meta"][1]["value"] if len(w["meta"]) > 1 else "",
            "href": w["href"],
        })
    import json
    return json.dumps(items, ensure_ascii=False, indent=2)


def render_domain_meta_json(data: dict[str, object]) -> str:
    """Output domain metadata as JSON for JS consumption."""
    meta = {}
    for d in data["domains"]:
        did = d["id"]
        meta[did] = {
            "label": d["title"],
            "colorHex": HERO_THEME_COLORS.get(did, "#5c687a"),
            "glyph": DOMAIN_GLYPH.get(did, "◆"),
        }
    import json
    return json.dumps(meta, ensure_ascii=False, indent=2)


def render_domains_section(domains: list[dict[str, object]], section: dict[str, str]) -> str:
    cards = []
    for domain in domains:
        did = domain["id"]
        theme = domain.get("theme", "misc")
        if theme == "misc":
            theme = "space"  # fallback
        glyph = DOMAIN_GLYPH.get(did, "◆")
        cards.append(
            f"""<div class="atlas-map-card atlas-map-card--{e(theme)}" tabindex="0" role="button" data-domain-key="{e(did)}" aria-label="{e(domain['title'])}，点击筛选书架">
        <div class="atlas-map-card__top">{e(domain['count'])}</div>
        <h3>{e(domain['title'])}</h3>
        <div class="atlas-map-card__glyph">{e(glyph)}</div>
      </div>"""
        )
    return f"""<section class="atlas-section atlas-reveal" id="knowledge-map">
    <div class="atlas-shell">
      <div class="atlas-section__head">
        <div>
          <p class="atlas-section__kicker">{e(section['kicker'])}</p>
          <h2 class="atlas-section__title">{e(section['title'])}</h2>
          <p class="atlas-section__desc">{e(section['description'])}</p>
        </div>
      </div>
      <div class="atlas-map-grid" id="atlas-map-grid">
        {'\n      '.join(cards)}
      </div>
    </div>
  </section>"""


def render_works_section(data: dict[str, object], works: list[dict[str, object]], filters: dict[str, list[dict[str, object]]]) -> str:
    section = data["sections"]["worksIndex"]

    # Domain pills for works-index — compact strip style (no dot, smaller text)
    domain_pills_wi = ['<button class="atlas-wi-pill is-active" data-domain="all">全部</button>']
    for d in data["domains"]:
        did = d["id"]
        domain_pills_wi.append(
            f'<button class="atlas-wi-pill" data-domain="{e(did)}">{e(d["title"])}</button>'
        )

    # Medium chips for works-index — compact strip style; skip "all" (already added manually)
    medium_chips_wi = []
    for m in data["filters"]["medium"]:
        if m["value"] == "all":
            continue  # added manually below
        active_cls = " is-active" if m.get("active") else ""
        medium_chips_wi.append(
            f'<button class="atlas-wi-chip{active_cls}" data-medium="{e(m["value"])}">{e(m["label"])}</button>'
        )

    rows = []
    for w in works:
        colors = [HERO_THEME_COLORS.get(d, "#5c687a") for d in w["domains"]]
        if len(colors) == 1:
            stripe = colors[0]
        else:
            segments = ", ".join(f"{c} {i/len(colors)*100}% {(i+1)/len(colors)*100}%" for i, c in enumerate(colors))
            stripe = f"linear-gradient(to bottom, {segments})"
        # Build domain label string
        domain_label_list = data.get("domains", [])
        domain_labels_map = {dl["id"]: dl["title"] for dl in domain_label_list}
        domain_labels_str = " · ".join(domain_labels_map.get(d, d) for d in w["domains"])
        meta = w["meta"]
        scale = e(meta[0]["value"]) if len(meta) > 0 else ""
        structure = e(meta[1]["value"]) if len(meta) > 1 else ""
        start_here = e(meta[2]["value"]) if len(meta) > 2 else ""
        # data attributes for JS filtering
        domains_attr = ",".join(w["domains"])
        mediums_attr = ",".join(w["medium"])
        rows.append(
            f"""<div class="atlas-work-row" tabindex="0" data-domain="{e(domains_attr)}" data-medium="{e(mediums_attr)}" style="--atlas-row-accent-bg:{stripe}">
        <div>
          <div class="atlas-work-row__title">{e(w['title'])}</div>
          <div class="atlas-work-row__sub">{e(w['sub'])} · {domain_labels_str}</div>
        </div>
        <a class="atlas-work-row__link" href="{e(w['href'])}">进入 →</a>
        <p class="atlas-work-row__summary">{e(w['summary'])}</p>
        <div class="atlas-work-row__meta">从这里开始：{start_here}</div>
        <div class="atlas-work-row__extra">
          <div><strong>规模</strong>{scale}</div>
          <div><strong>结构亮点</strong>{structure}</div>
        </div>
      </div>"""
        )
    total = len(works)
    return f"""<section class="atlas-section atlas-reveal" id="works-index">
    <div class="atlas-shell">
      <div class="atlas-section__head">
        <div>
          <p class="atlas-section__kicker">{e(section['kicker'])}</p>
          <h2 class="atlas-section__title">{e(section['title'])}</h2>
          <p class="atlas-section__desc">{e(section['description'])}</p>
        </div>
      </div>
      <div class="atlas-works-filters" id="atlas-works-index-filters">
        <div class="atlas-wi-strip">
          <div class="atlas-wi-group" role="group" aria-label="按领域筛选">
            <span class="atlas-wi-label">领域</span>
            {' '.join(domain_pills_wi)}
          </div>
          <div class="atlas-wi-group" role="group" aria-label="按媒介筛选">
            <span class="atlas-wi-label">媒介</span>
            <button class="atlas-wi-chip is-active" data-medium="all">全部</button> {' '.join(medium_chips_wi)}
          </div>
          <span class="atlas-works-meta">{total} 部</span>
        </div>
      </div>
      <div class="atlas-works-list" id="atlas-works-list">
        {'\n      '.join(rows)}
      </div>
    </div>
  </section>"""


def render_paths_section(data: dict[str, object]) -> str:
    section = data["sections"]["readingPaths"]
    chips = "\n".join(f'<li>{e(chip)}</li>' for chip in section["chips"])
    path_cards = []
    # Use the reordered paths from homepage-data.json (order already updated manually)
    for idx, path in enumerate(data["paths"]):
        num = str(idx + 1).zfill(2)
        path_cards.append(
            f"""<div class="atlas-path-card">
        <div class="atlas-path-card__num">{num}</div>
        <div><h3>{e(path['title'])}</h3><p>{e(path['summary'])}</p></div>
      </div>"""
        )
    return f"""<section class="atlas-section atlas-reveal" id="reading-paths">
    <div class="atlas-shell">
      <div class="atlas-section__head">
        <div>
          <p class="atlas-section__kicker">{e(section['kicker'])}</p>
          <h2 class="atlas-section__title">{e(section['title'])}</h2>
        </div>
      </div>
      <div class="atlas-paths-grid">
        {'\n      '.join(path_cards)}
      </div>
    </div>
  </section>"""


def render_methodology(data: dict[str, object]) -> str:
    section = data["sections"]["methodology"]
    # Flow steps
    flow_items = []
    for item in data["methodology"]["flow"]:
        flow_items.append(
            f"""<li>
        <div class="atlas-m-num">{e(item['step'])}</div>
        <div class="atlas-m-body"><h4>{e(item['title'])}</h4><p>{e(item['text'])}</p></div>
      </li>"""
        )
    # Variants (5 cards)
    variants = []
    for item in data["methodology"]["variants"]:
        variants.append(
            f"""<div class="atlas-method-variant">
        <h5>{e(item['title'])}</h5>
        <p>{e(item['text'])}</p>
      </div>"""
        )
    return f"""<section class="atlas-section atlas-reveal" id="methodology">
    <div class="atlas-shell">
      <div class="atlas-section__head">
        <div>
          <p class="atlas-section__kicker">{e(section['kicker'])}</p>
          <h2 class="atlas-section__title">{e(section['title'])}</h2>
          <p class="atlas-section__desc">{e(section['description'])}</p>
        </div>
      </div>
      <ol class="atlas-method-flow">
        {'\n      '.join(flow_items)}
      </ol>
      <div class="atlas-method-variants">
        {'\n      '.join(variants)}
      </div>
    </div>
  </section>"""


def render_footer(site: dict[str, object]) -> str:
    lines = "\n    ".join(f'<p>{e(line)}</p>' for line in site["footer"])
    return f"""<footer class="atlas-footer">
  <div class="atlas-shell">
    {lines}
  </div>
</footer>"""


def build_html(data: dict[str, object], works: list[dict[str, object]], domains: list[dict[str, object]], filters: dict[str, list[dict[str, object]]], metrics: dict[str, object]) -> str:
    site = data["site"]
    works_json = render_works_json(works)
    domain_meta_json = render_domain_meta_json(data)

    return f"""<!DOCTYPE html>
<html lang="{e(site['lang'])}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(site['title'])}</title>
  <meta name="description" content="{e(site['description'])}">
  <link rel="stylesheet" href="_shared/homepage.css">
</head>
<body>
  <!-- Generated from _data/homepage-data.json + _data/handbooks.json by scripts/project_tools.py. -->
  <div class="atlas-scroll-progress" id="atlas-scroll-progress" aria-hidden="true"></div>
  <a class="atlas-skip-link" href="#main-content">跳到正文</a>

  {render_header(site)}

  <main id="main-content">
    {render_hero(data, works, metrics)}
    {render_domains_section(domains, data['sections']['knowledgeMap'])}
    {render_works_section(data, works, filters)}
    {render_paths_section(data)}
    {render_methodology(data)}
  </main>

  {render_footer(site)}

  <script id="atlas-works-data" type="application/json">
{works_json}
  </script>
  <script id="atlas-domain-meta" type="application/json">
{domain_meta_json}
  </script>
  <script src="_shared/homepage.js"></script>
</body>
</html>"""


def write_metrics(metrics: dict[str, object]) -> None:
    save_json(METRICS_PATH, metrics)


def cmd_generate() -> int:
    data, works, filters, domains, metrics = build_runtime_data()
    html = build_html(data, works, domains, filters, metrics)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    write_metrics(metrics)
    print(
        f"Generated {OUTPUT_PATH.relative_to(ROOT)} from "
        f"{DATA_PATH.relative_to(ROOT)} + {HANDBOOKS_PATH.relative_to(ROOT)}"
    )
    print(
        f"Metrics: {metrics['totalHandbooks']} handbooks / "
        f"{metrics['totalPages']} pages / {metrics['totalDomains']} domains"
    )
    return 0