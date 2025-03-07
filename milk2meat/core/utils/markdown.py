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
        "tables",
        "pymdownx.superfences",
        "pymdownx.highlight",
        "pymdownx.betterem",
        "pymdownx.tasklist",
        "pymdownx.smartsymbols",
    ]

    extension_configs = {
        "pymdownx.highlight": {
            "css_class": "highlight",
        }
    }

    # Convert markdown to HTML
    html = markdown.markdown(text, extensions=extensions, extension_configs=extension_configs)

    # Sanitize HTML
    sanitized_html = nh3.clean(html)

    return sanitized_html
