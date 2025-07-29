import React, { memo } from "react";

import { Placeholder, Message } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_citations";

import { decode } from "html-entities";
import sanitizeHtml from "sanitize-html";
import Linkify from "linkify-react";

export const PlaceholderLoader = () => {
  return (
    <Placeholder fluid role="presentation">
      <Placeholder.Paragraph>
        <Placeholder.Line />
        <Placeholder.Line />
        <Placeholder.Line />
      </Placeholder.Paragraph>
    </Placeholder>
  );
};

export const ErrorMessage = ({ message, label }) => {
  return <Message negative role="status" aria-label={i18next.t(`Error generating ${label} citation`)}>{message}</Message>;
};

export const LinkifiedCitation = memo(({ citation }) => {
  const decodedCitation = decode(citation);
  const sanitizedCitation = sanitizeHtml(decodedCitation, {
    allowedTags: ["a", "b", "i", "em", "strong", "p"],
    allowedAttributes: {
      a: ["href", "target", "rel"],
    },
  });

  return (
    <Linkify 
      as="div" 
      options={{ target: "_blank", rel: "noopener noreferrer", className: "word-break-all" }}
    >
      {sanitizedCitation}
    </Linkify>
  );
});
