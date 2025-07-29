import React from "react";
import PropTypes from "prop-types";

import CitationListItem from "./CitationListItem";

import { List } from "semantic-ui-react";

const CitationList = ({ record, citationStyles }) => {
  return (
    <List divided relaxed size="large">
      {citationStyles.map(({ style, label }) => (
        <CitationListItem
          key={style}
          recordLink={record.links.self}
          style={style}
          label={label}
        />
      ))}
    </List>
  );
};

CitationList.propTypes = {
  record: PropTypes.object.isRequired,
  citationStyles: PropTypes.arrayOf(PropTypes.shape({
    style: PropTypes.string.isRequired,
    label: PropTypes.string,
  })).isRequired,
};

export default CitationList;
