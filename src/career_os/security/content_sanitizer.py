from __future__ import annotations

from bs4 import BeautifulSoup

from .prompt_injection import sanitize_external_content


def strip_html(html: str) -> str:
    """Reduce a raw web page to visible text before it ever reaches an LLM
    prompt — removes <script>/<style> content and hidden-instruction vectors
    like HTML comments and off-screen text nodes."""
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda s: s.strip().startswith("<!--")):
        comment.extract()
    return soup.get_text(separator="\n", strip=True)


def sanitize_html_content(html: str, source: str) -> dict:
    text = strip_html(html)
    return sanitize_external_content(text, source=source)
