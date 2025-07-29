import { useState, useEffect, useCallback, useRef } from "react";
import { withCancel } from "react-invenio-forms";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import axios from "axios";

const fetchCitation = async (recordLink, style) => {
  const locale = i18next.language === "cs" ? "cs-CZ" : i18next.language === "en" ? "en-US" : i18next.language;
  const url = `${recordLink}?locale=${locale}&style=${style}`;
  let acceptHeader;
  switch (style) {
    case "iso690-author-date-cs":
      acceptHeader = "text/x-iso-690+plain";
      break;
    case "bibtex":
      acceptHeader = "text/x-bibtex+plain";
      break;
    default:
      acceptHeader = "text/x-bibliography";
      break;
  }
  return await axios(url, {
    withCredentials: true,
    xsrfCookieName: "csrftoken",
    xsrfHeaderName: "X-CSRFToken",
    headers: {
      Accept: acceptHeader,
    },
  });
};

export const useCitation = (recordLink, defaultStyle) => {
  const [citation, setCitation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const cancellableFetchCitationRef = useRef(null);

  const getCitation = useCallback(async (style) => {
    setError(null);
    setLoading(true);
    setCitation("");

    const cancellableFetch = withCancel(
      fetchCitation(recordLink, style)
    );
    cancellableFetchCitationRef.current = cancellableFetch;

    try {
      const response = await cancellableFetch.promise;
      setLoading(false);
      setCitation(response.data);
    } catch (error) {
      if (error !== "UNMOUNTED") {
        setLoading(false);
        setCitation("");
        setError(i18next.t("An error occurred while generating the citation."));
      }
    }
  }, [recordLink]);

  useEffect(() => {
    const cancellableFetchCitation = cancellableFetchCitationRef.current;
    getCitation(defaultStyle);
    return () => {
      cancellableFetchCitation?.cancel();
    };
  }, [getCitation, defaultStyle]);

  return {
    getCitation,
    citation,
    loading,
    error,
  };
};
