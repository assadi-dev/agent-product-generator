from langchain_core.tools import tool
from backend.services.llm_factory import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


@tool
async def extract_key_features(
    product_name: str,
    category: str,
    product_description: str,
) -> str:
    """
    Extracts 5-8 key selling features (USPs) from a product description.
    Call this AFTER generate_product_description, passing its full_description as product_description.
    Returns a JSON array of feature strings, e.g. ["Feature 1", "Feature 2", ...].
    """
    llm = get_llm()
    system = (
        "You are a product marketing specialist. "
        "Extract specific, differentiated selling points — not generic claims. "
        "Each feature should be a concise, benefit-focused bullet point. "
        "Respond ONLY with a valid JSON array of strings, no markdown, no extra text."
    )
    prompt = f"""Product: {product_name}
Category: {category}

Description:
{product_description}

Extract 5-8 key features. Focus on:
- Concrete benefits (not vague claims like "high quality")
- Differentiators from competitors
- Features that matter to buyers in this category

Return format: ["Feature 1", "Feature 2", ...]"""

    response = await llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)])
    return response.content
