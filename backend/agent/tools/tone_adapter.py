from langchain_core.tools import tool
from backend.services.llm_factory import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


TONE_PERSONAS = {
    "professional": (
        "You write polished, credible B2B and B2C copy. "
        "Use authoritative language, active verbs, and clear value propositions. "
        "Avoid slang. Keep sentences clean and structured."
    ),
    "casual": (
        "You write friendly, approachable copy for everyday consumers. "
        "Use conversational language, contractions, and light humor where appropriate. "
        "Make the reader feel like a friend is recommending the product."
    ),
    "luxury": (
        "You write aspirational, premium copy for high-end brands. "
        "Use evocative language, sensory details, and exclusivity signals. "
        "Avoid price mentions, promotions, and anything that feels mass-market."
    ),
    "technical": (
        "You write precise, specification-driven copy for technical buyers. "
        "Lead with measurable capabilities, use industry terminology, and include exact specs. "
        "Avoid marketing fluff — engineers value accuracy over adjectives."
    ),
}


@tool
async def adapt_tone(
    content: str,
    tone: str,
    language: str,
    target_audience: str,
) -> str:
    """
    Rewrites product copy to match a specific tone: professional, casual, luxury, or technical.
    Call this AFTER generate_product_description to polish the content.
    Arguments:
      - content: JSON string from generate_product_description (title, tagline, short/full description)
      - tone: professional | casual | luxury | technical
      - language: 'en' or 'fr'
      - target_audience: persona description
    Returns a JSON string with the same keys but rewritten content.
    """
    persona = TONE_PERSONAS.get(tone, TONE_PERSONAS["professional"])
    llm = get_llm()
    system = persona + (
        " Preserve all factual information. "
        "Respond ONLY with valid JSON using the same keys as the input, no markdown."
    )
    prompt = f"""Target audience: {target_audience}
Language: {language}
Tone: {tone}

Rewrite the following product copy to match the tone described. Keep the same JSON structure:
{content}

Return the same JSON keys with rewritten values."""

    response = await llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)])
    return response.content
