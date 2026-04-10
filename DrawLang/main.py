from lark import Lark

with open("grammar.lark") as f:
    grammar = f.read()

parser = Lark(grammar)

with open("examples/test.draw") as f:
    code = f.read()

tree = parser.parse(code)

# print(tree.pretty())
svg = '<svg width="200" height="200">\n'

for stmt in tree.children:
    if stmt.data == "circle":
        x, y, r = stmt.children
        svg += f'<circle cx="{x}" cy="{y}" r="{r}" />\n'

svg += '</svg>'

with open("output.svg", "w") as f:
    f.write(svg)