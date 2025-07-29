# OARepo Citations

A citation management extension for OARepo that provides comprehensive citation functionality for academic records. This package enables users to generate and export citations in multiple academic formats directly from record detail pages.

## Installation

Install the package using pip:

```bash
pip install oarepo-citations
```

## Usage

### Basic Integration

Once installed, the citation functionality is automatically available on record detail pages. The package provides:

1. **Citation Dropdown Component**: A compact dropdown selector for citation styles
2. **Citation Modal Component**: An expanded modal view for detailed citation information

### Configuration & Integration

To customize the citation styles and default style, update the configuration settings in your `invenio.cfg` or equivalent configuration file:

```python
CITATION_STYLES = [
    { "style": "iso690-author-date-cs", "label": _("ČSN ISO 690") },
    { "style": "bibtex", "label": _("BibTeX") }
]
CITATION_STYLES_DEFAULT = "iso690-author-date-cs"
```

Include citations in your record JinjaX templates:

```jsx
<RecordCitations record={record} styles={config.get("CITATION_STYLES")} defaultStyle={config.get("CITATION_STYLES_DEFAULT")} />
```

#### Supported Citation Styles
The package supports various citation styles, including but not limited to:
- `{ "style": "iso690-author-date-cs", "label": "ČSN ISO 690" }`
- `{ "style": "apa", "label": "APA" }`
- `{ "style": "harvard-cite-them-right", "label": "Harvard" }`
- `{ "style": "modern-language-association", "label": "MLA" }`
- `{ "style": "vancouver", "label": "Vancouver" }`
- `{ "style": "chicago-fullnote-bibliography", "label": "Chicago" }`
- `{ "style": "ieee", "label": "IEEE" }`
- `{ "style": "bibtex", "label": "BibTeX" }`

### JavaScript Components

The package exports React components that can be used in custom implementations:

```javascript
import { RecordCitationsDropdown, RecordCitationsModal } from '@js/record_citations';
```

## License

This project is part of the OARepo ecosystem developed by CESNET.

## Support

For issues and questions, please use the project's issue tracker or contact the development team at CESNET.

