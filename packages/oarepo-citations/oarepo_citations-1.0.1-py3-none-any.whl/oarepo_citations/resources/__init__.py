from flask import request
from invenio_i18n.ext import current_i18n
from invenio_records_resources.resources.records.headers import etag_headers
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_runtime.resources.responses import ExportableResponseHandler
from marshmallow import Schema

from .csl import CSLBibTexSerializer, CSLJSONSerializer, StringCitationSerializer


def csl_url_args_retriever():
    """Returns the style and locale passed as URL args for CSL export."""
    style = request.args.get("style")
    locale = request.args.get("locale", current_i18n.locale)
    return style, locale


#
# Response handlers
#
def _bibliography_headers(obj_or_list, code, many=False):
    """Override content type for 'text/x-bibliography'."""
    _etag_headers = etag_headers(obj_or_list, code, many=False)
    _etag_headers["content-type"] = "text/plain"
    return _etag_headers


def create_citation_response_handlers(csl_json_schema_cls: Schema):
    """Create citation response handlers based on the provided CSL JSON schema.

    :param csl_json_schema_cls: CSL JSON schema class for serialization.
    """
    return {
        "application/vnd.citationstyles.csl+json": ExportableResponseHandler(
            export_code="csl",
            name=_("CSL"),
            serializer=CSLJSONSerializer(csl_json_schema_cls),
            headers=etag_headers,
        ),
        "text/x-iso-690+plain": ExportableResponseHandler(
            export_code="citation",
            name=_("Citation string"),
            serializer=StringCitationSerializer(
                csl_json_schema_cls, url_args_retriever=csl_url_args_retriever
            ),
            headers=_bibliography_headers,
        ),
        "text/x-bibtex+plain": ExportableResponseHandler(
            export_code="bibtex",
            name=_("BibTex"),
            serializer=CSLBibTexSerializer(csl_json_schema_cls),
        ),
        "text/x-bibliography": ExportableResponseHandler(
            export_code="bibliography",
            name=_("Bibliography"),
            serializer=StringCitationSerializer(
                csl_json_schema_cls, url_args_retriever=csl_url_args_retriever
            ),
            headers=_bibliography_headers,
        ),
    }
