# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "markdown-it-py==4.2.0",
# ]
# ///
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape as esc
from pathlib import Path

from markdown_it import MarkdownIt

# --- Configuration ---
POSTS_DIR = Path("posts")
OUTPUT_DIR = Path("build")

SITE_URL = "https://vedat.me"
SITE_NAME = "Vedat Baday"
SITE_DESCRIPTION = "Software engineer."
SITE_TAGLINE = ""  # optional subtitle under the name on the home page
JOB_TITLE = "Software engineer"

SOCIAL_LINKS = [
    ("github", "https://github.com/badayvedat"),
    ("linkedin", "https://linkedin.com/in/badayvedat"),
    ("twitter", "https://twitter.com/shizoidcat"),
]

# Three themes: dim (default), dark, light — driven by a class on <html>
# (none = dim). This inline init applies the saved/system choice before paint:
# a saved 'dark'/'light' wins; otherwise a light system preference picks light;
# everyone else gets the dim default.
THEME_INIT = (
    "<script>const t=localStorage.getItem('theme');"
    "if(t==='dark'||t==='light')document.documentElement.classList.add(t);"
    "else if(!t&&matchMedia('(prefers-color-scheme:light)').matches)"
    "document.documentElement.classList.add('light')</script>"
)

# Light-mode activation for Shiki's dual-theme output. The dark theme is the
# inline default; the light theme rides along in `--shiki-light(-bg)` vars.
CODE_CSS = """:root.light .shiki,
:root.light .shiki span {
  color: var(--shiki-light) !important;
  background-color: var(--shiki-light-bg) !important;
}
"""


def abs_url(path):
    return SITE_URL.rstrip("/") + "/" + path.lstrip("/")


OG_IMAGE = abs_url("og.svg")
FEED_URL = abs_url("feed.xml")

# --- Markdown Renderer ---
# Code fences are highlighted out-of-band by Shiki: during render the fence
# callback stashes (lang, code) and drops a placeholder; after all posts render
# we hand every block to highlight.mjs in one Node call, then swap the highlighted
# HTML back in (see build()).
_CODE_BLOCKS = []
_SHIKI_RE = re.compile(r'<pre data-shiki="(\d+)"></pre>')


def _collect_code(code, lang, attrs):
    idx = len(_CODE_BLOCKS)
    _CODE_BLOCKS.append({"code": code, "lang": (lang or "").strip()})
    return f'<pre data-shiki="{idx}"></pre>'


def shiki_render(blocks):
    if not blocks:
        return []
    proc = subprocess.run(
        ["node", "highlight.mjs"],
        input=json.dumps(blocks),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def apply_highlight(html, rendered):
    return _SHIKI_RE.sub(lambda m: rendered[int(m.group(1))], html)


md = MarkdownIt(
    "commonmark", {"breaks": True, "html": True, "highlight": _collect_code}
)


# --- Shared partials ---
def json_ld(data):
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(data, indent=2)
        + "\n  </script>"
    )


def head(
    *,
    doc_title,
    title,
    description,
    canonical,
    og_type,
    root,
    code=False,
    published="",
    jsonld="",
):
    code_link = f'\n  <link rel="stylesheet" href="{root}code.css">' if code else ""
    published_meta = (
        f'\n  <meta property="article:published_time" content="{published}">'
        if published
        else ""
    )
    jsonld_block = f"\n  {jsonld}" if jsonld else ""
    return f"""<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(doc_title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="{esc(SITE_NAME)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:site_name" content="{esc(SITE_NAME)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:type" content="image/svg+xml">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{esc(SITE_NAME)}">{published_meta}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <link rel="icon" href="{root}favicon.svg">
  <link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)}" href="{FEED_URL}">
  {THEME_INIT}
  <link rel="stylesheet" href="{root}style.css">{code_link}{jsonld_block}
</head>"""


def site_nav(root):
    # Inner pages get a single "home" link back to the index; the home page
    # itself has no top nav (its <h1> is the identity).
    return f"""<nav class="site nav-links">
    <a href="{root}index.html">home</a>
  </nav>"""


def theme_toggle():
    return '<button class="toggle" onclick="toggleTheme()" aria-label="Toggle theme"></button>'


def site_footer():
    links = "\n    ".join(
        f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'
        for name, url in SOCIAL_LINKS
    )
    return f"<footer>\n    {links}\n  </footer>"


def post_list(posts):
    items = []
    for p in posts:
        desc = (
            f'\n          <p class="desc">{esc(p["description"])}</p>'
            if p["description"]
            else ""
        )
        items.append(
            f"""        <li>
          <a href="posts/{p["slug"]}.html" class="post-link">
            <div class="row">
              <span class="title">{esc(p["title"])}</span>
              <time class="date" datetime="{p["date"]}">{p["display_date"]}</time>
            </div>{desc}
          </a>
        </li>"""
        )
    return "\n".join(items)


# --- Page templates ---
def index_template(posts):
    jsonld = json_ld(
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": SITE_NAME,
            "url": abs_url(""),
            "jobTitle": JOB_TITLE,
            "sameAs": [url for _, url in SOCIAL_LINKS],
        }
    )
    return f"""<!DOCTYPE html>
<html lang="en">
{
        head(
            doc_title=SITE_NAME,
            title=SITE_NAME,
            description=SITE_DESCRIPTION,
            canonical=abs_url(""),
            og_type="website",
            root="",
            jsonld=jsonld,
        )
    }
<body>
  {theme_toggle()}
  <main class="home">
    <div class="container">
      <header class="intro">
        <h1>{esc(SITE_NAME)}</h1>
        <p class="subtitle">{esc(SITE_TAGLINE)}</p>
      </header>
      <ul class="post-list home-posts">
{post_list(posts)}
      </ul>
    </div>
  </main>
  {site_footer()}
  <script src="theme.js"></script>
</body>
</html>
"""


def post_template(post, content):
    root = "../"
    title = post["title"]
    iso = post["date"]
    desc = post["meta_desc"]
    canonical = abs_url(f"posts/{post['slug']}.html")
    jsonld = json_ld(
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "datePublished": iso,
            "dateModified": iso,
            "description": desc,
            "url": canonical,
            "mainEntityOfPage": canonical,
            "author": {"@type": "Person", "name": SITE_NAME, "url": abs_url("")},
        }
    )
    return f"""<!DOCTYPE html>
<html lang="en">
{
        head(
            doc_title=f"{title} | {SITE_NAME}",
            title=title,
            description=desc,
            canonical=canonical,
            og_type="article",
            root=root,
            code=True,
            published=iso,
            jsonld=jsonld,
        )
    }
<body>
  {theme_toggle()}
  {site_nav(root)}
  <main>
    <div class="container-wide post">
      <h1>{esc(title)}</h1>
      <time class="post-date" datetime="{iso}">{post["display_date"]}</time>
      <article class="prose">{content}</article>
    </div>
  </main>
  {site_footer()}
  <script src="{root}theme.js"></script>
</body>
</html>
"""


# --- Static assets ---
STYLE_CSS = """:root {
  --bg: #16181d;        /* dim — the default theme */
  --text: #f5f5f4;      /* stone-100 */
  --muted: #a8a29e;     /* stone-400 */
  --border: #2d3038;
  --code-bg: #1d2026;
  --accent: #4db6ac;    /* teal */
  --body-size: 16px;
  --font-serif: 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, Cambria, 'Times New Roman', serif;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  color-scheme: dark;
}

:root.dark {
  --bg: #0a0a0a;        /* black */
  --border: #2a2a2a;
  --code-bg: #16181d;
  color-scheme: dark;
}

:root.light {
  --bg: #faf9f7;        /* warm near-white */
  --text: #1c1917;      /* stone-900 */
  --muted: #78716c;     /* stone-500 */
  --border: #e7e5e4;    /* stone-200 */
  --code-bg: #f1efec;   /* warm light gray */
  --accent: #0f766e;    /* darker teal for contrast on light */
  color-scheme: light;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { font-size: var(--body-size); scroll-behavior: smooth; }

body {
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text);
  font-size: 1rem;
  line-height: 1.7;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  transition: background-color 0.2s ease, color 0.2s ease;
}

/* Top navigation / wordmark */
nav.site {
  display: flex;
  justify-content: center;
  padding: 1.25rem 1rem;
}

/* Inner-page nav links */
nav.site.nav-links { gap: 1.5rem; }

.nav-links a {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--muted);
  text-decoration: none;
  transition: color 0.2s;
}

.nav-links a:hover { color: var(--accent); }

footer a {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--muted);
  text-decoration: none;
  transition: color 0.2s;
}

footer a:hover { color: var(--accent); }

.toggle {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 10;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--muted);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.4rem 0.65rem;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background-color 0.2s;
}

.toggle:hover { color: var(--accent); border-color: var(--accent); }
/* Label shows the next theme in the cycle: dark -> dim -> light -> dark.
   Base (no class) is dim, so its next is light. */
.toggle::after { content: 'light'; }
:root.dark .toggle::after { content: 'dim'; }
:root.light .toggle::after { content: 'dark'; }

main {
  flex: 1;
  width: 100%;
  padding: 1.5rem 1.25rem 4rem;
}

/* Home: vertically center the name + post list in the viewport so the page
   reads as composed rather than top-loaded with an empty lower half. */
main.home {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.container { max-width: 40rem; margin: 0 auto; }
.container-wide { max-width: 42rem; margin: 0 auto; }

/* Home intro */
.intro { text-align: center; }

.intro h1 {
  font-family: var(--font-serif);
  font-weight: 400;
  font-size: clamp(3rem, 9vw, 5rem);
  line-height: 1.05;
  margin-bottom: 1rem;
}

.intro .subtitle {
  color: var(--muted);
  font-size: 0.9rem;
}

/* Post list */
.home-posts { margin-top: 3.5rem; }
.post-list { list-style: none; }
.post-list li { padding: 0.85rem 0; border-bottom: 1px solid var(--border); }
.post-list li:last-child { border-bottom: none; }

.post-link { display: block; text-decoration: none; color: inherit; }

.post-list .row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
}

.post-list .title { color: var(--text); font-size: 1.15rem; }
.post-link:hover .title { color: var(--accent); text-decoration: underline; text-underline-offset: 3px; }

.post-list .date {
  color: var(--muted);
  font-size: 0.9rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.post-list .desc { color: var(--muted); font-size: 0.9rem; margin-top: 0.25rem; }

/* Post page */
.post h1 {
  font-family: var(--font-serif);
  font-weight: 400;
  font-size: clamp(2rem, 6vw, 3rem);
  line-height: 1.15;
  text-align: center;
  margin: 0.5rem 0 1rem;
}

.post-date {
  display: block;
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
  margin-bottom: 3rem;
}

/* Article prose */
.prose { font-size: 1.05rem; }
.prose > * + * { margin-top: 1.4rem; }

.prose h2,
.prose h3 {
  font-family: var(--font-serif);
  font-weight: 400;
  line-height: 1.2;
  margin-top: 2.5rem;
}

.prose h2 { font-size: 1.6rem; }
.prose h3 { font-size: 1.3rem; }

.prose a {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 2px;
  text-decoration-color: var(--muted);
}
.prose a:hover { text-decoration-color: var(--accent); }

.prose ul, .prose ol { padding-left: 1.4rem; }
.prose li { margin-bottom: 0.4rem; }
.prose li::marker { color: var(--muted); }

.prose img { max-width: 100%; height: auto; border-radius: 6px; }

.prose code {
  font-family: var(--font-mono);
  font-size: 0.85em;
  background: var(--code-bg);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}

.prose pre {
  font-family: var(--font-mono);
  background: var(--code-bg);
  border: 1px solid var(--border);
  padding: 1rem 1.1rem;
  border-radius: 8px;
  overflow-x: auto;
}

.prose pre code { background: none; padding: 0; font-size: 0.85rem; }

.prose blockquote {
  border-left: 2px solid var(--border);
  padding-left: 1.1rem;
  color: var(--muted);
  font-style: italic;
}

/* Footer */
footer {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  padding: 2rem 1rem 2.5rem;
}
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="20" fill="#141210"/>
  <text x="50" y="54" text-anchor="middle" dominant-baseline="central" font-family="ui-monospace, 'SF Mono', Menlo, Consolas, monospace" font-size="64" fill="#f5f5f4">V</text>
</svg>
"""

OG_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#141210"/>
  <text x="600" y="315" text-anchor="middle" dominant-baseline="central" font-family="Georgia, 'Times New Roman', serif" font-size="140" fill="#f5f5f4">Vedat</text>
</svg>
"""

THEME_JS = """const root = document.documentElement;
const THEMES = ['dark', 'dim', 'light'];

function currentTheme() {
  if (root.classList.contains('light')) return 'light';
  if (root.classList.contains('dark')) return 'dark';
  return 'dim';
}

function setTheme(theme) {
  root.classList.remove('dark', 'light');
  if (theme !== 'dim') root.classList.add(theme);
  localStorage.setItem('theme', theme);
}

function toggleTheme() {
  const next = THEMES[(THEMES.indexOf(currentTheme()) + 1) % THEMES.length];
  setTheme(next);
}
"""


# --- Post parsing ---
def parse_post(raw):
    """Return (title, date, description, markdown_body)."""
    fm = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if fm:
        meta = {}
        for line in fm.group(1).splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        return (
            meta.get("title", ""),
            meta.get("date", ""),
            meta.get("description", ""),
            fm.group(2),
        )

    lines = raw.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    title = lines[i].strip() if i < len(lines) else ""
    date = lines[i + 1].strip() if i + 1 < len(lines) else ""
    body = "\n".join(lines[i + 2 :])
    return title, date, "", body


def format_date(date):
    """Render an ISO date (YYYY-MM-DD) as e.g. "May 9, 2026"; pass others through."""
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        return f"{dt:%b} {dt.day}, {dt.year}"
    except ValueError:
        return date


def excerpt(markdown_body, limit=155):
    """A plain-text summary of a post body, for meta descriptions / the feed."""
    text = re.sub(r"```.*?```", " ", markdown_body, flags=re.S)  # code fences
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)  # images
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links -> text
    text = re.sub(r"<[^>]+>", " ", text)  # inline html
    text = re.sub(r"[#*_`>]", "", text)  # markdown punctuation
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


def rfc822(iso):
    try:
        dt = datetime.strptime(iso, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        dt = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return format_datetime(dt)


# --- Feeds / crawler files ---
def sitemap_xml(posts):
    urls = [f"  <url><loc>{abs_url('')}</loc></url>"]
    for p in posts:
        loc = abs_url(f"posts/{p['slug']}.html")
        lastmod = f"<lastmod>{p['date']}</lastmod>" if p["date"] else ""
        urls.append(f"  <url><loc>{loc}</loc>{lastmod}</url>")
    body = "\n".join(urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n"
    )


def robots_txt():
    return f"User-agent: *\nAllow: /\n\nSitemap: {abs_url('sitemap.xml')}\n"


def feed_xml(posts):
    items = []
    for p in posts:
        url = abs_url(f"posts/{p['slug']}.html")
        items.append(
            f"""    <item>
      <title>{esc(p["title"])}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{rfc822(p["date"])}</pubDate>
      <description>{esc(p["meta_desc"])}</description>
    </item>"""
        )
    last_build = rfc822(posts[0]["date"]) if posts else rfc822("")
    body = "\n".join(items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{esc(SITE_NAME)}</title>
    <link>{abs_url("")}</link>
    <description>{esc(SITE_DESCRIPTION)}</description>
    <language>en</language>
    <lastBuildDate>{last_build}</lastBuildDate>
    <atom:link href="{FEED_URL}" rel="self" type="application/rss+xml"/>
{body}
  </channel>
</rss>
"""


# --- Build ---
def build():
    print("Starting static site generation...")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    (OUTPUT_DIR / "posts").mkdir(parents=True, exist_ok=True)

    _CODE_BLOCKS.clear()
    posts = []
    md_files = sorted(POSTS_DIR.glob("*.md")) if POSTS_DIR.exists() else []
    for md_file in md_files:
        title, date, description, body = parse_post(md_file.read_text(encoding="utf-8"))
        post = {
            "slug": md_file.stem,
            "title": title,
            "date": date,
            "display_date": format_date(date),
            "description": description,
            "meta_desc": description or excerpt(body) or SITE_DESCRIPTION,
            # rendered with `<pre data-shiki="N">` placeholders for now
            "body_html": md.render(body),
        }
        posts.append(post)

    # One Node/Shiki call for every code block across all posts, then swap the
    # highlighted HTML back into each post and write it out.
    highlighted = shiki_render(_CODE_BLOCKS)
    for post in posts:
        html = apply_highlight(post.pop("body_html"), highlighted)
        (OUTPUT_DIR / "posts" / f"{post['slug']}.html").write_text(
            post_template(post, html), encoding="utf-8"
        )
        print(f"Built: posts/{post['slug']}.html")

    posts.sort(key=lambda p: p["date"], reverse=True)

    (OUTPUT_DIR / "index.html").write_text(index_template(posts), encoding="utf-8")
    (OUTPUT_DIR / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (OUTPUT_DIR / "code.css").write_text(CODE_CSS, encoding="utf-8")
    (OUTPUT_DIR / "theme.js").write_text(THEME_JS, encoding="utf-8")
    (OUTPUT_DIR / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    (OUTPUT_DIR / "og.svg").write_text(OG_SVG, encoding="utf-8")
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap_xml(posts), encoding="utf-8")
    (OUTPUT_DIR / "robots.txt").write_text(robots_txt(), encoding="utf-8")
    (OUTPUT_DIR / "feed.xml").write_text(feed_xml(posts), encoding="utf-8")
    print("Built: index.html, style.css, code.css, theme.js, favicon.svg, og.svg")
    print("Built: sitemap.xml, robots.txt, feed.xml")

    cname = Path("CNAME")
    if cname.exists():
        shutil.copy2(cname, OUTPUT_DIR / "CNAME")
        print("Copied: CNAME")

    print(f"\nDone! Output in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    build()
