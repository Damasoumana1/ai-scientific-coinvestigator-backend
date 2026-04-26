"""
Service for searching and downloading papers from OpenAlex.
OpenAlex is a fully open catalog of the global research system (200M+ works).
API docs: https://developers.openalex.org/
"""
import httpx
import os
from typing import List, Dict, Optional
from app.core.logging import logger


class OpenAlexService:
    """
    Service complet pour OpenAlex : recherche + téléchargement PDF open-access.
    Suit exactement le même pattern que ArXivService, DOAJService, PubMedService.
    """

    BASE_URL = "https://api.openalex.org/works"

    def __init__(
        self,
        download_dir: str = "./uploaded_files",
        email: str = "soumanadama93@gmail.com"
    ):
        self.download_dir = download_dir
        self.email = email  # Required by OpenAlex polite pool (higher rate limits)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    # ------------------------------------------------------------------
    # PUBLIC: fetch_papers — identique aux autres services
    # ------------------------------------------------------------------
    def fetch_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search OpenAlex for papers and return normalized metadata.
        Uses 'polite pool' via mailto param for better rate limits.
        Filters: only open-access works with a usable PDF or landing page URL.
        """
        logger.info(f"Searching OpenAlex for: '{query}' (max: {max_results})")

        params = {
            "search": query,
            "mailto": self.email,
            "per-page": min(max_results, 50),   # OpenAlex max per-page = 200
            "sort": "relevance_score:desc",
            # Only return open-access works to maximize PDF availability
            "filter": "is_oa:true",
            # Select only the fields we need (faster, lighter response)
            "select": (
                "id,title,authorships,abstract_inverted_index,"
                "open_access,topics,publication_date,doi,"
                "cited_by_count,primary_location"
            ),
        }

        results = []
        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

            for item in data.get("results", []):
                parsed = self._parse_item(item)
                if parsed:
                    results.append(parsed)

            logger.info(f"OpenAlex returned {len(results)} results for '{query}'")

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAlex HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"OpenAlex search error: {e}")

        return results

    # ------------------------------------------------------------------
    # PUBLIC: download_paper — même signature que DOAJService/PubMedService
    # ------------------------------------------------------------------
    def download_paper(self, paper_url: str, paper_id: str) -> str:
        """
        Downloads an open-access PDF from OpenAlex oa_url.
        Returns local file path, or empty string on failure.
        """
        if not paper_url:
            logger.warning(f"OpenAlex: no URL provided for {paper_id}")
            return ""

        # Sanitize filename (OpenAlex IDs look like "W2987984220")
        safe_id = paper_id.replace("/", "_").replace(":", "_")
        file_name = f"openalex_{safe_id}.pdf"
        file_path = os.path.join(self.download_dir, file_name)

        if os.path.exists(file_path):
            logger.info(f"OpenAlex: cache hit for {paper_id}")
            return file_path

        logger.info(f"OpenAlex: downloading {paper_id} from {paper_url}")
        try:
            with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                response = client.get(paper_url)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "").lower()
                if "application/pdf" not in content_type and len(response.content) < 1000:
                    logger.warning(
                        f"OpenAlex: response for {paper_id} is not a PDF "
                        f"(Content-Type: {content_type})"
                    )
                    return ""

                with open(file_path, "wb") as f:
                    f.write(response.content)

            logger.info(f"OpenAlex: saved {paper_id} → {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"OpenAlex: failed to download {paper_id}: {e}")
            return ""

    # ------------------------------------------------------------------
    # PRIVATE: helpers
    # ------------------------------------------------------------------
    def _parse_item(self, item: dict) -> Optional[Dict]:
        """
        Normalizes a single OpenAlex work into the common paper dict format
        shared by all services in this project.
        """
        title = item.get("title")
        if not title:
            return None  # Skip works without title

        # --- ID ---
        raw_id = item.get("id", "")
        # Looks like "https://openalex.org/W2987984220" → clean to "W2987984220"
        clean_id = f"openalex_{raw_id.split('/')[-1]}" if raw_id else "openalex_unknown"

        # --- Abstract (inverted index → plain text) ---
        abstract = self._reconstruct_abstract(item.get("abstract_inverted_index"))

        # --- Authors ---
        authors = []
        for authorship in item.get("authorships", []):
            name = authorship.get("author", {}).get("display_name")
            if name:
                authors.append(name)

        # --- Open Access PDF URL ---
        oa = item.get("open_access", {})
        pdf_url = oa.get("oa_url")  # Direct PDF or landing page
        has_pdf = bool(pdf_url)

        # Fallback: primary_location landing page
        if not pdf_url:
            primary = item.get("primary_location") or {}
            pdf_url = primary.get("landing_page_url") or primary.get("pdf_url")
            has_pdf = False  # It's a landing page, not a direct PDF

        # Fallback: DOI
        if not pdf_url and item.get("doi"):
            pdf_url = item["doi"]

        # --- Topics/Categories (replacing deprecated concepts) ---
        topics = []
        for topic in item.get("topics", [])[:5]:
            name = topic.get("display_name")
            if name:
                topics.append(name)

        return {
            "id": clean_id,
            "title": title,
            "authors": authors if authors else ["Unknown"],
            "summary": abstract,
            "url": pdf_url,
            "has_pdf": has_pdf,
            "categories": topics,
            "publication_date": item.get("publication_date", "n.d."),
            "cited_by_count": item.get("cited_by_count", 0),
            "source": "OpenAlex",
        }

    @staticmethod
    def _reconstruct_abstract(abstract_inverted_index: Optional[dict]) -> str:
        """
        OpenAlex stores abstracts as an inverted index: {word: [positions]}.
        This reconstructs the plain text.
        """
        if not abstract_inverted_index:
            return "No abstract available."

        try:
            max_idx = max(
                idx
                for positions in abstract_inverted_index.values()
                for idx in positions
            )
            words = [""] * (max_idx + 1)
            for word, positions in abstract_inverted_index.items():
                for idx in positions:
                    words[idx] = word
            return " ".join(w for w in words if w).strip()
        except Exception:
            return "Abstract reconstruction failed."
