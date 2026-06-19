// Build-time syntax highlighting for generate.py.
//
// Reads a JSON array of {code, lang} from stdin and writes a JSON array of
// highlighted HTML strings to stdout. Uses Shiki (VS Code's TextMate engine)
// with the real One Dark Pro / One Light themes, emitted as a dual theme:
// the dark theme is the inline default and the light theme rides along in
// `--shiki-light` CSS variables, which code.css activates under `:root.light`.
import { codeToHtml } from "shiki";

const THEMES = { light: "one-light", dark: "one-dark-pro" };

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8");
}

async function render(code, lang) {
  const opts = { themes: THEMES, defaultColor: "dark" };
  try {
    return await codeToHtml(code, { lang: lang || "text", ...opts });
  } catch {
    // Unknown / unsupported language → render as plain text on the same surface.
    return await codeToHtml(code, { lang: "text", ...opts });
  }
}

const blocks = JSON.parse(await readStdin());
const out = [];
for (const b of blocks) out.push(await render(b.code, b.lang));
process.stdout.write(JSON.stringify(out));
