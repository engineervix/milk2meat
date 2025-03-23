import markdown
import nh3


def parse_markdown(text):
    """
    Parse markdown text and return sanitized HTML.

    Args:
        text (str): Markdown text to parse

    Returns:
        str: Sanitized HTML
    """
    if not text:
        return ""

    # Configure markdown extensions
    extensions = [
        "smarty",
        "tables",
        "toc",
        "pymdownx.betterem",
        "pymdownx.caret",
        "pymdownx.keys",
        "pymdownx.magiclink",
        "pymdownx.mark",
        "pymdownx.smartsymbols",
        "pymdownx.superfences",
        "pymdownx.tasklist",
        "pymdownx.tilde",
    ]

    # Convert markdown to HTML
    html = markdown.markdown(text, extensions=extensions)

    # Sanitize HTML
    sanitized_html = nh3.clean(html)

    return sanitized_html
