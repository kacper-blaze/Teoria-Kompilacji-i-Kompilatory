# DrawLang

## Autorzy

* Kacper Kobieluch – [kkobieluch@student.agh.edu.pl](mailto:kkobieluch@student.agh.edu.pl)
* Kacper Kustra – [kkustra@student.agh.edu.pl](mailto:kkustra@student.agh.edu.pl)

---

# Opis projektu

## Temat projektu

DrawLang to autorski język dziedzinowy (DSL – Domain Specific Language) służący do generowania grafiki wektorowej SVG za pomocą prostych instrukcji tekstowych.

Projekt implementuje interpreter własnego języka programowania wraz z parserem i systemem wykonywania instrukcji.

---

# Założenia programu

## Cel projektu

Celem projektu jest:

- zaprojektowanie własnego języka dziedzinowego,
- implementacja parsera i interpretera,
- obsługa instrukcji sterujących i procedur,
- generowanie grafiki SVG,
- praktyczne wykorzystanie narzędzi do analizy składniowej.

---

## Rodzaj translatora

Projekt jest:

- interpreterem języka DrawLang.

Program:
- analizuje kod źródłowy,
- buduje drzewo składniowe AST,
- interpretuje instrukcje programu,
- generuje wynikowy plik SVG.

---

## Wynik działania programu

Interpreter przyjmuje program zapisany w języku DrawLang i generuje:

- grafikę wektorową SVG.

Przykładowe zastosowania:
- rysowanie figur geometrycznych,
- generowanie wzorów,
- eksperymenty z własnym językiem programowania,
- wizualizacja algorytmów geometrycznych.

---

## Język implementacji

Projekt został zaimplementowany w:

- Python 3.11+

---

## Sposób realizacji parsera

Projekt wykorzystuje bibliotekę:

- Lark (Python parsing library)

Parser został zaimplementowany z użyciem formalnej gramatyki zapisanej w pliku `grammar.lark`.

Lark został wybrany ze względu na:

- prostą integrację z Pythonem,
- obsługę gramatyk EBNF,
- możliwość użycia parsera Earley,
- brak konieczności generowania dodatkowego kodu parsera.

Rozważane alternatywy:

- ANTLR4,
- PLY (Python Lex-Yacc),
- Bison / YACC.

---

# Architektura programu

Proces przetwarzania programu DrawLang przebiega w kilku etapach:

1. Analiza leksykalna (tokenizacja),
2. Analiza składniowa (parser),
3. Budowa drzewa składniowego AST,
4. Interpretacja instrukcji programu,
5. Generowanie pliku SVG.

Schemat działania:

```text
Kod DrawLang
      ↓
Lexer / Parser (Lark)
      ↓
AST (Abstract Syntax Tree)
      ↓
Interpreter
      ↓
SVG
```

---

# Tokeny

## Słowa kluczowe

| Kategoria             | Leksemy |
|----------------------|----------|
| grafika              | `canvas`, `circle`, `line`, `rect`, `color`, `translate`, `scale` |
| sterowanie przepływem| `if`, `else`, `while`, `for`, `to`, `step`, `repeat`, `break`, `continue` |
| deklaracje           | `let`, `proc`, `return` |
| logiczne             | `and`, `or`, `not`, `true`, `false` |

---

## Literały i identyfikatory

| Token | Wzorzec | Przykład |
|------|------|------|
| `NUMBER` | `[0-9]+(\.[0-9]+)?` | `10`, `3.14` |
| `IDENTIFIER` | `[a-zA-Z_][a-zA-Z0-9_]*` | `x`, `radius` |
| `STRING` | `"..."` | `"hello"` |
| `HEX_COLOR` | `#[0-9a-fA-F]{6}` | `#FF00AA` |

---

## Operatory

| Typ | Operatory |
|------|------|
| arytmetyczne | `+ - * / %` |
| porównania | `== != < > <= >=` |
| logiczne | `and or not` |
| przypisanie | `=` |

---

## Separatory i grupowanie

| Symbol |
|------|
| `(` `)` |
| `{` `}` |
| `,` |

---

## Komentarze

Obsługiwane są:

```drawlang
// komentarz liniowy
```

oraz:

```drawlang
/* komentarz blokowy */
```

---

# Gramatyka języka

Pełna definicja gramatyki znajduje się w pliku:

```text
grammar.lark
```

Projekt wykorzystuje notację parsera Lark (EBNF-like).

---

## Fragment gramatyki

```ebnf
program: statement*

?statement: var_decl
          | assign_stmt
          | if_stmt
          | while_stmt
          | for_stmt
          | repeat_stmt
          | proc_decl
          | return_stmt
          | shape_stmt
          | call_stmt
```

---

## Wyrażenia arytmetyczne

```ebnf
?sum: product (add_op product)*
?product: unary (mul_op unary)*
```

Obsługiwane operatory:

- `+`
- `-`
- `*`
- `/`
- `%`

---

## Wyrażenia logiczne

```ebnf
?logical_expr: or_expr
?or_expr: and_expr (_OR and_expr)*
?and_expr: not_expr (_AND not_expr)*
```

Obsługiwane są:

- `and`
- `or`
- `not`
- operatory porównań

---

# Funkcjonalności języka

## Instrukcje rysujące

### Canvas

```drawlang
canvas width height
```

### Okręgi

```drawlang
circle x y r
```

### Linie

```drawlang
line x1 y1 x2 y2
```

### Prostokąty

```drawlang
rect x y width height
```

---

## Kolory i transformacje

```drawlang
color "#FF0000"
translate 50 50
scale 2
```

---

## Zmienne

```drawlang
let x = 10
x = x + 1
```

---

## Instrukcje sterujące

### If / else

```drawlang
if x > 10 {
    circle 100 100 50
}
else {
    rect 50 50 100 100
}
```

### While

```drawlang
while x < 100 {
    x = x + 10
}
```

### For

```drawlang
for i = 0 to 10 step 2 {
    circle i 100 10
}
```

### Repeat

```drawlang
repeat 5 {
    circle 50 50 10
}
```

---

## Procedury

```drawlang
proc star(cx, cy, r) {
    circle cx cy r
}

star(100, 100, 40)
```

Obsługiwane są:

- argumenty,
- lokalne zmienne,
- instrukcja `return`.

---

## Funkcje matematyczne

Dostępne funkcje:

- `sin(x)`
- `cos(x)`
- `tan(x)`
- `sqrt(x)`
- `abs(x)`
- `round(x)`
- `floor(x)`
- `ceil(x)`
- `min(a, b)`
- `max(a, b)`

---

# Interpreter

Interpreter wykonuje program bezpośrednio na podstawie drzewa AST.

Obsługiwane mechanizmy:

- zmienne,
- lokalne zakresy (scope),
- procedury,
- instrukcje sterujące,
- wyrażenia logiczne,
- transformacje geometryczne,
- generowanie SVG.

---

# AST – Abstract Syntax Tree

Parser buduje abstrakcyjne drzewo składniowe AST.

Przykład:

Kod:

```drawlang
let x = 5 + 2
```

AST:

```text
var_decl
 ├── x
 └── sum
      ├── 5
      ├── +
      └── 2
```

---

# Obsługa błędów

Interpreter obsługuje:

- błędy składniowe,
- nieznane zmienne,
- nieznane procedury,
- błędną liczbę argumentów,
- błędy wykonania,
- walidację parametrów figur geometrycznych.

---

# Pakiety zewnętrzne

Projekt wykorzystuje:

| Pakiet | Zastosowanie |
|------|------|
| `lark` | parser i analiza składniowa |
| `math` | funkcje matematyczne |

---

# Instalacja

## 1. Sklonowanie repozytorium

```bash
git clone <repo-url>
cd DrawLang
```

---

## 2. Utworzenie środowiska wirtualnego

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

---

## 3. Instalacja zależności

```bash
pip install -r requirements.txt
```

---

# Instrukcja obsługi

Generowanie SVG:

```bash
python main.py examples/showcase.draw
```

Wynik zostanie zapisany jako:

```text
examples/showcase.svg
```

---

## Wyświetlenie AST (drzewa składniowego)

```bash
python main.py examples/showcase.draw --ast
```

---

# Przykład użycia

## Program wejściowy

```drawlang
canvas 300 300

color "#ff0000"

circle 150 150 50

line 0 0 300 300
```

---

## Wynik SVG

```xml
<svg width="300" height="300">
  <circle cx="150" cy="150" r="50"
          stroke="#ff0000"
          fill="#ff0000" />

  <line x1="0" y1="0"
        x2="300" y2="300"
        stroke="#ff0000" />
</svg>
```

---

# Struktura projektu

```text
DrawLang/
├── examples/
│   ├── test_simple_showcase.draw
│   ├── test.draw
│   ├── showcase.draw
│   ├── mistakeInFile.draw
│   ├── complex.draw
│   ├── blank.draw
│   └── advanced.draw
├── grammar.lark
├── interpreter.py
├── main.py
├── requirements.txt
└── README.md
```

---

# Możliwe rozszerzenia

Planowane rozszerzenia projektu:

- eksport do PNG,
- dodatkowe figury geometryczne,
- animacje SVG,
- grupowanie elementów,
- rotacje,
- transformacje macierzowe,
- obsługa tablic,
- import plików.

---

# Wartość projektu

Projekt demonstruje:

- projektowanie własnego języka programowania,
- tworzenie parsera i interpretera,
- budowę AST,
- implementację mechanizmów wykonawczych,
- generowanie grafiki SVG,
- praktyczne wykorzystanie formalnych gramatyk.

---