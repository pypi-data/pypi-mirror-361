from typing import List


def generate_table(headers: List[str], data: List[List[str]]):
    widths = [[len(str(cell)) for cell in row] for row in data + [headers]]
    widths = [max(width) for width in zip(*widths)]

    def get_line(row):
        line = ""
        for idx, cell in enumerate(row):
            width = widths[idx]
            line += str(cell).ljust(width)
            line += "  "
        return line + "\n"

    underlines = ["-" * width for width in widths]

    yield get_line(headers)
    yield get_line(underlines)

    for row in data:
        yield get_line(row)
