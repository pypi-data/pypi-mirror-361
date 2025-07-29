from oarepo_ui.resources.config import TemplatePageUIResourceConfig
from oarepo_ui.resources.resource import TemplatePageUIResource


class RecordCitationsResourceConfig(TemplatePageUIResourceConfig):
    url_prefix = "/"
    blueprint_name = "record_citations"
    template_folder = "templates"


def create_blueprint(app):
    """Register blueprint for this resource."""
    return TemplatePageUIResource(RecordCitationsResourceConfig()).as_blueprint()
