"""
Hardcoded field definitions for all available form fields.
Each field is defined once here with its metadata (label, placeholder, type, etc).
Templates then just reference the field codes.
"""

FIELD_DEFINITIONS = {
    # Arbeiten & Aufträge
    "A_X5hX": {
        "label": "Arbeiten",
        "type": "text",
        "placeholder": "Beschreibung der Arbeiten",
        "required": True,
    },
    "B_OS9q": {
        "label": "Auftragsnummer",
        "type": "text",
        "placeholder": "z.B. 2024-001",
        "required": True,
    },
    "C_2MWd": {
        "label": "Auftragsdatum",
        "type": "date",
        "required": True,
    },
    "D_G8pr": {
        "label": "Gewerk Mit DIN",
        "type": "text",
        "placeholder": "z.B. DIN 276-1:2008-12",
        "required": True,
    },
    
    # Abschlagrechnung specific
    "E_3aZx": {
        "label": "Wievielte Abschlagsrechnung",
        "type": "number",
        "min": 1,
        "placeholder": "z.B. 1, 2, 3...",
        "required": True,
        "condition": {"field": "M_zUo9", "equals": "Abschlagsrechnung"},
    },
    
    # Rechnung
    "F_zc2N": {
        "label": "Rechnungsnummer",
        "type": "text",
        "placeholder": "z.B. RE-2024-001",
        "required": True,
    },
    "G_tQ7N": {
        "label": "Rechnungsdatum",
        "type": "date",
        "required": True,
    },
    "H_pe6V": {
        "label": "Aktuelles Datum (Manuell Einstellbar)",
        "type": "date",
        "defaultValue": "today",
        "required": True,
    },
    "I_5jBb": {
        "label": "Rechnungseingang",
        "type": "date",
        "helpText": "Datum eingeben",
        "showCalculation": True,
        "required": True,
    },
    
    # Firmendaten
    "J_knG9": {
        "label": "Firmenname",
        "type": "text",
        "placeholder": "Name des Unternehmens",
        "required": True,
    },
    "K_EQ0i": {
        "label": "Straße und Hausnummer der Firma",
        "type": "text",
        "placeholder": "z.B. Musterstraße 123",
        "required": True,
    },
    "L_YO8o": {
        "label": "PLZ und Stadt der Firma",
        "type": "text",
        "placeholder": "z.B. 12345 Musterstadt",
        "required": True,
    },
    
    # Rechnungsart
    "M_zUo9": {
        "label": "Rechnungsart",
        "type": "select",
        "options": ["Abschlagsrechnung", "Schlussrechnung"],
        "required": True,
    },
    
    # BAB Reference (required for MPG template)
    "N_jqA8": {
        "label": "BAB HWP",
        "type": "text",
        "placeholder": "BAB Referenz",
        "required": True,
    },
    
    # Unterschrift & Projekt
    "O_a1Pi": {
        "label": "Name (Unterschrift)",
        "type": "text",
        "placeholder": "Name des Unterzeichners",
        "required": True,
    },
    "P_C2ng": {
        "label": "Projekt",
        "type": "text",
        "placeholder": "Projektname",
        "required": True,
    },
    "Q_h8nI": {
        "label": "Betrifft",
        "type": "text",
        "placeholder": "Betreff der Korrespondenz",
        "required": True,
    },
}


def get_field_definition(field_code: str) -> dict:
    """Get the definition for a field by its code."""
    return FIELD_DEFINITIONS.get(field_code)


def build_field_config_from_codes(field_codes: list) -> list:
    """
    Build a complete field_config array by looking up codes in FIELD_DEFINITIONS.
    
    Args:
        field_codes: List of field codes like ["A_X5hX", "B_OS9q", ...]
        
    Returns:
        List of enriched field definitions with code included
    """
    field_config = []
    for code in field_codes:
        definition = get_field_definition(code)
        if definition:
            field_config.append({"code": code, **definition})
        else:
            raise ValueError(f"Unknown field code: {code}")
    return field_config
