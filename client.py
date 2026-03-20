"""
citation-constellation/client.py
==================================
Async API clients for OpenAlex and ROR with rate limiting, pagination, and retries.

Shared across all phases. Provides two client classes:
  - OpenAlexClient: fetches authors, works, citations, and institutions
  - RORClient: fetches institution hierarchy data from the ROR API

Both clients use httpx for async HTTP, implement automatic retry with
exponential backoff on failures, respect rate limits (HTTP 429), and
support concurrent request batching with configurable semaphores.

Configuration constants at the top control request behaviour.
Set OPENALEX_MAILTO to your email to use OpenAlex's polite pool
(faster rate limits for identified users).
"""

import asyncio
from typing import Optional, Callable

import httpx

# ============================================================
# Configuration
# ============================================================

OPENALEX_BASE = "https://api.openalex.org"
OPENALEX_MAILTO = "mahbub.ul.alam.anondo@gmail.com"  # Used for OpenAlex polite pool
ROR_BASE = "https://api.ror.org/v2"

PER_PAGE = 200              # Results per API page (OpenAlex max is 200)
MAX_CONCURRENT = 5          # Max concurrent API requests (avoids overwhelming APIs)
RATE_LIMIT_DELAY = 0.1      # Seconds between request batches (polite pacing)


# ============================================================
# OpenAlex Client
# ============================================================

class OpenAlexClient:
    """
    Async client for the OpenAlex API.

    Usage (as async context manager):
        async with OpenAlexClient() as client:
            author = await client.get_author("0000-0002-1101-3793")
            works = await client.get_works_by_author(author["id"])

    Features:
      - Automatic cursor-based pagination for large result sets
      - Retry with exponential backoff on HTTP errors and connection failures
      - Rate limit handling (backs off on HTTP 429)
      - Concurrent batch fetching with semaphore-based throttling
      - API call counter for audit/reporting
    """

    def __init__(self, mailto: str = OPENALEX_MAILTO):
        self.mailto = mailto
        self.api_calls = 0                          # Running counter for audit reporting
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Initialise the HTTP client with OpenAlex base URL and polite pool params."""
        self.client = httpx.AsyncClient(
            base_url=OPENALEX_BASE,
            params={"mailto": self.mailto},         # Identifies us to the polite pool
            timeout=30.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args):
        """Cleanly close the HTTP client."""
        if self.client:
            await self.client.aclose()

    async def _get(self, path: str, params: dict = None) -> dict:
        """
        Low-level GET request with retry logic.

        Retries up to 3 times on:
          - HTTP errors (non-2xx status codes)
          - Connection errors (network issues)
          - Rate limiting (HTTP 429 — backs off using Retry-After header)

        Args:
            path: API endpoint path (e.g. "/authors/A12345").
            params: Optional query parameters.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            httpx.HTTPStatusError: If all retries are exhausted.
        """
        params = params or {}
        retries = 3
        for attempt in range(retries):
            try:
                resp = await self.client.get(path, params=params)
                self.api_calls += 1

                # Handle rate limiting: wait as long as the API tells us to
                if resp.status_code == 429:
                    wait = float(resp.headers.get("retry-after", 2))
                    await asyncio.sleep(wait)
                    continue

                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPStatusError, httpx.ConnectError) as e:
                if attempt == retries - 1:
                    raise  # Give up after final attempt
                await asyncio.sleep(1 * (attempt + 1))  # Linear backoff: 1s, 2s, 3s
        return {}

    # ── Author Resolution ──

    async def get_author(self, identifier: str) -> dict:
        """
        Resolve an author by ORCID or OpenAlex ID.

        Accepts three identifier formats:
          - ORCID:      "0000-0002-1101-3793" → /authors/orcid:0000-0002-1101-3793
          - OpenAlex:   "A5100390903"          → /authors/A5100390903
          - Full URL:   "https://openalex.org/A5100390903" → /authors/A5100390903

        Returns:
            Raw OpenAlex author JSON.
        """
        if identifier.startswith("0000-"):
            # ORCID format (starts with 0000-)
            path = f"/authors/orcid:{identifier}"
        elif identifier.startswith("A") or identifier.startswith("https://"):
            # OpenAlex ID or full URL
            clean = identifier.replace("https://openalex.org/", "")
            path = f"/authors/{clean}"
        else:
            # Fallback: pass identifier as-is
            path = f"/authors/{identifier}"
        return await self._get(path)

    # ── Works Fetching ──

    async def get_works_by_author(self, author_id: str, progress_callback: Callable = None) -> list[dict]:
        """
        Fetch all works by an author using cursor-based pagination.

        Uses OpenAlex's cursor pagination to iterate through all works
        attributed to the given author. Selects only the fields needed
        by the pipeline to minimise response size.

        Args:
            author_id: Bare OpenAlex author ID (e.g. "A5100390903").
            progress_callback: Optional callback(done, total) for progress display.

        Returns:
            List of raw work JSON dicts.
        """
        works, cursor = [], "*"  # "*" is the initial cursor value for OpenAlex
        while cursor:
            params = {
                "filter": f"author.id:{author_id}",
                "per_page": PER_PAGE,
                "cursor": cursor,
                # Select only the fields we actually use (reduces response size)
                "select": ",".join([
                    "id", "doi", "title", "publication_year", "type",
                    "cited_by_count", "authorships", "referenced_works",
                    "primary_location",
                ]),
            }
            data = await self._get("/works", params)
            results = data.get("results", [])
            works.extend(results)

            # Report progress if a callback was provided
            if progress_callback:
                progress_callback(len(works), data.get("meta", {}).get("count", 0))

            # Advance cursor; None means no more pages
            cursor = data.get("meta", {}).get("next_cursor")
            if not results:
                break  # Safety: stop if a page returns no results
            await asyncio.sleep(RATE_LIMIT_DELAY)
        return works

    # ── Citation Fetching ──

    async def get_citing_works(self, work_id: str) -> list[dict]:
        """
        Fetch all works that cite a given work, using cursor pagination.

        Args:
            work_id: Bare OpenAlex work ID (e.g. "W2100837269").

        Returns:
            List of raw citing work JSON dicts.
        """
        clean_id = work_id.replace("https://openalex.org/", "")
        works, cursor = [], "*"
        while cursor:
            params = {
                "filter": f"cites:{clean_id}",
                "per_page": PER_PAGE,
                "cursor": cursor,
                "select": "id,doi,title,publication_year,authorships",
            }
            data = await self._get("/works", params)
            results = data.get("results", [])
            works.extend(results)
            cursor = data.get("meta", {}).get("next_cursor")
            if not results:
                break
            await asyncio.sleep(RATE_LIMIT_DELAY)
        return works

    async def get_citing_works_batch(self, work_ids: list[str], progress_callback: Callable = None) -> dict[str, list[dict]]:
        """
        Fetch citing works for multiple works concurrently.

        Uses a semaphore to limit concurrent requests to MAX_CONCURRENT,
        preventing API overload while still parallelising I/O.

        Args:
            work_ids: List of bare OpenAlex work IDs to fetch citations for.
            progress_callback: Optional callback(done, total) for progress display.

        Returns:
            Dict mapping each work_id to its list of citing works.
        """
        results = {}
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        completed = 0

        async def fetch_one(wid):
            nonlocal completed
            async with sem:
                citing = await self.get_citing_works(wid)
                results[wid] = citing
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(work_ids))

        tasks = [fetch_one(wid) for wid in work_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
        return results

    # ── Co-Author Work Fetching (Phase 2) ──

    async def get_coauthors_for_works(self, work_ids: list[str], progress_callback: Callable = None) -> list[dict]:
        """
        Fetch authorship data for a batch of works concurrently.

        Used in Phase 2 to expand the co-author graph beyond the target
        researcher's direct publications. Fetches only the fields needed
        for graph construction (id, year, authorships).

        Args:
            work_ids: List of OpenAlex work IDs (may include URL prefix).
            progress_callback: Optional callback(done, total) for progress display.

        Returns:
            List of raw work JSON dicts with authorship information.
        """
        works = []
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        completed = 0

        async def fetch_one(wid):
            nonlocal completed
            async with sem:
                clean = wid.replace("https://openalex.org/", "")
                data = await self._get(f"/works/{clean}", {"select": "id,publication_year,authorships"})
                works.append(data)
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(work_ids))

        tasks = [fetch_one(wid) for wid in work_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
        return works

    # ── Institution Fetching (Phase 3) ──

    async def get_institution(self, institution_id: str) -> dict:
        """
        Fetch a single institution's metadata from OpenAlex.

        Args:
            institution_id: OpenAlex institution ID (may include URL prefix).

        Returns:
            Raw institution JSON dict.
        """
        clean = institution_id.replace("https://openalex.org/", "")
        return await self._get(f"/institutions/{clean}")

    async def get_institutions_batch(self, institution_ids: list[str], progress_callback: Callable = None) -> dict[str, dict]:
        """
        Fetch metadata for multiple institutions concurrently.

        Silently skips institutions that fail to fetch (some OpenAlex
        institution IDs may be stale or invalid). This is acceptable
        because missing institution data results in UNKNOWN classification
        rather than a pipeline failure.

        Args:
            institution_ids: List of OpenAlex institution IDs.
            progress_callback: Optional callback(done, total) for progress display.

        Returns:
            Dict mapping institution_id to raw JSON. Missing institutions are omitted.
        """
        results = {}
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        completed = 0

        async def fetch_one(iid):
            nonlocal completed
            async with sem:
                clean = iid.replace("https://openalex.org/", "")
                try:
                    data = await self._get(f"/institutions/{clean}")
                    results[iid] = data
                except Exception:
                    pass  # Skip failed fetches — missing data → UNKNOWN classification
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(institution_ids))

        tasks = [fetch_one(iid) for iid in institution_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
        return results


# ============================================================
# ROR Client (Phase 3+)
# ============================================================

class RORClient:
    """
    Async client for the ROR (Research Organization Registry) API v2.

    Used in Phase 3 to resolve institutional hierarchies: parent-child
    relationships between universities, research centres, and consortia.

    Usage (as async context manager):
        async with RORClient() as client:
            org = await client.get_organization("01an7q238")
            # Returns full ROR record including relationships
    """

    def __init__(self):
        self.api_calls = 0
        self.client = None

    async def __aenter__(self):
        """Initialise the HTTP client with ROR API v2 base URL."""
        self.client = httpx.AsyncClient(
            base_url=ROR_BASE,
            timeout=15.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args):
        """Cleanly close the HTTP client."""
        if self.client:
            await self.client.aclose()

    async def _get(self, path, params=None):
        """
        Low-level GET request with retry logic (same pattern as OpenAlexClient).

        Returns an empty dict on final failure (rather than raising) because
        missing ROR data is non-fatal — it just means we can't resolve the
        institutional hierarchy for that particular organisation.
        """
        params = params or {}
        retries = 3
        for attempt in range(retries):
            try:
                resp = await self.client.get(path, params=params)
                self.api_calls += 1
                if resp.status_code == 429:
                    await asyncio.sleep(2)  # ROR doesn't send Retry-After, use fixed 2s
                    continue
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPStatusError, httpx.ConnectError):
                if attempt == retries - 1:
                    return {}  # Graceful degradation: missing ROR data → UNKNOWN
                await asyncio.sleep(1 * (attempt + 1))
        return {}

    async def get_organization(self, ror_id):
        """
        Fetch a single organization's full record from ROR.

        The response includes the 'relationships' array with parent/child
        links, which the InstitutionHierarchy uses to detect SAME_PARENT_ORG.

        Args:
            ror_id: ROR identifier (with or without 'https://ror.org/' prefix).

        Returns:
            Raw ROR JSON dict, or empty dict on failure.
        """
        clean = ror_id.replace("https://ror.org/", "")
        return await self._get(f"/organizations/{clean}")

    async def get_organizations_batch(self, ror_ids, progress_callback=None):
        """
        Fetch multiple ROR organizations concurrently.

        Paced with RATE_LIMIT_DELAY between requests and limited to
        MAX_CONCURRENT simultaneous connections.

        Args:
            ror_ids: List of ROR identifiers.
            progress_callback: Optional callback(done, total) for progress display.

        Returns:
            Dict mapping ror_id to raw JSON. Failed fetches are omitted.
        """
        results = {}
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        completed = 0

        async def fetch_one(rid):
            nonlocal completed
            async with sem:
                data = await self.get_organization(rid)
                if data:
                    results[rid] = data
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(ror_ids))
                await asyncio.sleep(RATE_LIMIT_DELAY)

        tasks = [fetch_one(rid) for rid in ror_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
        return results
