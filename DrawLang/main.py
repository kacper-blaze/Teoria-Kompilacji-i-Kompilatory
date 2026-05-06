"""DrawLang front-end.

Usage:
    python main.py <input.draw> [--ast]

--ast   Pretty-print the parse tree instead of generating SVG.

Without --ast the program is fully interpreted (variables, loops,
procedures, expressions) and the result is written as an SVG file
next to the input file.
"""
from __future__ import annotations

import sys
from pathlib import Path
from lark import Lark

from interpreter import Interpreter

GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")


def build_parser() -> Lark:
    return Lark(GRAMMAR_PATH.read_text(encoding="utf-8"), start="start")


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

    interp = Interpreter()
    svg = interp.run(tree)

    out_path = source_path.with_suffix(".svg")
    out_path.write_text(svg, encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
