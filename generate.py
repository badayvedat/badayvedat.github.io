import shutil
from pathlib import Path
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

# --- Configuration ---
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("build")
PYGMENTS_CSS_FILENAME = "pygments.css"
STYLE_CSS_FILENAME = "style.css"
HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <link rel="stylesheet" href="{{root_path}}/{PYGMENTS_CSS_FILENAME}">
    <link rel="stylesheet" href="{{root_path}}/{STYLE_CSS_FILENAME}">
</head>
<body>
{{body_content}}
</body>
</html>
"""

# --- Syntax Highlighting Setup ---


def highlight_code(code, lang, attrs):
    """Highlight code blocks using Pygments."""
    if not lang:
        # Try guessing the lexer if no language is provided
        try:
            lexer = guess_lexer(code)
            lang = lexer.aliases[0]  # Use the first alias as the lang name
        except ClassNotFound:
            # If guessing fails, default to plain text
            lexer = get_lexer_by_name("text")
            lang = "text"
    else:
        try:
            lexer = get_lexer_by_name(lang)
        except ClassNotFound:
            print(
                f"Warning: Pygments lexer not found for language '{lang}'. Falling back to 'text'."
            )
            lexer = get_lexer_by_name("text")  # Fallback lexer

    formatter = HtmlFormatter(cssclass="highlight", wrapcode=True)
    return highlight(code, lexer, formatter)


# --- Markdown Renderer ---
md = MarkdownIt(
    "commonmark",  # Use CommonMark spec
    {"breaks": True, "html": True, "highlight": highlight_code},
    # enable=["table"] # Optionally enable extensions like tables
)

# --- Helper Functions ---


def generate_pygments_css(output_dir, filename):
    """Generates the CSS file for Pygments highlighting."""
    formatter = HtmlFormatter(style="default", cssclass="highlight")  # Choose a style
    css_content = formatter.get_style_defs()
    css_path = output_dir / filename
    try:
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
        print(f"Generated Pygments CSS: {css_path}")
    except OSError as e:
        print(f"Error writing CSS file {css_path}: {e}")


def render_markdown_to_html(md_content, title, root_path):
    """Renders markdown content into a full HTML page."""
    body = md.render(md_content)
    return HTML_TEMPLATE.format(title=title, body_content=body, root_path=root_path)


def process_file(md_path, input_base, output_base):
    """Processes a single markdown file."""
    try:
        with open(md_path, encoding="utf-8") as f:
            md_content = f.read()

        relative_path = md_path.relative_to(input_base)
        output_html_path = output_base / relative_path.with_suffix(".html")
        output_html_dir = output_html_path.parent

        # Create output directory if it doesn't exist
        output_html_dir.mkdir(parents=True, exist_ok=True)

        # Calculate relative path to CSS file from the HTML file's directory
        depth = len(relative_path.parts) - 1  # How many levels deep is the file?
        root_path = ".." * depth if depth > 0 else "."

        # Use filename as title (simple approach)
        title = md_path.stem.replace("-", " ").replace("_", " ").title()

        html_content = render_markdown_to_html(md_content, title, root_path)

        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Processed: {md_path} -> {output_html_path}")

    except Exception as e:
        print(f"Error processing file {md_path}: {e}")


def copy_static_assets(input_dir, output_dir):
    """Copy static assets like CSS files from input to output directory."""
    static_files = list(input_dir.glob("*.css"))
    for file in static_files:
        try:
            shutil.copy2(file, output_dir)
            print(f"Copied static file: {file} -> {output_dir}")
        except Exception as e:
            print(f"Error copying static file {file}: {e}")


# --- Main Execution ---
def main():
    """Main function to generate the static site."""
    print("Starting static site generation...")

    # Clean and recreate output directory
    if OUTPUT_DIR.exists():
        print(f"Cleaning output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Created output directory: {OUTPUT_DIR}")

    # Generate Pygments CSS
    generate_pygments_css(OUTPUT_DIR, PYGMENTS_CSS_FILENAME)

    # Copy static assets
    copy_static_assets(INPUT_DIR, OUTPUT_DIR)

    # Find all markdown files in the input directory recursively
    md_files = list(INPUT_DIR.rglob("*.md"))

    if not md_files:
        print(f"No markdown files found in {INPUT_DIR}.")
        return

    print(f"Found {len(md_files)} markdown files to process.")

    # Process each markdown file
    for md_file in md_files:
        process_file(md_file, INPUT_DIR, OUTPUT_DIR)

    print("\nStatic site generation complete!")
    print(f"Output generated in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
