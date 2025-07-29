import React from "react";
import ReactDOM from "react-dom";

import { RecordCitationsModal } from "./components";

const recordCitationsAppDiv = document.getElementById("record-citations");
const settings = JSON.parse(recordCitationsAppDiv.dataset.citationSettings);

ReactDOM.render(
  <RecordCitationsModal
    record={JSON.parse(recordCitationsAppDiv.dataset.record)}
    citationStyles={settings?.styles}
  />,
  recordCitationsAppDiv
);

export { RecordCitationsModal };
