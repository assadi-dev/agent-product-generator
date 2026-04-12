from langchain_core.tools import tool
from backend.services.llm_factory import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


@tool
async def extract_seo_keywords(
    product_name: str,
    category: str,
    description: str,
    target_audience: str,
    language: str,
) -> str:
    """
    Extracts SEO keywords and generates an optimized meta title and meta description.
    Call this AFTER generate_product_description.
    Returns a JSON object with keys: seo_keywords (list), meta_title (str), meta_description (str).
    """
    llm = get_llm()
    system = (
        "You are an SEO specialist with e-commerce expertise. "
        "Generate keywords and meta tags that maximize organic search visibility. "
        "Follow strict character limits. Respond ONLY with valid JSON, no markdown."
    )
    prompt = f"""Product: {product_name}
Category: {category}
Target audience: {target_audience}
Language: {language}

Description:
{description}

Generate SEO assets with this JSON structure:
{{
  "seo_keywords": ["keyword1", "keyword2", ...],  // 10-15 keywords, mix short-tail and long-tail
  "meta_title": "<title under 60 characters including product name>",
  "meta_description": "<compelling description under 155 characters with a call to action>"
}}

Rules:
- Keywords should include the product name, category, use cases, and audience terms
- meta_title MUST be under 60 characters
- meta_description MUST be under 155 characters
- If language is 'fr', write all content in French"""

    response = await llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)])
    return response.content
