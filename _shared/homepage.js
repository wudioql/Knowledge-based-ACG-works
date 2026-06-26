(function () {
  'use strict';

  /* ==================== Works Data ==================== */
  var worksData = null;
  var scriptTag = document.getElementById('atlas-works-data');
  if (scriptTag) {
    try { worksData = JSON.parse(scriptTag.textContent); } catch (e) { worksData = []; }
  }
  if (!worksData || !worksData.length) return;

  var DOMAIN_META = {};
  var dmScript = document.getElementById('atlas-domain-meta');
  if (dmScript) {
    try { DOMAIN_META = JSON.parse(dmScript.textContent); } catch (e) { /* fallback */ }
  }

  function domainColor(key) {
    return (DOMAIN_META[key] && DOMAIN_META[key].colorHex) || '#8a94a6';
  }

  var activeDomain = 'all', activeMedium = 'all', activeFolder = null;

  /* ==================== Rack ==================== */
  var rackEl = document.getElementById('atlas-rack');
  var detailTitle = document.getElementById('atlas-detail-title');
  var detailSummary = document.getElementById('atlas-detail-summary');
  var detailTags = document.getElementById('atlas-detail-tags');
  var detailCta = document.getElementById('atlas-detail-cta');

  function workMatches(w) {
    return (activeDomain === 'all' || w.domains.indexOf(activeDomain) !== -1) &&
           (activeMedium === 'all' || w.medium.indexOf(activeMedium) !== -1);
  }

  function renderRack() {
    if (!rackEl) return;
    rackEl.innerHTML = '';
    var visible = worksData.filter(workMatches);
    visible.forEach(function (w, idx) {
      var colors = w.domains.map(domainColor);
      var stripeBg = colors.length === 1 ? colors[0]
        : 'linear-gradient(to bottom, ' + colors.map(function (c, i) {
            return c + ' ' + (i / colors.length * 100) + '% ' + ((i+1) / colors.length * 100) + '%';
          }).join(', ') + ')';
      var headBg = 'background: color-mix(in srgb, ' + colors[0] + ' 9%, #ffffff)';
      var glyphs = w.domains.map(function (d) {
        return (DOMAIN_META[d] && DOMAIN_META[d].glyph) || '◆';
      }).join('');
      var tagLabel = w.domains.map(function (d) { return d.toUpperCase(); }).join(' · ');
      var catalog = String(worksData.indexOf(w) + 1).padStart(2, '0');

      var btn = document.createElement('button');
      btn.className = 'atlas-spine';
      btn.type = 'button';
      btn.setAttribute('aria-label', w.title + ' · ' + w.subtitle);
      btn.innerHTML =
        '<span class="atlas-spine__stripe" style="background:' + stripeBg + '"></span>' +
        '<div class="atlas-spine__head" style="' + headBg + '">' +
          '<span class="atlas-spine__num">No.' + catalog + '</span>' +
          '<span class="atlas-spine__glyphs">' + glyphs.split('').map(function (g) { return '<span>' + g + '</span>'; }).join('') + '</span>' +
        '</div>' +
        '<div class="atlas-spine__body">' +
          '<div class="atlas-spine__title">' + esc(w.title) + '</div>' +
          '<div class="atlas-spine__ghost">' + esc(w.title.charAt(0)) + '</div>' +
        '</div>' +
        '<div class="atlas-spine__sub">' + esc(w.subtitle) + '</div>' +
        '<div class="atlas-spine__foot">' +
          '<div class="atlas-spine__media" aria-hidden="true">' +
            '<i class="' + (w.medium.indexOf('novel') !== -1 ? 'on' : '') + '"></i>' +
            '<i class="' + (w.medium.indexOf('manga') !== -1 ? 'on' : '') + '"></i>' +
            '<i class="' + (w.medium.indexOf('anime') !== -1 ? 'on' : '') + '"></i>' +
            '<i class="' + (w.medium.indexOf('game') !== -1 ? 'on' : '') + '"></i>' +
          '</div>' +
          '<span class="atlas-spine__tag">' + esc(tagLabel) + '</span>' +
        '</div>';
      btn.addEventListener('mouseenter', function () { showDetail(w, btn); });
      btn.addEventListener('focus', function () { showDetail(w, btn); });
      btn.addEventListener('click', function () { window.location.href = w.href; });
      rackEl.appendChild(btn);
    });

    var meta = document.getElementById('atlas-rack-meta');
    if (meta) meta.textContent = visible.length + ' / ' + worksData.length + ' 部';
    if (activeFolder && !visible.some(function (v) { return v.folder === activeFolder; })) clearDetail();
  }

  function esc(s) { return String(s).replace(/[&<>"']/g, function (m) { return ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[m]; }); }

  function showDetail(w, el) {
    var spines = document.querySelectorAll('.atlas-spine');
    Array.prototype.forEach.call(spines, function (s) { s.classList.remove('is-active'); });
    if (el) el.classList.add('is-active');
    activeFolder = w.folder;
    if (detailTitle) detailTitle.textContent = w.title + ' · ' + w.subtitle;
    if (detailSummary) detailSummary.textContent = w.summary + ' ' + (w.startHere || '');
    if (detailTags) detailTags.innerHTML = (w.tags || []).map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('');
    if (detailCta) {
      detailCta.href = w.href;
      detailCta.style.visibility = 'visible';
      detailCta.textContent = '进入《' + w.title + '》→';
    }
  }

  function clearDetail() {
    activeFolder = null;
    var spines = document.querySelectorAll('.atlas-spine');
    Array.prototype.forEach.call(spines, function (s) { s.classList.remove('is-active'); });
    if (detailTitle) detailTitle.textContent = '把鼠标移到一本书脊上';
    if (detailSummary) detailSummary.textContent = '或用 Tab 键聚焦。点击领域 / 媒介标签可筛选书架。';
    if (detailTags) detailTags.innerHTML = '';
    if (detailCta) detailCta.style.visibility = 'hidden';
  }

  /* ==================== Filters ==================== */
  var domainBar = document.getElementById('atlas-domain-bar');
  if (domainBar) {
    domainBar.addEventListener('click', function (e) {
      var btn = e.target.closest('.atlas-domain-pill');
      if (!btn) return;
      activeDomain = btn.getAttribute('data-domain');
      var pills = document.querySelectorAll('.atlas-domain-pill');
      Array.prototype.forEach.call(pills, function (b) { b.classList.toggle('is-active', b === btn); });
      renderRack(); clearDetail();
    });
  }

  var mediumChips = document.getElementById('atlas-medium-chips');
  if (mediumChips) {
    mediumChips.addEventListener('click', function (e) {
      var btn = e.target.closest('.atlas-medium-chip');
      if (!btn) return;
      activeMedium = btn.getAttribute('data-medium');
      var chips = document.querySelectorAll('.atlas-medium-chip');
      Array.prototype.forEach.call(chips, function (b) { b.classList.toggle('is-active', b === btn); });
      renderRack(); clearDetail();
    });
  }

  /* ==================== Nav Toggle ==================== */
  var navToggle = document.getElementById('atlas-nav-toggle');
  var siteNav = document.getElementById('atlas-nav');
  if (navToggle && siteNav) {
    navToggle.addEventListener('click', function () {
      var open = siteNav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
    var navLinks = siteNav.querySelectorAll('a');
    Array.prototype.forEach.call(navLinks, function (a) {
      a.addEventListener('click', function () {
        siteNav.classList.remove('is-open');
        if (navToggle) navToggle.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('click', function (event) {
      if (!siteNav.classList.contains('is-open')) return;
      if (siteNav.contains(event.target) || navToggle.contains(event.target)) return;
      siteNav.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && siteNav.classList.contains('is-open')) {
        siteNav.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ==================== Knowledge Map ==================== */
  var mapGrid = document.getElementById('atlas-map-grid');
  if (mapGrid) {
    var mapCards = mapGrid.querySelectorAll('.atlas-map-card');
    Array.prototype.forEach.call(mapCards, function (card) {
      card.addEventListener('click', function () {
        var key = card.getAttribute('data-domain-key');
        if (!key) return;
        activeDomain = key;
        var pills = document.querySelectorAll('.atlas-domain-pill');
        Array.prototype.forEach.call(pills, function (b) {
          b.classList.toggle('is-active', b.getAttribute('data-domain') === key);
        });
        renderRack(); clearDetail();
        var hero = document.querySelector('.atlas-hero');
        if (hero) hero.scrollIntoView({ behavior: 'smooth' });
      });
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          card.click();
        }
      });
    });
  }

  /* ==================== Scroll Progress ==================== */
  var scrollBar = document.getElementById('atlas-scroll-progress');
  if (scrollBar) {
    window.addEventListener('scroll', function () {
      var h = document.documentElement;
      var pct = h.scrollTop / (h.scrollHeight - h.clientHeight);
      scrollBar.style.width = (pct * 100) + '%';
    }, { passive: true });
  }

  /* ==================== Reveal ==================== */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        e.target.classList.add('is-visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });
  var reveals = document.querySelectorAll('.atlas-reveal');
  Array.prototype.forEach.call(reveals, function (el) { io.observe(el); });

  /* ==================== Init ==================== */
  renderRack();
})();
