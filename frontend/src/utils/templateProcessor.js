/**
 * Template processor: transforms a template's pdf_definition with form data.
 * Replaces {{placeholder}} and {{placeholder|filter}} syntax.
 */

/**
 * Format a date to German locale (DD.MM.YYYY)
 */
export function formatDateDE(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

/**
 * Add days to a date (skips weekends is not implemented yet, simple add)
 */
export function calculatePaymentDeadline(rechnungseingang, rechnungsart) {
  if (!rechnungseingang) return '';
  const date = new Date(rechnungseingang);
  const daysToAdd = rechnungsart === 'Schlussrechnung' ? 29 : 20;
  date.setDate(date.getDate() + daysToAdd);
  return date.toISOString().split('T')[0];
}

/**
 * Get the display text for invoice type
 */
export function getInvoiceTypeText(formData) {
  if (formData.M_zUo9 === 'Abschlagsrechnung' && formData.E_3aZx) {
    return `${formData.E_3aZx}. Abschlagsrechnung`;
  }
  return formData.M_zUo9 || '';
}

/**
 * Process a template's pdf_definition with form data.
 * Replaces {{fieldCode}} and {{fieldCode|filter}} placeholders.
 */
export function processTemplate(pdfDefinition, formData, templateId) {
  // Deep clone the pdf definition
  const processed = JSON.parse(JSON.stringify(pdfDefinition));

  // Pre-calculate special computed fields
  const computed = {
    paymentDeadline: calculatePaymentDeadline(formData.I_5jBb, formData.M_zUo9),
    invoiceTypeDisplayText: getInvoiceTypeText(formData),
  };

  // Recursively replace placeholders
  _replacePlaceholders(processed, formData, computed);

  return processed;
}

/**
 * Recursively walk the object and replace {{placeholder}} syntax.
 */
function _replacePlaceholders(obj, formData, computed) {
  if (typeof obj === 'string') {
    return _replacePlaceholdersInString(obj, formData, computed);
  } else if (Array.isArray(obj)) {
    for (let i = 0; i < obj.length; i++) {
      if (typeof obj[i] === 'string') {
        obj[i] = _replacePlaceholdersInString(obj[i], formData, computed);
      } else if (obj[i] !== null && typeof obj[i] === 'object') {
        _replacePlaceholders(obj[i], formData, computed);
      }
    }
  } else if (obj !== null && typeof obj === 'object') {
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        if (typeof obj[key] === 'string') {
          obj[key] = _replacePlaceholdersInString(obj[key], formData, computed);
        } else if (obj[key] !== null && typeof obj[key] === 'object') {
          _replacePlaceholders(obj[key], formData, computed);
        }
      }
    }
  }
  return obj;
}

/**
 * Replace {{placeholder}} and {{placeholder|filter}} in a string.
 */
function _replacePlaceholdersInString(str, formData, computed) {
  if (typeof str !== 'string') return str;

  return str.replace(/\{\{([a-zA-Z_][a-zA-Z0-9_]*)(?:\|([a-zA-Z]+))?\}\}/g, (match, fieldCode, filter) => {
    // Check computed fields first
    if (computed.hasOwnProperty(fieldCode)) {
      const value = computed[fieldCode];
      return _applyFilter(value, filter);
    }

    // Check form data
    const value = formData[fieldCode];
    if (value === undefined || value === null || value === '') {
      return '';
    }

    return _applyFilter(value, filter);
  });
}

/**
 * Apply a filter to a value.
 */
function _applyFilter(value, filter) {
  if (!filter) return String(value);

  switch (filter) {
    case 'dateDE':
      return formatDateDE(value);
    default:
      return String(value);
  }
}
