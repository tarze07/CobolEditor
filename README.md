# COBOL Editor

Edytor COBOL z podświetlaniem składni, wyszukiwaniem w wielu plikach i regulacją wielkości czcionki napisany w Pythonie z wykorzystaniem PySide6 (Qt).

## Funkcje

- **Drzewo katalogów roboczych**: Przeglądarka katalogów w stylu Sublime Text - wybierz katalog roboczy i przeglądaj pliki w drzewie
- **Podświetlanie składni COBOL**: Automatyczne kolorowanie słów kluczowych, komentarzy, stringów, liczb i sekcji
- **Wyszukiwanie tekstu**: Funkcja Find (Ctrl+F) z możliwością wyszukiwania kolejnych wystąpień (F3)
- **Wyszukiwanie w wielu plikach**: Funkcja Find in Files (Ctrl+Shift+F) pozwala wyszukiwać w wielu plikach COBOL jednocześnie
- **Regulacja wielkości czcionki**: Możliwość powiększania (Ctrl++) i pomniejszania (Ctrl+-) czcionki
- **Motywy kolorystyczne**: 4 dostępne motywy (Light, Dark, High Contrast, Monokai)
- **Numeracja linii**: Automatyczna numeracja linii po lewej stronie
- **Operacje na plikach**: New, Open, Save, Save As
- **Skróty klawiszowe**: Szybki dostęp do podstawowych funkcji

## Wymagania

- Python 3.8 lub nowszy
- PySide6

## Instalacja

Sklonuj repozytorium:
```bash
git clone <repository-url>
cd CobolEditor
```

Zainstaluj wymagane zależności:
```bash
pip install -r requirements.txt
```

lub bezpośrednio:
```bash
pip install PySide6
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
- **Select Working Directory**: Wybierz katalog roboczy do przeglądania w drzewie
- **Exit**: Zamknij edytor

**Edit**
- **Find (Ctrl+F)**: Wyszukaj tekst w bieżącym pliku
- **Find Next (F3)**: Znajdź następne wystąpienie
- **Find in Files (Ctrl+Shift+F)**: Wyszukaj tekst w wielu plikach COBOL
- **Select All (Ctrl+A)**: Zaznacz cały tekst

**View**
- **Theme**: Wybierz motyw kolorystyczny (Light, Dark, High Contrast, Monokai)
- **Increase Font Size (Ctrl++)**: Powiększ czcionkę
- **Decrease Font Size (Ctrl+-)**: Pomniejsz czcionkę
- **Reset Font Size**: Przywróć domyślny rozmiar czcionki

**Help**
- **About**: Informacje o programie

### Skróty klawiszowe

| Skrót | Akcja |
|-------|-------|
| Ctrl+N | Nowy plik |
| Ctrl+O | Otwórz plik |
| Ctrl+S | Zapisz plik |
| Ctrl+F | Wyszukaj w pliku |
| F3 | Znajdź następne |
| Ctrl+Shift+F | Wyszukaj w wielu plikach |
| Ctrl++ | Powiększ czcionkę |
| Ctrl+- | Pomniejsz czcionkę |
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

### Drzewo katalogów roboczych

Edytor posiada panel boczny z drzewem katalogów (podobny do Sublime Text):

1. Wybierz **File > Select Working Directory** lub użyj ikony w menu
2. Wybierz katalog, który chcesz przeglądać
3. Drzewo katalogów pojawi się po lewej stronie edytora
4. Katalogi oznaczone są ikoną 📁
5. Pliki COBOL (.cbl, .cob, .cobol) oznaczone są ikoną 📄
6. Inne pliki oznaczone są ikoną 📋
7. **Kliknij dwukrotnie** na plik, aby go otworzyć w edytorze
8. Drzewo automatycznie sortuje katalogi przed plikami
9. Ukryte pliki i katalogi (zaczynające się od .) są pomijane
10. Panel drzewa dostosowuje się do aktualnego motywu kolorystycznego

### Wyszukiwanie

**Wyszukiwanie w bieżącym pliku:**
1. Naciśnij **Ctrl+F** lub wybierz **Edit > Find**
2. Wpisz szukany tekst w oknie dialogowym
3. Naciśnij **F3** lub wybierz **Edit > Find Next**, aby znaleźć kolejne wystąpienia
4. Wyszukiwanie nie rozróżnia wielkości liter
5. Po dotarciu do końca pliku wyszukiwanie zaczyna się od początku

**Wyszukiwanie w wielu plikach:**
1. Naciśnij **Ctrl+Shift+F** lub wybierz **Edit > Find in Files**
2. Wybierz katalog, w którym chcesz wyszukać
3. Wpisz szukany tekst w oknie dialogowym
4. Wyniki pojawią się w nowym oknie z listą wszystkich dopasowań
5. Kliknij dwukrotnie na wynik, aby otworzyć plik i przejść do odpowiedniej linii
6. Wyszukiwanie dotyczy plików z rozszerzeniami: .cbl, .cob, .cobol

### Regulacja wielkości czcionki

1. **Powiększanie**: Naciśnij **Ctrl++** lub wybierz **View > Increase Font Size**
2. **Pomniejszanie**: Naciśnij **Ctrl+-** lub wybierz **View > Decrease Font Size**
3. **Reset**: Wybierz **View > Reset Font Size**, aby przywrócić domyślny rozmiar (11)
4. Zakres wielkości czcionki: 6-72 punktów
5. Zmiana wielkości czcionki aktualizuje podświetlanie składni

## Przykładowy plik COBOL

W repozytorium znajduje się przykładowy plik `example.cbl` do testowania edytora.

## Struktura projektu

```
CobolEditor/
├── cobol_editor.py    # Główny plik edytora
├── example.cbl        # Przykładowy plik COBOL
├── requirements.txt   # Zależności projektu
└── README.md          # Ta dokumentacja
```

## Licencja

Ten projekt jest dostępny na licencji MIT.

## Autor

Stworzony przy użyciu Claude Code
