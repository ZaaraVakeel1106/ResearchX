export interface HealthResponse {
  status: "ok";
}

export interface PaperSearchAuthor {
  provider_id: string | null;
  display_name: string | null;
}

export interface PaperMetadataProvenance {
  provider: string;
  retrieved_at: string;
}

export interface PaperSearchResult {
  provider_id: string;
  provider_url: string | null;
  title: string | null;
  authors: PaperSearchAuthor[] | null;
  publication_year: number | null;
  publication_date: string | null;
  venue: string | null;
  doi: string | null;
  abstract: string | null;
  landing_page_url: string | null;
  open_access_status: "open_access" | "not_marked_open_access" | null;
  open_access_url: string | null;
  citation_count: number | null;
  metadata_provenance: PaperMetadataProvenance;
}

export interface PaperSearchResponse {
  items: PaperSearchResult[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    has_more: boolean;
    provider_limit_reached: boolean;
  };
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNullableString(value: unknown): value is string | null {
  return value === null || typeof value === "string";
}

function isSafeExternalUrl(value: unknown): value is string | null {
  if (value === null) return true;
  if (typeof value !== "string") return false;
  try {
    const url = new URL(value);
    return (
      (url.protocol === "https:" || url.protocol === "http:") &&
      !url.username &&
      !url.password
    );
  } catch {
    return false;
  }
}

function isPaperSearchAuthor(value: unknown): value is PaperSearchAuthor {
  return (
    isRecord(value) &&
    isNullableString(value.provider_id) &&
    isNullableString(value.display_name)
  );
}

function isPaperSearchResult(value: unknown): value is PaperSearchResult {
  return (
    isRecord(value) &&
    typeof value.provider_id === "string" &&
    value.provider_id.length > 0 &&
    isSafeExternalUrl(value.provider_url) &&
    isNullableString(value.title) &&
    (value.authors === null ||
      (Array.isArray(value.authors) && value.authors.every(isPaperSearchAuthor))) &&
    (value.publication_year === null || Number.isInteger(value.publication_year)) &&
    isNullableString(value.publication_date) &&
    isNullableString(value.venue) &&
    isNullableString(value.doi) &&
    isNullableString(value.abstract) &&
    isSafeExternalUrl(value.landing_page_url) &&
    (value.open_access_status === null ||
      value.open_access_status === "open_access" ||
      value.open_access_status === "not_marked_open_access") &&
    isSafeExternalUrl(value.open_access_url) &&
    (value.citation_count === null ||
      (Number.isInteger(value.citation_count) && (value.citation_count as number) >= 0)) &&
    isRecord(value.metadata_provenance) &&
    typeof value.metadata_provenance.provider === "string" &&
    typeof value.metadata_provenance.retrieved_at === "string" &&
    !Number.isNaN(Date.parse(value.metadata_provenance.retrieved_at))
  );
}

function isPaperSearchResponse(value: unknown): value is PaperSearchResponse {
  if (!isRecord(value) || !Array.isArray(value.items) || !isRecord(value.pagination)) {
    return false;
  }
  const pagination = value.pagination;
  return (
    value.items.every(isPaperSearchResult) &&
    Number.isInteger(pagination.page) && (pagination.page as number) >= 1 &&
    Number.isInteger(pagination.page_size) && (pagination.page_size as number) >= 1 &&
    Number.isInteger(pagination.total) && (pagination.total as number) >= 0 &&
    typeof pagination.has_more === "boolean" &&
    typeof pagination.provider_limit_reached === "boolean"
  );
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }

  const payload: unknown = await response.json();
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("status" in payload) ||
    payload.status !== "ok"
  ) {
    throw new Error("Health check returned an invalid response");
  }

  return payload as HealthResponse;
}

export async function searchPapers(
  query: string,
  page = 1,
  pageSize = 20,
): Promise<PaperSearchResponse> {
  const params = new URLSearchParams({ q: query, page: String(page), page_size: String(pageSize) });
  const response = await fetch(`${API_BASE_URL}/papers/search?${params.toString()}`);
  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      typeof payload === "object" &&
      payload !== null &&
      "error" in payload &&
      typeof payload.error === "object" &&
      payload.error !== null &&
      "message" in payload.error &&
      typeof payload.error.message === "string"
        ? payload.error.message
        : "Paper search is temporarily unavailable.";
    throw new Error(message);
  }

  if (!isPaperSearchResponse(payload)) {
    throw new Error("Paper search returned an invalid response.");
  }

  return payload;
}
