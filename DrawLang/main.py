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
from lark.exceptions import LarkError, UnexpectedCharacters, UnexpectedToken

from interpreter import Interpreter

GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")


def build_parser() -> Lark:
    return Lark(GRAMMAR_PATH.read_text(encoding="utf-8"), start="start", lexer="basic")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1

    show_ast = "--ast" in argv[2:]
    source_path = Path(argv[1])

    parser = build_parser()
    
    try:
        source_text = source_path.read_text(encoding="utf-8")
        tree = parser.parse(source_text)
    except (UnexpectedCharacters, UnexpectedToken) as e:
        print(f"Syntax error in {source_path}:")
        
        # Determine the position
        line = getattr(e, "line", "?")
        column = getattr(e, "column", "?")
        
        if isinstance(e, UnexpectedToken):
            found = f"'{e.token.value}'"
        else:
            # UnexpectedCharacters has a different structure
            found = f"'{source_text[e.pos_in_stream]}'" if hasattr(e, "pos_in_stream") else "unknown character"

        print(f"  Unexpected {found} at line {line}, column {column}.")
        
        # Show context if available
        try:
            print("\n" + e.get_context(source_text))
        except Exception:
            pass

        if isinstance(e, UnexpectedToken) and e.expected:
            # Simple heuristic to clean up terminal names
            clean_expected = []
            for term in e.expected:
                if term.startswith("__ANON"): continue # Skip anonymous terminals
                name = term.lstrip("_")
                clean_expected.append(name.lower() if term.startswith("_") else name)
            
            if clean_expected:
                print(f"  Expected one of: {', '.join(sorted(set(clean_expected)))}")

        return 1
    except LarkError as e:
        print(f"Parse error in {source_path}: {e}")
        return 1

    if show_ast:
        print(tree.pretty())
        return 0

    try:
        interp = Interpreter()
        svg = interp.run(tree)
    except (ValueError, TypeError, NameError) as e:
        print(f"Runtime error in {source_path}: {e}")
        return 1

    out_path = source_path.with_suffix(".svg")
    out_path.write_text(svg, encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
