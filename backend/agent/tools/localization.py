from langchain_core.tools import tool
from backend.services.llm_factory import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


@tool
async def localize_content(content: str, target_language: str) -> str:
    """
    Translates and culturally adapts product copy to the target language.
    Call this as the LAST content step when language is 'fr'.
    Skip this tool entirely when language is 'en'.
    Arguments:
      - content: JSON string containing all product sheet text fields
      - target_language: 'fr' (French) or 'en' (English — no-op, return as-is)
    Returns a JSON string with all text fields translated and culturally adapted.
    """
    if target_language.lower() == "en":
        return content

    llm = get_llm()
    system = (
        "You are a professional marketing translator specializing in French e-commerce. "
        "Translate AND culturally adapt the content — not word-for-word, but for a French audience. "
        "Use natural French marketing language (vous form for professional, tu for casual). "
        "Preserve all JSON structure and keys. Respond ONLY with valid JSON, no markdown."
    )
    prompt = f"""Translate and culturally adapt the following product copy to French (fr-FR):
{content}

Rules:
- Translate all text values, keep all JSON keys in English
- Adapt idioms and expressions to sound natural in French, not like translated English
- Maintain the same tone style as the original
- Return valid JSON with the same structure"""

    response = await llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)])
    return response.content
