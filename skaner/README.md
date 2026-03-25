# Skaner i kolorowanie składni (HTML)

Projekt implementuje skaner (lexer) dla uproszczonego języka programowania i generuje pokolorowany kod jako plik HTML.

## Założony format wejściowy

Uproszczony język C-podobny:
- słowa kluczowe: `if`, `else`, `while`, `for`, `return`, `int`, `float`, `bool`, `true`, `false`, `void`, `function`, `var`
- identyfikatory: litera lub `_`, dalej litery/cyfry/`_`
- liczby: całkowite i zmiennoprzecinkowe (np. `12`, `3.14`)
- napisy: cudzysłowy `"..."`, obsługa sekwencji `\`
- komentarze: `// ...` oraz `/* ... */`
- operatory: `+ - * / % = == != < <= > >= && || !`
- delimitery: `() {} [] ; , . :`

## Tabela tokenów

| Token | Opis | Przykłady |
|---|---|---|
| `KEYWORD` | słowa kluczowe języka | `if`, `return`, `int` |
| `IDENTIFIER` | nazwy zmiennych/funkcji | `x`, `licznik_1`, `main` |
| `NUMBER` | liczby całkowite i float | `42`, `10.5` |
| `STRING` | literały tekstowe | `"Ala ma kota"` |
| `COMMENT` | komentarze jedno- i wieloliniowe | `// opis`, `/* opis */` |
| `OPERATOR` | operatory arytm./log./por. | `+`, `==`, `&&`, `!` |
| `DELIMITER` | nawiasy i separatory | `(`, `)`, `{`, `;`, `,` |
| `WHITESPACE` | białe znaki (zachowanie układu) | spacja, tab, nowa linia |
| `UNKNOWN` | nieznany znak/niezamknięty token | np. samotny znak spoza alfabetu |

## Diagram przejść (DFA, uproszczony)

```mermaid
flowchart TD
	S([START]) -->|biały znak| WS[WHITESPACE]
	S -->|litera/_| ID[IDENTIFIER/KEYWORD]
	S -->|cyfra| NUM[NUMBER]
	S -->|"| STR[STRING]
	S -->|/| SLASH{next}
	S -->|operator| OP[OPERATOR]
	S -->|delimiter| DEL[DELIMITER]
	S -->|inny znak| UNK[UNKNOWN]

	ID -->|litera/cyfra/_| ID
	ID --> E([EMIT])

	NUM -->|cyfra| NUM
	NUM -->|. + cyfra| NUMF[NUMBER_FLOAT]
	NUMF -->|cyfra| NUMF
	NUM --> E
	NUMF --> E

	STR -->|\\ + dowolny| STR
	STR -->|"| E
	STR -->|EOF| UNK

	SLASH -->|/| C1[LINE_COMMENT]
	SLASH -->|*| C2[BLOCK_COMMENT]
	SLASH -->|inne| OP

	C1 -->|do \n| C1
	C1 --> E

	C2 -->|dowolny znak| C2
	C2 -->|*/| E
	C2 -->|EOF| UNK

	WS -->|biały znak| WS
	WS --> E

	OP --> E
	DEL --> E
	UNK --> E
```

## Działanie programu

Program:
1. wczytuje cały plik wejściowy,
2. tokenizuje tekst zgodnie z tabelą tokenów,
3. zapisuje wynik do pliku HTML,
4. zachowuje układ tekstu z wejścia (spacje/taby/nowe linie) przez render w `<pre>`.

## Uruchomienie

Po zbudowaniu uruchom:

```bash
./build/Debug/skaner.exe <plik_wejsciowy> <plik_wyjsciowy_html>
```

Przykład:

```bash
./build/Debug/skaner.exe input.txt output.html
```

Następnie otwórz `output.html` w przeglądarce.