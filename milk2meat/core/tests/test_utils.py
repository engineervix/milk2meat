from milk2meat.core.utils.markdown import parse_markdown


class TestMarkdownUtils:
    def test_parse_markdown_none(self):
        """Test parsing None value"""
        assert parse_markdown(None) == ""
        assert parse_markdown("") == ""

    def test_parse_markdown_basic(self):
        """Test parsing basic markdown"""
        markdown = "# Heading\n\nThis is a paragraph."
        html = parse_markdown(markdown)

        assert "<h1>Heading</h1>" in html
        assert "<p>This is a paragraph.</p>" in html

    def test_parse_markdown_formatting(self):
        """Test parsing markdown formatting"""
        markdown = "**Bold text** and *italic text*"
        html = parse_markdown(markdown)

        assert "<strong>Bold text</strong>" in html
        assert "<em>italic text</em>" in html

    def test_parse_markdown_lists(self):
        """Test parsing markdown lists"""
        markdown = "- Item 1\n- Item 2\n- Item 3"
        html = parse_markdown(markdown)

        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "<li>Item 2</li>" in html
        assert "<li>Item 3</li>" in html
        assert "</ul>" in html

    def test_parse_markdown_code(self):
        """Test parsing markdown code blocks"""
        markdown = "```python\ndef hello():\n    print('Hello world!')\n```"
        html = parse_markdown(markdown)

        assert "<pre>" in html
        assert "<code>" in html
        assert "<span>def</span><span> </span><span>hello</span><span>():</span>" in html
        assert "<span>print</span><span>(</span><span>'Hello world!'</span><span>)</span>" in html
        assert "</code>" in html
        assert "</pre>" in html

    def test_parse_markdown_links(self):
        """Test parsing markdown links"""
        markdown = "[Link text](https://example.com)"
        html = parse_markdown(markdown)

        assert '<a href="https://example.com" rel="noopener noreferrer">Link text</a>' in html

    def test_markdown_tables(self):
        """Test parsing markdown tables"""
        markdown = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        html = parse_markdown(markdown)

        assert "<table>" in html
        assert "<thead>" in html
        assert "<tbody>" in html
        assert "<th>Header 1</th>" in html
        assert "<td>Cell 1</td>" in html

    def test_sanitize_html_script(self):
        """Test sanitization of script tags"""
        markdown = "# Title\n\n<script>alert('XSS')</script>"
        html = parse_markdown(markdown)

        assert "<h1>Title</h1>" in html
        assert "<script>" not in html
        assert "alert" not in html

    def test_sanitize_html_eventhandlers(self):
        """Test sanitization of event handlers"""
        markdown = "# Title\n\n<a href='#' onclick='alert(\"XSS\")'>Click me</a>"
        html = parse_markdown(markdown)

        assert "<h1>Title</h1>" in html
        assert '<a href="#" rel="noopener noreferrer">Click me</a>' in html
        assert "onclick" not in html

    def test_sanitize_html_iframes(self):
        """Test sanitization of iframes"""
        markdown = "# Title\n\n<iframe src='https://evil.com'></iframe>"
        html = parse_markdown(markdown)

        assert "<h1>Title</h1>" in html
        assert "<iframe" not in html

    def test_blockquotes(self):
        """Test parsing blockquotes (important for Bible verses)"""
        markdown = "> This is a Bible verse.\n> Second line of the verse."
        html = parse_markdown(markdown)

        assert "<blockquote>" in html
        assert "This is a Bible verse." in html
        assert "Second line of the verse." in html
        assert "</blockquote>" in html

    def test_task_lists(self):
        """Test parsing task lists"""
        markdown = "- [x] Completed task\n- [ ] Incomplete task"
        html = parse_markdown(markdown)

        assert "Completed task" in html
        assert "Incomplete task" in html
        # The exact HTML will depend on the pymdownx.tasklist extension config
        # but should at minimum contain the text
