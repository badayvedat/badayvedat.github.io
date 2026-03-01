const fs = require('fs');
const path = require('path');
const { marked } = require('marked');

const DIST = 'dist';
const POSTS_DIR = 'posts';

// Common meta tags
const SITE_DESCRIPTION = "Vedat's personal website";
const FAVICON = `<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90' font-family='monospace' fill='%2300aa66'>>_</text></svg>">`;
const THEME_INIT = `<script>const t=localStorage.getItem('theme');if(t!=='dark'&&!(t===null&&matchMedia('(prefers-color-scheme:dark)').matches))document.documentElement.classList.add('light')</script>`;

// Clean and create dist
if (fs.existsSync(DIST)) {
  fs.rmSync(DIST, { recursive: true });
}
fs.mkdirSync(DIST);
fs.mkdirSync(path.join(DIST, 'posts'));

// Parse frontmatter
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { meta: {}, content };

  const meta = {};
  match[1].split('\n').forEach(line => {
    const [key, ...val] = line.split(':');
    if (key && val.length) meta[key.trim()] = val.join(':').trim();
  });

  return { meta, content: match[2] };
}

// Post template
function postTemplate(slug, title, date, content) {
  const pageTitle = `${title} / vedat`;
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="${SITE_DESCRIPTION}">
  <meta property="og:title" content="${pageTitle}">
  <meta property="og:description" content="${SITE_DESCRIPTION}">
  <meta property="og:type" content="article">
  <title>${pageTitle}</title>
  <link rel="icon" href="../favicon.svg">
  ${THEME_INIT}
  <link rel="stylesheet" href="../style.css">
  <link rel="stylesheet" href="../prism.css">
</head>
<body class="page">
  <main>
    <header>
      <div class="prompt"><a href="../index.html">~/vedat</a>/<a href="../writing.html">writing</a>/${slug}</div>
      <button class="toggle" onclick="toggleTheme()"></button>
    </header>
    <span class="date">${date}</span>
    <article>${content}</article>
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
</html>`;
}

// Build posts and collect metadata
const posts = [];
const mdFiles = fs.existsSync(POSTS_DIR)
  ? fs.readdirSync(POSTS_DIR).filter(f => f.endsWith('.md'))
  : [];

mdFiles.forEach(file => {
  const slug = file.replace('.md', '');
  const raw = fs.readFileSync(path.join(POSTS_DIR, file), 'utf-8');
  const { meta, content } = parseFrontmatter(raw);

  const title = meta.title || slug;
  const date = meta.date || '';
  const html = marked(content);

  posts.push({ slug, title, date });

  const output = postTemplate(slug, title, date, html);
  fs.writeFileSync(path.join(DIST, 'posts', `${slug}.html`), output);
  console.log(`Built: posts/${slug}.html`);
});

// Sort posts by date (newest first)
posts.sort((a, b) => b.date.localeCompare(a.date));

// Generate writing.html
const writingList = posts.map(p => `
      <li>
        <a href="posts/${p.slug}.html">${p.title}</a>
        <span class="date">${p.date}</span>
      </li>`).join('');

const writingHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="${SITE_DESCRIPTION}">
  <meta property="og:title" content="writing / vedat">
  <meta property="og:description" content="${SITE_DESCRIPTION}">
  <meta property="og:type" content="website">
  <title>writing / vedat</title>
  <link rel="icon" href="favicon.svg">
  ${THEME_INIT}
  <link rel="stylesheet" href="style.css">
</head>
<body class="page">
  <main>
    <header>
      <div class="prompt"><a href="index.html">~/vedat</a>/writing</div>
      <button class="toggle" onclick="toggleTheme()"></button>
    </header>
    <ul class="post-list">${writingList}
    </ul>
  </main>
  <script src="theme.js"></script>
</body>
</html>`;

fs.writeFileSync(path.join(DIST, 'writing.html'), writingHtml);
console.log('Built: writing.html');

// Copy CNAME for GitHub Pages custom domain
if (fs.existsSync('CNAME')) {
  fs.copyFileSync('CNAME', path.join(DIST, 'CNAME'));
  console.log('Copied: CNAME');
}

// Copy static pages
['index.html'].forEach(file => {
  if (fs.existsSync(file)) {
    let content = fs.readFileSync(file, 'utf-8');
    // Update paths and extract styles to external
    content = content.replace(/<style>[\s\S]*?<\/style>/, '<link rel="stylesheet" href="style.css">');
    content = content.replace(/<script>[\s\S]*?<\/script>/, '<script src="theme.js"></script>');
    fs.writeFileSync(path.join(DIST, file), content);
    console.log(`Copied: ${file}`);
  }
});

// Create shared CSS
const sharedCss = `* { margin: 0; padding: 0; box-sizing: border-box; }

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
nav a::before { content: '→'; color: var(--dim); }
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
`;

fs.writeFileSync(path.join(DIST, 'style.css'), sharedCss);
console.log('Built: style.css');

// Create theme.js
const themeJs = `const root = document.documentElement;

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
`;

fs.writeFileSync(path.join(DIST, 'theme.js'), themeJs);
console.log('Built: theme.js');

// Create favicon.svg
const faviconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <text y=".9em" font-size="90" font-family="monospace" fill="#00aa66">>_</text>
</svg>`;

fs.writeFileSync(path.join(DIST, 'favicon.svg'), faviconSvg);
console.log('Built: favicon.svg');

// Create prism.css (syntax highlighting)
const prismCss = `.token.comment, .token.prolog, .token.doctype, .token.cdata { color: var(--dim); }
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
`;

fs.writeFileSync(path.join(DIST, 'prism.css'), prismCss);
console.log('Built: prism.css');

console.log('\nDone! Serve with: npx serve dist');
