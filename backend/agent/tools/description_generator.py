import json
from langchain_core.tools import tool
from backend.services.llm_factory import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


@tool
async def generate_product_description(
    product_name: str,
    category: str,
    context: str,
    tone: str,
    language: str,
) -> str:
    """
    Generates a rich product description given available context.
    Call this tool FIRST (before feature extraction, SEO, or tone adaptation).
    Arguments:
      - product_name: name of the product
      - category: product category
      - context: any available product info (scraped content, raw description, etc.)
      - tone: one of professional | casual | luxury | technical
      - language: 'en' or 'fr'
    Returns a JSON string with keys: full_description, short_description, title, tagline.
    """
    llm = get_llm()
    system = (
        "You are an expert product copywriter. "
        "Generate compelling, accurate product copy based on the context provided. "
        "Do NOT invent technical specifications that are not supported by the context. "
        "Respond ONLY with valid JSON, no markdown, no extra text."
    )
    prompt = f"""Product: {product_name}
Category: {category}
Desired tone: {tone}
Language: {language}

Available context:
{context or "No additional context provided. Use your knowledge of this product category."}

Generate a product sheet draft with the following JSON structure:
{{
  "title": "<punchy marketing title, max 80 chars>",
  "tagline": "<one-sentence value proposition, max 120 chars>",
  "short_description": "<2-3 sentence elevator pitch>",
  "full_description": "<3-5 paragraphs, rich marketing copy>"
}}"""

    response = await llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)])
    return response.content
