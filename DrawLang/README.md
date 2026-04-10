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

### (Optional Extensions)

* `repeat n { ... }`
* `translate x y`
* `scale s`

---

## 🧩 Tokens

* KEYWORDS: `circle`, `line`, `rect`, `canvas`, `color`
* NUMBER: integers and floating-point numbers
* IDENTIFIER: names (e.g., color names)
* HEX_COLOR: `#RRGGBB`
* SYMBOLS: `{ }`

---

## 📜 Grammar (Lark)

```
?start: program

program: statement*

statement: canvas
         | circle
         | line
         | rect
         | color

canvas: "canvas" NUMBER NUMBER

circle: "circle" NUMBER NUMBER NUMBER
line: "line" NUMBER NUMBER NUMBER NUMBER
rect: "rect" NUMBER NUMBER NUMBER NUMBER

color: "color" (IDENTIFIER | HEX)

%import common.NUMBER
%import common.CNAME -> IDENTIFIER
%import common.WS
%ignore WS

HEX: /#[0-9a-fA-F]{6}/
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
