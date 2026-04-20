"""DrawLang front-end.

Usage:
    python main.py <input.draw> [--ast]

Without --ast the script tries to render simple shape statements
(canvas / circle / line / rect / color) into an SVG file, ignoring
control-flow and procedure declarations. The full interpreter for
variables, loops and procedures will be implemented in a later step.

With --ast the parsed syntax tree is pretty-printed instead.
"""

from __future__ import annotations

import sys
from pathlib import Path

from lark import Lark, Tree, Token


GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")


def build_parser() -> Lark:
    return Lark(GRAMMAR_PATH.read_text(encoding="utf-8"), start="start")


def literal(node) -> str:
    """Render a leaf expression as a literal string for the SVG output.

    Anything more complex than NUMBER / IDENTIFIER / HEX_COLOR is
    rejected for now (SVG generation is intentionally minimal).
    """
    if isinstance(node, Token):
        return str(node)
    if isinstance(node, Tree) and node.data == "number":
        return str(node.children[0])
    if isinstance(node, Tree) and node.data == "var":
        raise ValueError(
            f"variable references are not supported by the basic SVG backend "
            f"(got '{node.children[0]}')"
        )
    raise ValueError(f"unsupported expression in shape statement: {node}")


def render_svg(tree: Tree) -> str:
    width, height = "200", "200"
    body: list[str] = []
    current_color: str | None = None

    def color_attr() -> str:
        return f' stroke="{current_color}" fill="{current_color}"' if current_color else ""

    for stmt in tree.children:
        if not isinstance(stmt, Tree):
            continue

        if stmt.data == "canvas_stmt":
            width, height = literal(stmt.children[0]), literal(stmt.children[1])

        elif stmt.data == "circle_stmt":
            x, y, r = (literal(c) for c in stmt.children)
            body.append(f'  <circle cx="{x}" cy="{y}" r="{r}"{color_attr()} />')

        elif stmt.data == "line_stmt":
            x1, y1, x2, y2 = (literal(c) for c in stmt.children)
            body.append(
                f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{color_attr()} />'
            )

        elif stmt.data == "rect_stmt":
            x, y, w, h = (literal(c) for c in stmt.children)
            body.append(
                f'  <rect x="{x}" y="{y}" width="{w}" height="{h}"{color_attr()} />'
            )

        elif stmt.data == "color_stmt":
            value_node = stmt.children[0]
            current_color = str(value_node.children[0])

    inner = "\n".join(body)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}">\n{inner}\n</svg>\n'
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1

    show_ast = "--ast" in argv[2:]
    source_path = Path(argv[1])

    parser = build_parser()
    tree = parser.parse(source_path.read_text(encoding="utf-8"))

    if show_ast:
        print(tree.pretty())
        return 0

    try:
        svg = render_svg(tree)
    except ValueError as exc:
        print(f"[warn] cannot generate SVG: {exc}", file=sys.stderr)
        print("       printing AST instead:\n", file=sys.stderr)
        print(tree.pretty())
        return 0

    out_path = source_path.with_suffix(".svg")
    out_path.write_text(svg, encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
