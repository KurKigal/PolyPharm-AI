import html


def esc(value) -> str:
    return html.escape(str(value))
