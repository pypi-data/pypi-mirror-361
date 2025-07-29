import React, { useState } from "react";
import PropTypes from "prop-types";

import { i18next } from "@translations/oarepo_citations";
import { Segment, Modal, Button } from "semantic-ui-react";

import TriggerButton from "./TriggerButton";
import CitationList from "./CitationList";

export const RecordCitationsModal = ({ record, citationStyles }) => {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <Modal
        onClose={() => setModalOpen(false)}
        onOpen={() => setModalOpen(true)}
        open={modalOpen}
        trigger={<TriggerButton />}
        role="dialog"
        aria-labelledby="citation-modal-header"
        aria-describedby="citation-modal-desc"
      >
        <Modal.Header as="h1" id="citation-modal-header">{i18next.t("Citations")}</Modal.Header>
        <Modal.Content>
          <p id="citation-modal-desc">{i18next.t("record-citation-modal-description")}</p>
          <Segment>
            <CitationList record={record} citationStyles={citationStyles} />
          </Segment>
        </Modal.Content>
        <Modal.Actions>
          <Button title={i18next.t("Close citations modal window")} onClick={() => setModalOpen(false)}>
            {i18next.t("Close")}
          </Button>
        </Modal.Actions>
      </Modal>
    </>
  );
};

RecordCitationsModal.propTypes = {
  record: PropTypes.object.isRequired,
  citationStyles: PropTypes.arrayOf(PropTypes.shape({
    style: PropTypes.string.isRequired,
    label: PropTypes.string,
  })).isRequired,
};

RecordCitationsModal.defaultProps = {
  citationStyles: [
    { "style": "iso690-author-date-cs", "label": "ČSN ISO 690" },
    { "style": "apa", "label": "APA" },
    { "style": "harvard-cite-them-right", "label": "Harvard" },
    { "style": "modern-language-association", "label": "MLA" },
    { "style": "vancouver", "label": "Vancouver" },
    { "style": "chicago-fullnote-bibliography", "label": "Chicago" },
    { "style": "ieee", "label": "IEEE" },
    { "style": "bibtex", "label": "BibTeX" },
  ],
};
