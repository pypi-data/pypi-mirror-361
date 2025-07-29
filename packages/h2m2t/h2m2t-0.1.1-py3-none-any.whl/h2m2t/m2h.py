from mistune import create_markdown


def markdown_to_html(md: str) -> str:
    markdown = create_markdown(
        escape=False,
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
