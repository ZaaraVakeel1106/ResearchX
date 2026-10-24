import { useRef, useState } from "react";
import type { FormEvent } from "react";

import { searchPapers } from "../services/api";
import type { PaperSearchResponse, PaperSearchResult } from "../services/api";

type SearchState = "idle" | "loading" | "success" | "error";

function Authors({ authors }: { authors: PaperSearchResult["authors"] }) {
  if (authors === null) {
    return <span>Author information unavailable</span>;
  }
  if (authors.length === 0) {
    return <span>OpenAlex lists no authors for this work</span>;
  }
  const names = authors
    .map((author) => author.display_name)
    .filter((name): name is string => Boolean(name));
  return (
    <span>
      {names.length > 0 ? names.join(", ") : "Author names unavailable"}
      {authors.some((author) => !author.display_name) && names.length > 0
        ? " · Some author names unavailable"
        : ""}
    </span>
  );
}

function PaperCard({ paper }: { paper: PaperSearchResult }) {
  const sourceUrl = paper.landing_page_url ?? paper.open_access_url ?? paper.provider_url;
  const sourceLabel = paper.landing_page_url
    ? "View paper"
    : paper.open_access_url
      ? "View open-access copy"
      : "View OpenAlex record";
  const abstractSnippet = paper.abstract
    ? paper.abstract.length > 480
      ? `${paper.abstract.slice(0, 477).trimEnd()}…`
      : paper.abstract
    : null;
  const openAccessLabel =
    paper.open_access_status === "open_access"
      ? "Marked open access by OpenAlex"
      : paper.open_access_status === "not_marked_open_access"
        ? "Not marked open access by OpenAlex"
        : "Open-access status unavailable";

  return (
    <article className="paper-card">
      <div className="paper-card__topline">
        <span>OPENALEX WORK</span>
        {sourceUrl && (
          <a href={sourceUrl} target="_blank" rel="noopener noreferrer">
            {sourceLabel} <span aria-hidden="true">↗</span>
          </a>
        )}
        {paper.landing_page_url &&
          paper.open_access_url &&
          paper.open_access_url !== paper.landing_page_url && (
            <a href={paper.open_access_url} target="_blank" rel="noopener noreferrer">
              View open-access copy <span aria-hidden="true">↗</span>
            </a>
          )}
      </div>
      <h3>{paper.title ?? "Title unavailable in OpenAlex metadata"}</h3>
      <p className="paper-card__authors"><Authors authors={paper.authors} /></p>
      <dl className="paper-card__details">
        <div><dt>Year</dt><dd>{paper.publication_year ?? "Unavailable"}</dd></div>
        <div><dt>Venue</dt><dd>{paper.venue ?? "Unavailable"}</dd></div>
        <div><dt>DOI</dt><dd>{paper.doi ?? "Unavailable"}</dd></div>
        <div>
          <dt>Citations</dt>
          <dd>{paper.citation_count === null ? "Unavailable" : paper.citation_count}</dd>
        </div>
        <div><dt>Access</dt><dd>{openAccessLabel}</dd></div>
      </dl>
      <p className="paper-card__abstract">
        {abstractSnippet ?? "Abstract unavailable in OpenAlex metadata."}
      </p>
      <p className="paper-card__source">
        Source: {paper.metadata_provenance.provider} · Retrieved{" "}
        <time dateTime={paper.metadata_provenance.retrieved_at}>
          {new Date(paper.metadata_provenance.retrieved_at).toLocaleString()}
        </time>
      </p>
    </article>
  );
}

export function PaperDiscovery() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [state, setState] = useState<SearchState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<PaperSearchResponse | null>(null);
  const requestSequence = useRef(0);

  async function runSearch(searchTerm: string, page: number) {
    const requestId = ++requestSequence.current;
    setState("loading");
    setError(null);
    setSubmittedQuery(searchTerm);
    try {
      const result = await searchPapers(searchTerm, page);
      if (requestId === requestSequence.current) {
        setResponse(result);
        setState("success");
      }
    } catch (searchError) {
      if (requestId === requestSequence.current) {
        setResponse(null);
        setError(
          searchError instanceof Error
            ? searchError.message
            : "Paper search is temporarily unavailable.",
        );
        setState("error");
      }
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedQuery = query.trim();
    if (!normalizedQuery) {
      setResponse(null);
      setError("Enter a research topic or keyword to search.");
      setState("error");
      return;
    }
    void runSearch(normalizedQuery, 1);
  }

  return (
    <section className="discovery" id="search" aria-labelledby="search-title">
      <div className="discovery__intro">
        <span className="section-number">02 / PAPER DISCOVERY</span>
        <h2 id="search-title">Start with a question.<br /><em>Find the work.</em></h2>
        <p>Search OpenAlex research metadata. Search results are shown as provider records and are not saved to a Research X workspace.</p>
      </div>

      <form className="search-form" role="search" onSubmit={handleSubmit}>
        <label htmlFor="paper-query">Research topic or keywords</label>
        <div className="search-form__controls">
          <input
            id="paper-query"
            name="q"
            type="search"
            maxLength={300}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="e.g. graph neural networks"
            aria-describedby="paper-query-help"
          />
          <button type="submit" disabled={state === "loading"}>
            {state === "loading" ? "Searching…" : "Search papers"}
          </button>
        </div>
        <p id="paper-query-help">Search across titles, abstracts, and indexed keywords. Up to 300 characters.</p>
      </form>

      <div className="search-feedback" aria-live="polite">
        {state === "idle" && <p>Enter a topic to explore available research metadata.</p>}
        {state === "loading" && <p role="status">Searching OpenAlex…</p>}
        {state === "error" && <p className="search-error" role="alert">{error}</p>}
        {state === "success" && response?.items.length === 0 && (
          <p>No works were returned for “{submittedQuery}”. Try a different topic.</p>
        )}
      </div>

      {state === "success" && response && response.items.length > 0 && (
        <div className="search-results">
          <div className="search-results__heading">
            <p>
              {response.pagination.total.toLocaleString()} results for “{submittedQuery}”
            </p>
            <span>Metadata supplied by OpenAlex</span>
          </div>
          <ul aria-label="Paper search results">
            {response.items.map((paper) => (
              <li key={paper.provider_id}><PaperCard paper={paper} /></li>
            ))}
          </ul>
          <nav className="pagination" aria-label="Search result pages">
            <button
              type="button"
              disabled={response.pagination.page <= 1}
              onClick={() => void runSearch(submittedQuery, response.pagination.page - 1)}
            >
              Previous
            </button>
            <span>Page {response.pagination.page}</span>
            <button
              type="button"
              disabled={!response.pagination.has_more}
              onClick={() => void runSearch(submittedQuery, response.pagination.page + 1)}
            >
              Next
            </button>
          </nav>
          {response.pagination.provider_limit_reached && (
            <p className="pagination__limit" role="status">
              OpenAlex basic paging is limited to the first 10,000 matching works. Refine your query to explore more specific results.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
