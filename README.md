# COBOL Editor

Edytor COBOL z podświetlaniem składni i funkcją wyszukiwania napisany w Pythonie.

## Funkcje

- **Podświetlanie składni COBOL**: Automatyczne kolorowanie słów kluczowych, komentarzy, stringów, liczb i sekcji
- **Wyszukiwanie tekstu**: Funkcja Find (Ctrl+F) z możliwością wyszukiwania kolejnych wystąpień (F3)
- **Numeracja linii**: Automatyczna numeracja linii po lewej stronie
- **Operacje na plikach**: New, Open, Save, Save As
- **Skróty klawiszowe**: Szybki dostęp do podstawowych funkcji

## Wymagania

- Python 3.x
- tkinter (zwykle zainstalowany domyślnie z Pythonem)

## Instalacja

Sklonuj repozytorium:
```bash
git clone <repository-url>
cd pluginCobol
```

## Uruchamianie

```bash
python3 cobol_editor.py
```

lub nadaj uprawnienia wykonywalne i uruchom bezpośrednio:
```bash
chmod +x cobol_editor.py
./cobol_editor.py
```

## Użytkowanie

### Menu

**File**
- **New (Ctrl+N)**: Utwórz nowy plik
- **Open (Ctrl+O)**: Otwórz istniejący plik COBOL
- **Save (Ctrl+S)**: Zapisz aktualny plik
- **Save As**: Zapisz plik pod nową nazwą
- **Exit**: Zamknij edytor

**Edit**
- **Find (Ctrl+F)**: Wyszukaj tekst w pliku
- **Find Next (F3)**: Znajdź następne wystąpienie
- **Select All (Ctrl+A)**: Zaznacz cały tekst

**Help**
- **About**: Informacje o programie

### Skróty klawiszowe

| Skrót | Akcja |
|-------|-------|
| Ctrl+N | Nowy plik |
| Ctrl+O | Otwórz plik |
| Ctrl+S | Zapisz plik |
| Ctrl+F | Wyszukaj |
| F3 | Znajdź następne |
| Ctrl+A | Zaznacz wszystko |

### Podświetlanie składni

Edytor rozpoznaje i koloruje:
- **Słowa kluczowe COBOL**: ACCEPT, MOVE, PERFORM, IF, etc. (niebieski, pogrubiony)
- **Dywizyje**: IDENTIFICATION, ENVIRONMENT, DATA, PROCEDURE (fioletowy, pogrubiony)
- **Sekcje**: WORKING-STORAGE, FILE-CONTROL, etc. (fioletowy)
- **Typy danych**: PIC X(10), PIC 9(5)V99, etc. (turkusowy)
- **Komentarze**: Linie zaczynające się od * (zielony, kursywa)
- **Stringi**: Tekst w cudzysłowach (czerwony)
- **Liczby**: Wartości numeryczne (zielony)

### Wyszukiwanie

1. Naciśnij **Ctrl+F** lub wybierz **Edit > Find**
2. Wpisz szukany tekst w oknie dialogowym
3. Naciśnij **F3** lub wybierz **Edit > Find Next**, aby znaleźć kolejne wystąpienia
4. Wyszukiwanie nie rozróżnia wielkości liter
5. Po dotarciu do końca pliku wyszukiwanie zaczyna się od początku

## Przykładowy plik COBOL

W repozytorium znajduje się przykładowy plik `example.cbl` do testowania edytora.

## Struktura projektu

```
pluginCobol/
├── cobol_editor.py    # Główny plik edytora
├── example.cbl        # Przykładowy plik COBOL
└── README.md          # Ta dokumentacja
```

## Licencja

Ten projekt jest dostępny na licencji MIT.

## Autor

Stworzony przy użyciu Claude Code
