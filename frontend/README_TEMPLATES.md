# Templates Structure

This project supports multiple document templates. Each template is stored in its own folder with a consistent structure.

## Folder Structure

```
src/
├── templates/
│   ├── index.js                          # Central export for all templates
│   ├── shared/                           # Shared components (headers, footers, utils)
│   │   └── (common files go here)
│   └── anschreiben_gewerk/              # Individual template folder
│       ├── index.js                      # Template exports
│       ├── template_anschreiben_gewerk.js # PDF template definition
│       └── fieldConfig.js                # Field configuration and helpers
├── assets/                               # Images, logos, etc.
└── App.js                                # Main application

```

## Adding a New Template

1. Create a new folder in `src/templates/` with your template name
2. Create the following files:
   - `template_[name].js` - PDF template definition
   - `fieldConfig.js` - Form field configuration
   - `index.js` - Export the template functions

3. Add the template to `src/templates/index.js`

4. Update `App.js` to support template selection if needed

## Template File Structure

### `fieldConfig.js`
Defines the form fields for the template:
```javascript
export const fieldConfig = [
  {
    code: 'FIELD_CODE',
    label: 'Field Label',
    type: 'text|number|date|select',
    required: true,
    // ... other properties
  },
];
```

### `template_[name].js`
Defines the PDF layout using pdfmake:
```javascript
export const createPdfTemplate = (data) => {
  return {
    pageSize: 'A4',
    content: [
      // PDF content here
    ],
  };
};
```

## Shared Resources

Place shared items in:
- `src/templates/shared/` - Reusable template components
- `src/assets/` - Images, logos, fonts
