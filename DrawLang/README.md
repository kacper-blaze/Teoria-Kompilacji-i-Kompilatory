# 🎨 DrawLang – A Domain-Specific Language for Vector Graphics

## 📌 Authors

* Kacper Kobieluch – [kkobieluch@student.agh.edu.pl](mailto:kkobieluch@student.agh.edu.pl)
* Kacper Kustra – [kkustra@student.agh.edu.pl](mailto:kkustra@student.agh.edu.pl)

---

## 🛠️ Implementation Language

* Python 3.11+

---

## ⚙️ Parser Generator

This project uses:

* **Lark (Python parsing library)**

Alternative tools:

* ANTLR4
* PLY (Python Lex-Yacc)
* Bison / YACC

Lark was chosen because:

* it is easy to use and beginner-friendly
* it does not require external code generation
* it integrates directly with Python

---

## 🎯 Project Goal

DrawLang is a custom domain-specific language (DSL) designed to describe vector graphics using simple textual commands.

The program parses DrawLang code and generates:

* SVG images

---

## 📥 Input Format

Example program:

```
canvas 200 200

circle 100 100 50
line 0 0 200 200

color red
circle 50 50 20
```

---

## 📤 Output Format

The program generates an SVG file, for example:

```xml
<svg width="200" height="200">
  <circle cx="100" cy="100" r="50" />
  <line x1="0" y1="0" x2="200" y2="200" />
</svg>
```

---

## ✨ Features

### Basic Shapes

* `circle x y r`
* `line x1 y1 x2 y2`
* `rect x y width height`

### Settings

* `canvas width height`
* `color name`
* `color #RRGGBB`
* `translate x y`
* `scale s`

### Variables

* `let x = 10`
* `x = x + 1`

### Control flow

* `if cond { ... } else if cond { ... } else { ... }`
* `while cond { ... }`
* `for i = 0 to 10 { ... }` (optionally `step expr`)
* `repeat n { ... }`
* `break`    – exit the innermost loop
* `continue` – skip to the next loop iteration

### Procedures

```
proc star(cx, cy, r) {
    circle cx cy r
}

star(100, 100, 40)
```

* declaration: `proc NAME(p1, p2, ...) { ... }`
* call:        `NAME(a1, a2, ...)`
* `return expr` is supported (optional value)

### Expressions

* arithmetic: `+ - * / %`
* comparison: `== != < > <= >=`
* logical:    `and`, `or`, `not`
* literals:   numbers, strings (`"hello"`), `true`, `false`
* grouping:   `( ... )`
* function calls inside expressions

### Comments

* `// line comment`
* `/* block comment */`

---

## 🧩 Tokens

### Keywords (reserved)

| Token       | Lexem                                                                                       |
|-------------|---------------------------------------------------------------------------------------------|
| shape kw    | `canvas`, `circle`, `line`, `rect`, `color`, `translate`, `scale`                           |
| control kw  | `if`, `else`, `while`, `for`, `to`, `step`, `repeat`, `return`, `break`, `continue`         |
| binding kw  | `let`, `proc`                                                                               |
| logical kw  | `and`, `or`, `not`, `true`, `false`                                                         |

### Literals & identifiers

| Token        | Pattern (regex)                          | Example          |
|--------------|------------------------------------------|------------------|
| `NUMBER`     | `[0-9]+ ( "." [0-9]+ )?`                 | `42`, `3.14`     |
| `IDENTIFIER` | `[a-zA-Z_][a-zA-Z0-9_]*`                 | `red`, `cx`      |
| `STRING`     | `"([^"\\]\|\\.)*"` (escaped string)      | `"hello"`        |
| `HEX_COLOR`  | `#[0-9a-fA-F]{6}`                        | `#FF00AA`        |

### Operators & punctuation

| Token       | Lexem(s)                              |
|-------------|---------------------------------------|
| arithmetic  | `+`  `-`  `*`  `/`  `%`               |
| comparison  | `==` `!=` `<` `>` `<=` `>=`           |
| assignment  | `=`                                   |
| grouping    | `(`  `)`  `{`  `}`                    |
| separator   | `,`                                   |

### Ignored

| Token         | Pattern             | Action  |
|---------------|---------------------|---------|
| `WS`          | `[ \t\r\n]+`        | skipped |
| `CPP_COMMENT` | `//[^\n]*`          | skipped |
| `C_COMMENT`   | `/* ... */`         | skipped |

---

## 📜 Grammar (Lark)

The complete grammar lives in [`grammar.lark`](grammar.lark). High-level summary:

```
program     ::= statement*

statement   ::= var_decl | assign_stmt
              | if_stmt  | while_stmt | for_stmt | repeat_stmt
              | break_stmt | continue_stmt
              | proc_decl | return_stmt | call_stmt
              | shape_stmt

var_decl    ::= "let" IDENTIFIER "=" expr
assign_stmt ::= IDENTIFIER "=" expr

if_stmt     ::= "if" expr block ("else" (if_stmt | block))?
while_stmt  ::= "while" expr block
for_stmt    ::= "for" IDENTIFIER "=" expr "to" expr ("step" expr)? block
repeat_stmt ::= "repeat" expr block

break_stmt    ::= "break"
continue_stmt ::= "continue"

proc_decl   ::= "proc" IDENTIFIER "(" params? ")" block
params      ::= IDENTIFIER ("," IDENTIFIER)*
return_stmt ::= "return" expr?
call_stmt   ::= call
call        ::= IDENTIFIER "(" args? ")"
args        ::= expr ("," expr)*

shape_stmt  ::= "canvas"    expr expr
              | "circle"    expr expr expr
              | "line"      expr expr expr expr
              | "rect"      expr expr expr expr
              | "color"     (HEX_COLOR | STRING | IDENTIFIER)
              | "translate" expr expr
              | "scale"     expr

block       ::= "{" statement* "}"

expr        ::= or_expr
or_expr     ::= and_expr ("or" and_expr)*
and_expr    ::= not_expr ("and" not_expr)*
not_expr    ::= "not" not_expr | comparison
comparison  ::= sum (("==" | "!=" | "<=" | ">=" | "<" | ">") sum)?
sum         ::= product (("+" | "-") product)*
product     ::= unary (("*" | "/" | "%") unary)*
unary       ::= "-" unary | atom
atom        ::= NUMBER | STRING | "true" | "false"
              | call | IDENTIFIER | "(" expr ")"
```

---

## 🔄 Processing Pipeline

1. Lexical analysis (tokenization)
2. Syntax analysis (parsing using Lark)
3. Building an internal representation (scene model)
4. Interpreting commands
5. Generating SVG output

---

## 🧪 Examples

### Example 1

Input:

```
canvas 200 200
circle 100 100 50
```

Output:

* A circle centered in the canvas

---

### Example 2

Input:

```
canvas 300 300
color blue
rect 50 50 200 100
line 0 0 300 300
```

---

## 📚 Functional Requirements

* parsing DrawLang programs
* supporting basic shapes
* generating valid SVG output
* handling colors

---

## ⚙️ Non-Functional Requirements

* clean and readable code
* modular architecture
* easy extensibility
* complete documentation in repository

---

## 🚀 Possible Extensions

* PNG export (e.g., using Pillow)
* grouping elements
* variables support
* SVG animations

---

## 📁 Project Structure

```
/grammar
/src
    parser.py
    interpreter.py
    svg_generator.py
/examples
README.md
```

---

## 💼 Project Value

This project demonstrates:

* creation of a custom DSL
* use of a parser generator
* transformation from text → graphics

---

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd DrawLang
   
2. Create and activate virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
## ▶️ Usage (planned)

```
python main.py input.draw
```

---
