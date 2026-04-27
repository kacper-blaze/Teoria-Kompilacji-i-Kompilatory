# DrawLang – język dziedzinowy do grafiki wektorowej

## Autorzy

* Kacper Kobieluch – [kkobieluch@student.agh.edu.pl](mailto:kkobieluch@student.agh.edu.pl)
* Kacper Kustra – [kkustra@student.agh.edu.pl](mailto:kkustra@student.agh.edu.pl)

---

## Język implementacji

* Python 3.11+

---

## Generator parsera

Projekt korzysta z biblioteki:

* **Lark (Python parsing library)**

Rozważane alternatywy:

* ANTLR4
* PLY (Python Lex-Yacc)
* Bison / YACC

Lark został wybrany, ponieważ:

* jest prosty w użyciu i przyjazny dla początkujących,
* nie wymaga zewnętrznej generacji kodu,
* integruje się bezpośrednio z Pythonem.

---

# Interpreter własnego języka

## Cel projektu

DrawLang to autorski język dziedzinowy (DSL) służący do opisywania grafiki wektorowej za pomocą prostych komend tekstowych.

Program parsuje kod w DrawLang i generuje:

* obrazy w formacie SVG.

---

## Format wejściowy

Przykładowy program:

```
canvas 200 200

circle 100 100 50
line 0 0 200 200

color red
circle 50 50 20
```

---

## Format wyjściowy

Wynikiem działania programu jest plik SVG, na przykład:

```xml
<svg width="200" height="200">
  <circle cx="100" cy="100" r="50" />
  <line x1="0" y1="0" x2="200" y2="200" />
</svg>
```

---

## Funkcjonalności

### Podstawowe kształty

* `circle x y r`
* `line x1 y1 x2 y2`
* `rect x y width height`

### Ustawienia sceny

* `canvas width height`
* `color name`
* `color #RRGGBB`
* `translate x y`
* `scale s`

### Zmienne

* `let x = 10`
* `x = x + 1`

### Sterowanie przepływem

* `if cond { ... } else if cond { ... } else { ... }`
* `while cond { ... }`
* `for i = 0 to 10 { ... }` (opcjonalnie `step expr`)
* `repeat n { ... }`
* `break`    – wyjście z najbliższej pętli
* `continue` – przejście do kolejnej iteracji

### Procedury

```
proc star(cx, cy, r) {
    circle cx cy r
}

star(100, 100, 40)
```

* deklaracja: `proc NAZWA(p1, p2, ...) { ... }`
* wywołanie: `NAZWA(a1, a2, ...)`
* obsługiwana jest instrukcja `return expr` (wartość opcjonalna)

### Wyrażenia

#### Wyrażenia arytmetyczne
* operatory: `+ - * / %`
* literały: liczby, zmienne, wywołania funkcji
* grupowanie: `( ... )`

#### Wyrażenia logiczne  
* operatory: `and`, `or`, `not`
* porównania: `== != < > <= >=` (porównują wyrażenia arytmetyczne)
* literały: `true`, `false`

#### Wspólne elementy
* zmienne i identyfikatory
* wywołania funkcji
* łańcuchy znaków (`"hello"`)

### Komentarze

* `// komentarz liniowy`
* `/* komentarz blokowy */`

---

## Tokeny

### Słowa kluczowe (zarezerwowane)

| Kategoria             | Leksemy                                                                             |
|-----------------------|-------------------------------------------------------------------------------------|
| kształty / scena      | `canvas`, `circle`, `line`, `rect`, `color`, `translate`, `scale`                   |
| sterowanie przepływem | `if`, `else`, `while`, `for`, `to`, `step`, `repeat`, `return`, `break`, `continue` |
| deklaracje            | `let`, `proc`                                                                       |
| logiczne / literały   | `and`, `or`, `not`, `true`, `false`                                                 |

### Literały i identyfikatory

| Token        | Wzorzec (regex)                          | Przykład         |
|--------------|------------------------------------------|------------------|
| `NUMBER`     | `[0-9]+ ( "." [0-9]+ )?`                 | `42`, `3.14`     |
| `IDENTIFIER` | `[a-zA-Z_][a-zA-Z0-9_]*`                 | `red`, `cx`      |
| `STRING`     | `"([^"\\]\|\\.)*"` (z sekwencjami `\`)   | `"hello"`        |
| `HEX_COLOR`  | `#[0-9a-fA-F]{6}`                        | `#FF00AA`        |

### Operatory i znaki interpunkcyjne

| Kategoria   | Leksemy                               |
|-------------|---------------------------------------|
| arytmetyczne| `+`  `-`  `*`  `/`  `%`               |
| porównania  | `==` `!=` `<` `>` `<=` `>=`           |
| przypisanie | `=`                                   |
| grupowanie  | `(`  `)`  `{`  `}`                    |
| separator   | `,`                                   |

### Pomijane

| Token         | Wzorzec             | Akcja    |
|---------------|---------------------|----------|
| `WS`          | `[ \t\r\n]+`        | pomijany |
| `CPP_COMMENT` | `//[^\n]*`          | pomijany |
| `C_COMMENT`   | `/* ... */`         | pomijany |

---

## Gramatyka

Pełna definicja gramatyki znajduje się w pliku [[grammar.lark](cci:7://file:///home/blaze/PycharmProjects/Teoria-Kompilacji-i-Kompilatory/DrawLang/grammar.lark:0:0-0:0)](grammar.lark).
W skrócie obejmuje ona:

* deklaracje zmiennych (`let`) oraz przypisania,
* instrukcje sterujące: `if/else`, `while`, `for ... to ... step`, `repeat`, `break`, `continue`,
* deklaracje i wywołania procedur (`proc`, `return`),
* instrukcje rysujące (`canvas`, `circle`, `line`, `rect`, `color`, `translate`, `scale`),
* wyrażenia z podziałem na arytmetyczne (`+ - * / %`) i logiczne (`and or not`, porównania),
* priorytety operatorów i grupowanie,
* bloki `{ ... }` zawierające dowolny ciąg instrukcji.

---

## Etapy przetwarzania

1. Analiza leksykalna (tokenizacja).
2. Analiza składniowa (parser Lark).
3. Budowa wewnętrznej reprezentacji (model sceny).
4. Interpretacja instrukcji.
5. Generowanie wyjściowego pliku SVG.

---

## Przykłady

### Przykład 1

Wejście:

```
canvas 200 200
circle 100 100 50
```

Wynik:

* okrąg umieszczony na środku płótna.

---

### Przykład 2

Wejście:

```
canvas 300 300
color blue
rect 50 50 200 100
line 0 0 300 300
```

Dodatkowe, bardziej rozbudowane przykłady znajdują się w katalogu [`examples/`](examples).

---

## Wymagania funkcjonalne

* parsowanie programów napisanych w DrawLang,
* obsługa podstawowych kształtów,
* generowanie poprawnego pliku SVG,
* obsługa kolorów.

---

## Wymagania niefunkcjonalne

* czytelny i uporządkowany kod,
* modularna architektura,
* łatwa rozszerzalność,
* kompletna dokumentacja w repozytorium.

---

## Możliwe rozszerzenia

* eksport do PNG (np. z użyciem Pillow),
* grupowanie elementów,
* animacje SVG,
* dodatkowe prymitywy (elipsa, wielokąt, krzywe Béziera).

---

## Struktura projektu

```
DrawLang/
├── examples/
│   ├── advanced.draw
│   └── test.draw
├── .gitignore
├── grammar.lark
├── main.py
├── README.md
└── requirements.txt
```

* `grammar.lark` – definicja gramatyki języka DrawLang dla parsera Lark.
* `main.py` – punkt wejścia: wczytuje plik `.draw`, buduje drzewo składniowe i generuje SVG (lub wypisuje AST).
* `examples/` – przykładowe programy w DrawLang (`test.draw`, `advanced.draw`).
* `requirements.txt` – lista zależności Pythona.

---

## Wartość projektu

Projekt pokazuje:

* tworzenie własnego języka dziedzinowego (DSL),
* praktyczne wykorzystanie generatora parserów,
* transformację: tekst → grafika.

---

## Instalacja

1. Sklonowanie repozytorium:

   ```bash
   git clone <adres-repozytorium>
   cd DrawLang
   ```

2. Utworzenie i aktywacja środowiska wirtualnego:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Instalacja zależności:

   ```bash
   pip install -r requirements.txt
   ```

---

## Uruchomienie

Generowanie pliku SVG na podstawie programu w DrawLang:

```bash
python main.py examples/test.draw
```

Wynik zostanie zapisany obok pliku wejściowego (np. `examples/test.svg`).

Podgląd drzewa składniowego (AST) zamiast generowania SVG:

```bash
python main.py examples/test.draw --ast
```

---
