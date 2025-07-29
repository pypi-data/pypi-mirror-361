from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    ".",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "record_citations": "./js/record_citations/index.js",
                "record_citations_dropdown": "./js/record_citations/dropdown/index.js",
                "record_citations_modal": "./js/record_citations/modal/index.js",
                "record_citations_components": "./js/record_citations/custom-components.js",
            },
            "dependencies": {
                "linkifyjs": "^4.3.1",
                "linkify-react": "^4.3.1",
            },
            "devDependencies": {},
            "aliases": {
                "@js/record_citations": "./js/record_citations",
            },
        }
    },
)
