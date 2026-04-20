# Przewodnik testowania skanera

## Plik testowe

Przygotowałem 3 pliki testowe w folderze `examples/`:

1. **simple.txt** — minimalny kod testujący słowa kluczowe, identyfikatory, komentarze i operatory
2. **full_syntax.txt** — kompleksowy kod ze wszystkimi typami tokenów: liczby, stringi, komentarze multi-line, operatory
3. **edge_cases.txt** — przypadki brzegowe: liczby zmiennoprzecinkowe, escape-quoteы, identyfikatory ze znakami specjalnymi

## Uruchomienie testów

Z folderu głównego projektu:

```bash
mkdir -p examples/outputs

./build/Debug/skaner.exe examples/simple.txt examples/outputs/simple.html
./build/Debug/skaner.exe examples/full_syntax.txt examples/outputs/full_syntax.html
./build/Debug/skaner.exe examples/edge_cases.txt examples/outputs/edge_cases.html
```

## Weryfikacja wyników

Wygenerowane pliki HTML w `examples/outputs/` otwórz przeglądarką (dwuklik lub drag-drop do przeglądarki).

Sprawdzaj:
- **Słowa kluczowe** (if, while, function, return, int, float, var, bool, true, false) → _granatowy, pogrubiony_
- **Identyfikatory** (nazwy zmiennych, funkcji) → _jasnoniebieskie_
- **Liczby** (42, 3.14, 0.001) → _bladozielone_
- **Stringi** ("...") → _popielate_
- **Komentarze** (// i /* */) → _zielone, pochylone_
- **Operatory** (+, -, ==, !=, <=, >=, &&, ||) → _szare_
- **Delimitery** ((, ), {, }, [, ], ;, ,, .) → _żółte_
- **Białe znaki** (spacje, taby, nowe linie) → _zachane bez zmian_
- **Układ tekstu** → _dokładnie taki sam jak w pliku wejściowym_

## Checklist testowy

- [ ] Kolorowanie działa w przeglądarce
- [ ] Wszystkie typy tokenów są różnymi kolorami
- [ ] Układ tekstu (wcięcia, nowe linie) jest zachowany
- [ ] HTML jest poprawnie sformułowany i ładuje się bez błędów
- [ ] Stringi z escape-sequencami są obsługiwane
- [ ] Komentarze wieloliniowe są prawidłowo zamykane
- [ ] Operatory dwuznakowe (==, !=, <=, >=, &&, ||) są traktowani jako jeden token

## Testowanie niestandardowych danych

Możesz stworzyć własny plik testowy:

```bash
cat > examples/custom.txt <<EOF
function test() {
    var x = 100;
    // Twój kod od tutaj
}
EOF

./build/Debug/skaner.exe examples/custom.txt examples/outputs/custom.html
```

Następnie otwórz `examples/outputs/custom.html` w przeglądarce i sprawdź wyniki.
