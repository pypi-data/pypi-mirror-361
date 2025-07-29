# The Library of Babbl

Turn markdown into beautiful research blog posts.

![Babbl](assets/babel_img.jpg)

## Features

- **Custom Markdown Renderer**: Built with Marko for extensible HTML formatting
- **Frontmatter Support**: YAML frontmatter in markdown files
- **Table Support**: Full markdown table rendering with custom styling
- **Beautiful Templates**: Clean, responsive HTML output with modern styling
- **Fully Customizable CSS**: Complete control over styling through CSS files
- **CLI Interface**: Easy-to-use command-line tools
- **Syntax Highlighting**: Code blocks with Pygments integration

## Installation

```bash
pip install babbl
```

## Quick Start

### Render a single markdown file:

```bash
babbl render example.md
```

### Build multiple files in a directory:

```bash
babbl build ./docs --output-dir ./public
```

### Render with custom CSS file:

```bash
babbl render example.md --css my-styles.css
```

## Usage

### Python API

```python
from babbl import HTMLRenderer, BabblParser
from pathlib import Path

# Initialize parser and renderer
parser = BabblParser()
renderer = HTMLRenderer()

# Render a markdown file
with open("example.md", "r") as f:
    content = f.read()
document = parser.parse(content)
html = renderer.html(document, metadata={})
print(f"Generated HTML: {html}")
```

### Frontmatter Support

Babbl supports YAML frontmatter in markdown files:

```markdown
---
title: "My Research Paper"
author: "Dr. Jane Smith"
date: "2024-01-15"
description: "A groundbreaking study"
---

# Content here...
```

### Table Support

Babbl includes full support for markdown tables:

```markdown
| Component | Memory (MB) | Percentage |
|-----------|-------------|------------|
| Renderer Core | 2.1 | 50% |
| Frontmatter Processor | 0.9 | 22% |
| HTML Formatter | 1.2 | 28% |
```

Tables are automatically styled with clean, responsive CSS and support proper header formatting.

### CSS Customization

Babbl provides complete control over styling through CSS files:

**Customize your styles:**
```css
/* my-styles.css */
body {
    font-family: "Georgia", serif;
    background-color: #f5f5f5;
    color: #333;
}

.heading-1 {
    color: #2c3e50;
    font-size: 2.5rem;
    border-bottom: 2px solid #3498db;
}

.code-block {
    background: #2c3e50;
    color: #ecf0f1;
    border-radius: 8px;
}
```

**Use your custom styles:**
```bash
babbl render example.md --css my-styles.css
```

The CSS system supports all standard CSS properties for:
- Body and section styling
- All heading levels (h1-h6)
- Paragraphs and text
- Code blocks and inline code
- Links and images
- Lists and blockquotes
- Emphasis (bold/italic)
- Responsive design
- Syntax highlighting

### Table of Contents

Babbl can automatically generate a table of contents for documents with h1 headings:

```bash
# Generate HTML with table of contents
babbl render example.md --toc
```

The table of contents:
- Appears as a sidebar on the left side of the content
- Lists all h1 headings with clickable links
- Is responsive and collapses on mobile devices
- Uses clean, modern styling that matches the document theme
- Provides smooth scrolling to section anchors

**Python API usage:**
```python
from babbl import HTMLRenderer, BabblParser

parser = BabblParser()
renderer = HTMLRenderer(show_toc=True)  # Enable table of contents

document = parser.parse(content)
html = renderer.html(document, metadata={})
```

## CLI Commands

### `babbl render <file>`
Render a single markdown file to HTML.

Options:
- `--output, -o`: Specify output file path
- `--css`: Path to CSS file
- `--toc`: Generate table of contents for h1 headings

### `babbl build <directory>`
Build multiple markdown files in a directory.

Options:
- `--output-dir, -o`: Output directory
- `--pattern`: File pattern to match (default: `*.md`)
- `--recursive, -r`: Process subdirectories
- `--css`: Path to CSS file
- `--toc`: Generate table of contents for h1 headings

## Supported Markdown Features

- **Headings**: `# ## ###` etc.
- **Code blocks**: ```python with syntax highlighting
- **Inline code**: `code`
- **Links**: `[text](url)`
- **Images**: `![alt](src)`
- **Lists**: Ordered and unordered
- **Blockquotes**: `> quote`
- **Emphasis**: **bold** and *italic*
- **Tables**: Full markdown table support
- **Paragraphs**: Automatic wrapping

## License

MIT License