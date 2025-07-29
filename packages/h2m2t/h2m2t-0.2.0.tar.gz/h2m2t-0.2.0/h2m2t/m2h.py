from mistune import HTMLRenderer, create_markdown


def markdown_to_html(md: str) -> str:
    renderer = HTMLRendererFixed(escape=False, allow_harmful_protocols=True)
    markdown = create_markdown(
        renderer=renderer,
        plugins=[
            # Default:
            "strikethrough",
            "footnotes",
            "table",
            "speedup",
            # Enabled:
            "url",
            "task_lists",
            "def_list",
            "abbr",
            "mark",
            "insert",
            "superscript",
            "subscript",
            "math",
            # "ruby",
            "spoiler",
        ],
    )
    html = markdown(md)

    return f'<!doctype html><html><head><meta charset="utf-8"><title></title></head><body>{html}</body></html>'


class HTMLRendererFixed(HTMLRenderer):
    def link(self, text: str, url: str, title: str | None = None) -> str:
        url = url.replace("%20", " ")
        url = url.replace("%28", "(").replace("%29", ")")
        return super().link(text, url, title)
