# Template Erstellung & Upload-Anleitung

## Überblick

AutoDoc speichert alle Templates als JSON-Dateien in der Datenbank. Templates definieren die Struktur des Formulars (Felder) und das PDF-Layout (Layout). Sie können eigene Templates erstellen und über die Benutzeroberfläche hochladen.

## Template-Struktur

Ein Template ist eine JSON-Datei mit folgender Struktur:

```json
{
  "id": "mein_template",
  "name": "Mein Template",
  "description": "Kurzbeschreibung des Templates",
  "field_config": [...],
  "pdf_definition": {...}
}
```

### 1. `id` (String, erforderlich)
Eine eindeutige Kennung für das Template (keine Leerzeichen, nur lowercase und `_`).

**Beispiel:** `"rechnungsschreiben"`, `"angebot_vorlage"`

---

### 2. `name` (String, erforderlich)
Der Anzeigename des Templates in der Benutzeroberfläche.

**Beispiel:** `"Rechnungsschreiben"`

---

### 3. `description` (String, optional)
Eine längere Beschreibung, was dieses Template macht.

---

## `field_config` – Formularfelder definieren

Das `field_config` ist ein Array von Feldern, die in der Benutzeroberfläche angezeigt werden.

### Feld-Struktur

```json
{
  "code": "eindeutige_feldkennung",
  "label": "Anzeigetext für das Label",
  "type": "text|number|date|select",
  "placeholder": "Hilfetext im Input",
  "required": true|false,
  "defaultValue": "einmalige_standardwert",
  "condition": {"field": "andere_feldkennung", "equals": "wert"},
  "options": ["Wert1", "Wert2"],
  "min": 1,
  "helpText": "Zusätzliche Hilfe unterhalb des Labels",
  "calculated": true,
  "showCalculation": true
}
```

### Feld-Attribute

| Attribut | Typ | Beschreibung |
|----------|-----|-------------|
| `code` | String | Eindeutige Kennung des Feldes (verwendet in PDF-Template) |
| `label` | String | Beschriftung des Feldes in der Benutzeroberfläche |
| `type` | String | `text`, `number`, `date`, oder `select` |
| `placeholder` | String | Platzhaltertext im Eingabefeld |
| `required` | Boolean | Ist das Feld erforderlich? (Standard: `false`) |
| `defaultValue` | String/Number | Standardwert beim Laden; `"today"` aktiviert das heutige Datum |
| `condition` | Object | Zeige dieses Feld nur wenn: `{"field": "CODE", "equals": "WERT"}` |
| `options` | Array | Für `type: "select"` – Array von Auswahloptionen |
| `min` | Number | Für `type: "number"` – Mindestwert |
| `helpText` | String | Zusätzliche Hilfe unterhalb des Labels |
| `calculated` | Boolean | Feld ist nur Anzeige (nicht editierbar) |
| `showCalculation` | Boolean | Zeige berechneten Wert im Help-Text |

### Beispiel-Felder

```json
[
  {
    "code": "A_X5hX",
    "label": "Arbeiten",
    "type": "text",
    "placeholder": "Beschreibung der Arbeiten",
    "required": true
  },
  {
    "code": "B_OS9q",
    "label": "Auftragsnummer",
    "type": "text",
    "placeholder": "z.B. 2024-001",
    "required": true
  },
  {
    "code": "C_2MWd",
    "label": "Auftragsdatum",
    "type": "date",
    "required": true
  },
  {
    "code": "M_zUo9",
    "label": "Rechnungsart",
    "type": "select",
    "options": ["Abschlagsrechnung", "Schlussrechnung"],
    "required": true
  },
  {
    "code": "E_3aZx",
    "label": "Wievielte Abschlagsrechnung",
    "type": "number",
    "min": 1,
    "required": true,
    "condition": {"field": "M_zUo9", "equals": "Abschlagsrechnung"}
  }
]
```

---

## `pdf_definition` – PDF-Layout definieren

Das `pdf_definition` ist das pdfMake-Format für das PDF-Dokument-Layout. Es definiert Seitenmaße, Header/Footer, Schriftarten, Abstände und Inhalte.

### Platzhalter-Syntax

Feldwerte werden automatisch in das PDF eingefügt, indem Sie `{{feldcode}}` verwenden:

```json
{
  "text": "Name: {{J_knG9}}"
}
```

### Filter

Sie können Feldwerte mit Filtern formatieren: `{{feldcode|filtername}}`

**Verfügbare Filter:**

| Filter | Beschreibung | Beispiel |
|--------|-------------|---------|
| `dateDE` | Datums-Format (DD.MM.YYYY) | `{{C_2MWd\|dateDE}}` → `31.12.2024` |

### Besondere Platzhalter

Einige Platzhalter werden automatisch berechnet:

| Platzhalter | Beschreibung |
|-------------|-------------|
| `{{paymentDeadline\|dateDE}}` | Zahlungsfrist (20 oder 29 Tage nach Rechnungseingang, abhängig von Rechnungsart) |
| `{{invoiceTypeDisplayText}}` | Text für die Rechnungsart ("Abschlagsrechnung" oder "Schlussrechnung") |

### Grundstruktur

```json
{
  "pageSize": "A4",
  "pageMargins": [40, 40, 40, 40],
  "header": {...},
  "footer": {...},
  "content": [...]
}
```

### Header & Footer mit Bildern

```json
"header": {
  "image": "headerImage",
  "width": 595.28,
  "alignment": "center",
  "margin": [0, 0, 0, 0]
}
```

**Verfügbare Bilder:**
- `"headerImage"` – Kopfzeilenbild (aus `backend/template_data/header.png`)
- `"footerImage"` – Fußzeilenbild (aus `backend/template_data/footer.png`)

### Content-Elemente

#### Text

```json
{
  "text": "Dies ist normaler Text",
  "fontSize": 12,
  "bold": true,
  "italics": false,
  "margin": [0, 0, 0, 10]
}
```

#### Mehrspaltig (Columns)

```json
{
  "columns": [
    {"width": 100, "text": "Spalte 1"},
    {"width": "*", "text": "Spalte 2 (flexible Breite)"}
  ],
  "margin": [0, 0, 0, 10]
}
```

#### Abstände

```json
{"text": " ", "margin": [0, 0, 0, 20]}
```

### Beispiel-PDF-Definition

```json
{
  "pageSize": "A4",
  "pageMargins": [40, 150, 40, 60],
  "header": {
    "image": "headerImage",
    "width": 595.28,
    "alignment": "center",
    "margin": [0, 0, 0, 0]
  },
  "footer": {
    "image": "footerImage",
    "width": 595.28,
    "alignment": "center",
    "margin": [0, 0, 0, 0]
  },
  "content": [
    {"text": "Firma: {{J_knG9}}", "fontSize": 11, "bold": true},
    {"text": "Auftrag: {{B_OS9q}}", "fontSize": 10},
    {"text": "Datum: {{C_2MWd|dateDE}}", "fontSize": 10},
    {"text": " ", "margin": [0, 0, 0, 20]},
    {"text": "Sehr geehrte Damen und Herren,", "fontSize": 10},
    {"text": "anbei erhalten Sie Ihre Rechnung.", "fontSize": 10, "margin": [0, 0, 0, 20]},
    {"text": "Mit freundlichen Grüßen", "fontSize": 10}
  ]
}
```

---

## Beispiel-Datei nutzen

Verwenden Sie die bereitgestellte Beispiel-Template-Datei als Vorlage:

📄 **`backend/template_data/anschreiben_gewerk_template.json`**

Diese Datei können Sie als Basis für eigene Templates kopieren und anpassen.

---

## Template hochladen

1. **Template-JSON erstellen** (oder eine bestehende Datei kopieren und anpassen)
2. **In der Benutzeroberfläche navigieren:**
   - Linke Sidebar → Abschnitt "Templates"
   - Klick auf "+ Template hochladen"
3. **JSON-Datei auswählen** und hochladen
4. Das Template erscheint sofort in der Templates-Liste

---

## Best Practices

### Feldcodes
- Verwenden Sie kurze, eindeutige Codes (z.B. `A_X5hX`, `B_OS9q`)
- Notieren Sie sich alle Codes – diese werden in `pdf_definition` verwendet

### Bedingte Felder
Wenn ein Feld nur unter bestimmten Bedingungen angezeigt werden soll:

```json
{
  "code": "E_3aZx",
  "label": "Wievielte Abschlagsrechnung",
  "type": "number",
  "condition": {"field": "M_zUo9", "equals": "Abschlagsrechnung"}
}
```

Dieses Feld wird nur angezeigt, wenn das Feld `M_zUo9` den Wert `"Abschlagsrechnung"` hat.

### Datumsformatierung
- Alle Datumsfelder sollten `"type": "date"` verwenden
- Im PDF müssen Sie den Filter `|dateDE` verwenden: `{{C_2MWd|dateDE}}`

### Erforderliche Felder
Markieren Sie wichtige Felder mit `"required": true`. Sie werden in der Benutzeroberfläche mit einem roten Stern `*` gekennzeichnet.

---

## Fehlerbehandlung

Wenn das Template nicht hochgeladen werden kann:

1. **JSON-Format prüfen** – Alle `"` müssen correct sein, keine trailing commas
2. **Eindeutige Template-ID** – Stelle sicher, dass die `id` nicht bereits existiert
3. **Feldcodes konsistent** – Alle Feldcodes in `pdf_definition` müssen in `field_config` definiert sein

Sie können Ihre JSON-Datei mit einem Online-Tool wie [jsonlint.com](https://jsonlint.com/) validieren.

---

## Weitere Ressourcen

- **pdfMake Dokumentation:** https://pdfmake.github.io/docs/0.3/

Für Fragen zur Entwicklung eigener Templates, schauen Sie sich `backend/template_data/anschreiben_gewerk_template.json` als Beispiel an.
