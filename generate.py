# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "markdown-it-py==4.2.0",
# ]
# ///
"""Static site generator.

Reads markdown from `input/` and renders the terminal-styled site (home page,
writing index, and post pages) into `build/`. Styling and theming mirror the
design from the `nwvolxmw` revision; syntax highlighting is done client-side by
Prism, so the markdown renderer only needs to emit `language-*` code blocks.
"""
import re
import shutil
from pathlib import Path

from markdown_it import MarkdownIt

# --- Configuration ---
INPUT_DIR = Path("input")
POSTS_DIR = INPUT_DIR / "posts"
OUTPUT_DIR = Path("build")

SITE_DESCRIPTION = "Vedat's personal website"

# Inline init runs before paint to avoid a flash of the wrong theme. Defaults to
# light unless the visitor explicitly chose dark or prefers a dark color scheme.
THEME_INIT = (
    "<script>const t=localStorage.getItem('theme');"
    "if(t!=='dark'&&!(t===null&&matchMedia('(prefers-color-scheme:dark)').matches))"
    "document.documentElement.classList.add('light')</script>"
)

# --- Markdown Renderer ---
# `html: True` passes through inline HTML; default `langPrefix` of "language-"
# produces the `<code class="language-xxx">` markup Prism expects.
md = MarkdownIt("commonmark", {"breaks": True, "html": True})


# --- Templates ---
INDEX_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>vedat</title>
  <meta name="description" content="{SITE_DESCRIPTION}">
  <meta property="og:title" content="vedat">
  <meta property="og:description" content="{SITE_DESCRIPTION}">
  <meta property="og:type" content="website">
  <link rel="icon" href="favicon.svg">
  {THEME_INIT}
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <header>
      <div class="prompt">~/vedat</div>
      <button class="toggle" onclick="toggleTheme()"></button>
    </header>

    <h1>software engineer</h1>

    <p>I like thinking through hard problems. It also pays the bills.</p>

    <nav>
      <a href="writing.html">writing</a>
    </nav>

    <div class="links">
      <a href="https://github.com/badayvedat" target="_blank">github</a>
      <a href="https://linkedin.com/in/badayvedat" target="_blank">linkedin</a>
      <a href="https://twitter.com/shizoidcat" target="_blank">twitter</a>
    </div>
  </main>

  <script src="theme.js"></script>
</body>
</html>
"""


def writing_template(items):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{SITE_DESCRIPTION}">
  <meta property="og:title" content="writing / vedat">
  <meta property="og:description" content="{SITE_DESCRIPTION}">
  <meta property="og:type" content="website">
  <title>writing / vedat</title>
  <link rel="icon" href="favicon.svg">
  {THEME_INIT}
  <link rel="stylesheet" href="style.css">
</head>
<body class="page">
  <main>
    <header>
      <div class="prompt"><a href="index.html">~/vedat</a>/writing</div>
      <button class="toggle" onclick="toggleTheme()"></button>
    </header>
    <ul class="post-list">{items}
    </ul>
  </main>
  <script src="theme.js"></script>
</body>
</html>
"""


def post_template(slug, title, date, content):
    page_title = f"{title} / vedat"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{SITE_DESCRIPTION}">
  <meta property="og:title" content="{page_title}">
  <meta property="og:description" content="{SITE_DESCRIPTION}">
  <meta property="og:type" content="article">
  <title>{page_title}</title>
  <link rel="icon" href="../favicon.svg">
  {THEME_INIT}
  <link rel="stylesheet" href="../style.css">
  <link rel="stylesheet" href="../prism.css">
</head>
<body class="page">
  <main>
    <header>
      <div class="prompt"><a href="../index.html">~/vedat</a>/<a href="../writing.html">writing</a>/{slug}</div>
      <button class="toggle" onclick="toggleTheme()"></button>
    </header>
    <span class="date">{date}</span>
    <article>{content}</article>
  </main>
  <script src="../theme.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-javascript.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-typescript.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-bash.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-json.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-css.min.js"></script>
</body>
</html>
"""


# --- Static assets (shared CSS / theme script / favicon / Prism theme) ---
STYLE_CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #0a0a0a;
  --text: #e0e0e0;
  --dim: #606060;
  --accent: #00aa66;
  --border: #1a1a1a;
  --code-bg: #151515;
}

:root.light {
  --bg: #f4f1eb;
  --text: #1a1a1a;
  --dim: #737373;
  --accent: #16803c;
  --border: #d8d4cc;
  --code-bg: #e8e4dd;
}

body {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  background: var(--bg);
  color: var(--text);
  font-size: 15px;
  line-height: 1.6;
  min-height: 100vh;
  padding: 3rem 2rem;
  transition: background 0.3s, color 0.3s;
}

main { max-width: 80ch; width: 100%; margin: 0 auto; }

header {
  position: sticky;
  top: 0;
  background: var(--bg);
  z-index: 1;
  transition: background 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.prompt { color: var(--accent); }
.prompt a { color: var(--dim); text-decoration: none; }
.prompt a:hover { color: var(--text); }

.toggle {
  background: none;
  border: 1px solid var(--dim);
  color: var(--dim);
  padding: 0.25rem 0.5rem;
  font-family: inherit;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle::after { content: 'light'; }
:root.light .toggle::after { content: 'dark'; }

.toggle:hover {
  border-color: var(--text);
  color: var(--text);
}

h1 {
  font-size: 1rem;
  font-weight: normal;
  margin-bottom: 1.5rem;
}

h1 span { color: var(--dim); }

p { color: var(--dim); margin-bottom: 2rem; }

nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

nav a {
  color: var(--text);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

nav a:hover { color: var(--accent); }
nav a::before { content: '\\2192'; color: var(--dim); }
nav a:hover::before { color: var(--accent); }

.links {
  display: flex;
  gap: 1.5rem;
  font-size: 0.85rem;
}

.links a { color: var(--dim); text-decoration: none; }
.links a:hover { color: var(--accent); }

/* Post list */
.post-list { list-style: none; margin-top: 2rem; }

.post-list li {
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
}

.post-list a { color: var(--text); text-decoration: none; }
.post-list a:hover { color: var(--accent); }

.date {
  color: var(--dim);
  font-size: 0.85rem;
  white-space: nowrap;
}

/* Projects */
.projects { margin-top: 2rem; }

.project {
  padding: 1rem 0;
  border-bottom: 1px solid var(--border);
}

.project h2 {
  font-size: 1rem;
  font-weight: normal;
  margin-bottom: 0.25rem;
}

.project h2 a { color: var(--text); text-decoration: none; }
.project h2 a:hover { color: var(--accent); }
.project p { color: var(--dim); font-size: 0.9rem; margin-bottom: 0; }

/* Article */
article { margin-top: 1.5rem; }

article h1, article h2, article h3 {
  font-weight: normal;
  margin: 2rem 0 1rem;
}

article h1 { font-size: 1.4rem; }
article h2 { font-size: 1.15rem; color: var(--accent); }
article h3 { font-size: 1rem; }

article p { margin-bottom: 1.25rem; color: var(--text); }
article a { color: var(--accent); }

article ul, article ol {
  margin-bottom: 1.25rem;
  padding-left: 1.5rem;
}

article li { margin-bottom: 0.5rem; }

article code {
  font-family: inherit;
  background: var(--code-bg);
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  font-size: 0.9em;
}

article pre {
  background: var(--code-bg);
  padding: 1rem;
  overflow-x: auto;
  margin-bottom: 1.25rem;
  border-radius: 3px;
}

article pre code { background: none; padding: 0; }

article blockquote {
  border-left: 2px solid var(--accent);
  padding-left: 1rem;
  color: var(--dim);
  margin-bottom: 1.25rem;
}
"""

THEME_JS = """const root = document.documentElement;

function setTheme(theme) {
  if (theme === 'light') {
    root.classList.add('light');
  } else {
    root.classList.remove('light');
  }
  localStorage.setItem('theme', theme);
}

function toggleTheme() {
  const isLight = root.classList.contains('light');
  setTheme(isLight ? 'dark' : 'light');
}

const saved = localStorage.getItem('theme');
if (saved) {
  setTheme(saved);
} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
  setTheme('dark');
} else {
  setTheme('light');
}
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <text y=".9em" font-size="90" font-family="monospace" fill="#00aa66">>_</text>
</svg>
"""

PRISM_CSS = """.token.comment, .token.prolog, .token.doctype, .token.cdata { color: var(--dim); }
.token.punctuation { color: var(--text); }
.token.property, .token.tag, .token.boolean, .token.number, .token.constant, .token.symbol { color: #e89a4e; }
:root.light .token.property, :root.light .token.tag, :root.light .token.boolean, :root.light .token.number, :root.light .token.constant, :root.light .token.symbol { color: #b65a00; }
.token.selector, .token.attr-name, .token.string, .token.char, .token.builtin { color: var(--accent); }
.token.operator, .token.entity, .token.url { color: var(--text); }
.token.atrule, .token.attr-value, .token.keyword { color: #c792ea; }
:root.light .token.atrule, :root.light .token.attr-value, :root.light .token.keyword { color: #7c4dff; }
.token.function, .token.class-name { color: #82aaff; }
:root.light .token.function, :root.light .token.class-name { color: #2962ff; }
.token.regex, .token.important, .token.variable { color: #f78c6c; }
"""


# --- Post parsing ---
def parse_post(raw):
    """Return (title, date, markdown_body).

    Supports YAML-ish frontmatter (`--- title: ... date: ... ---`) and the
    plain format used by existing posts: first non-empty line is the title,
    the following line is the date, and the rest is the body.
    """
    fm = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if fm:
        meta = {}
        for line in fm.group(1).splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        return meta.get("title", ""), meta.get("date", ""), fm.group(2)

    lines = raw.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    title = lines[i].strip() if i < len(lines) else ""
    date = lines[i + 1].strip() if i + 1 < len(lines) else ""
    body = "\n".join(lines[i + 2:])
    return title, date, body


# --- Build ---
def build():
    print("Starting static site generation...")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    (OUTPUT_DIR / "posts").mkdir(parents=True, exist_ok=True)

    # Posts
    posts = []
    md_files = sorted(POSTS_DIR.glob("*.md")) if POSTS_DIR.exists() else []
    for md_file in md_files:
        slug = md_file.stem
        title, date, body = parse_post(md_file.read_text(encoding="utf-8"))
        html = md.render(body)

        (OUTPUT_DIR / "posts" / f"{slug}.html").write_text(
            post_template(slug, title, date, html), encoding="utf-8"
        )
        posts.append({"slug": slug, "title": title, "date": date})
        print(f"Built: posts/{slug}.html")

    # Newest first by date string (ISO dates sort naturally; others fall back
    # to lexical order, which is good enough for the current set).
    posts.sort(key=lambda p: p["date"], reverse=True)

    items = "".join(
        f'\n      <li>\n'
        f'        <a href="posts/{p["slug"]}.html">{p["title"]}</a>\n'
        f'        <span class="date">{p["date"]}</span>\n'
        f"      </li>"
        for p in posts
    )
    (OUTPUT_DIR / "writing.html").write_text(writing_template(items), encoding="utf-8")
    print("Built: writing.html")

    # Home page
    (OUTPUT_DIR / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    print("Built: index.html")

    # Static assets
    (OUTPUT_DIR / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (OUTPUT_DIR / "theme.js").write_text(THEME_JS, encoding="utf-8")
    (OUTPUT_DIR / "prism.css").write_text(PRISM_CSS, encoding="utf-8")
    (OUTPUT_DIR / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    print("Built: style.css, theme.js, prism.css, favicon.svg")

    # CNAME for the GitHub Pages custom domain
    cname = Path("CNAME")
    if cname.exists():
        shutil.copy2(cname, OUTPUT_DIR / "CNAME")
        print("Copied: CNAME")

    print(f"\nDone! Output in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    build()
