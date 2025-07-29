import React from "react";
import PropTypes from "prop-types";

import { Button } from "semantic-ui-react";

import { i18next } from "@translations/oarepo_citations";

const TriggerButton = ({ onClick }) => {
  return (
    <Button title={i18next.t('Open citations modal window')} className="citations-trigger-button" onClick={onClick}>
      {i18next.t('cite this work').toUpperCase()}
    </Button>
  );
};

TriggerButton.propTypes = {
  onClick: PropTypes.func,
};

export default TriggerButton;