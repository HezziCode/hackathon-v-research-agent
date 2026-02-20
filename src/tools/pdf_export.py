"""T051: PDF export — Markdown to PDF via WeasyPrint."""

from __future__ import annotations

import logging
from pathlib import Path

import markdown as md

logger = logging.getLogger(__name__)

REPORT_CSS = """
body { font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }
h1 { color: #1a1a2e; border-bottom: 2px solid #16213e; padding-bottom: 10px; }
h2 { color: #16213e; margin-top: 30px; }
h3 { color: #0f3460; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; }
th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
th { background-color: #16213e; color: white; }
blockquote { border-left: 4px solid #16213e; padding-left: 16px; color: #555; }
code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
.confidence-high { color: #27ae60; }
.confidence-medium { color: #f39c12; }
.confidence-low { color: #e74c3c; }
"""


def markdown_to_pdf(markdown_content: str, output_path: str) -> str:
    """Convert Markdown to PDF using WeasyPrint.

    Returns the output file path.
    """
    try:
        from weasyprint import HTML
    except ImportError:
        logger.error("WeasyPrint not installed — skipping PDF generation")
        return ""

    html_content = md.markdown(
        markdown_content,
        extensions=["tables", "fenced_code", "toc"],
    )

    full_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>{REPORT_CSS}</style></head>
<body>{html_content}</body>
</html>"""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    HTML(string=full_html).write_pdf(str(output))
    logger.info("PDF generated: %s", output_path)
    return str(output)
