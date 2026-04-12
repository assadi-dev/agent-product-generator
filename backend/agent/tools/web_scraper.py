import httpx
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from backend.logging_config import get_logger

logger = get_logger(__name__)


@tool
async def scrape_product_url(url: str) -> str:
    """
    Scrapes a product URL and returns cleaned text content (title, description, main body).
    Use this tool ONLY when the user has provided a source_url to enrich the product sheet.
    Returns a plain text string with the most relevant product information found on the page.
    """
    logger.info("scrape_start", url=url)
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else ""
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        # Extract main text paragraphs
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 40]
        body = "\n".join(paragraphs[:20])  # cap at first 20 meaningful paragraphs

        content = f"Page Title: {title}\nMeta Description: {meta_desc}\n\nContent:\n{body}"
        # Limit total length to ~3000 chars to stay within context
        result = content[:3000]
        logger.info("scrape_success", url=url, content_length=len(result))
        return result

    except httpx.HTTPStatusError as exc:
        logger.error("scrape_http_error", url=url, status_code=exc.response.status_code, error=str(exc))
        return f"[scrape_error] HTTP {exc.response.status_code} for URL: {url}"
    except httpx.RequestError as exc:
        logger.error("scrape_request_error", url=url, error=str(exc))
        return f"[scrape_error] Could not reach URL: {exc}"
    except Exception as exc:
        logger.error("scrape_unexpected_error", url=url, error=str(exc), exc_info=True)
        return f"[scrape_error] Could not fetch URL: {exc}"
