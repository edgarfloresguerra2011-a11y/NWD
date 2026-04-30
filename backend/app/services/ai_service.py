import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def generate_warmup_content(sender_name: str = "Nexus User"):
    """Generate high-quality, human-like email content for warmup."""
    if not settings.OPENROUTER_API_KEY:
        return None

    prompt = f"""
    Generate a short, professional, and human-like email for a business relationship.
    The goal is 'email warmup', so it should look like a genuine interaction.
    Subject should be catchy and natural.
    The sender name is {sender_name}.
    Include a question to encourage a reply.
    Keep it under 50 words.
    Return only the subject and body in JSON format: {{"subject": "...", "body": "..."}}
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://nexus-warmup.com", # Required by OpenRouter
                    "X-Title": "Nexus Warmup Engine",
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a professional business assistant writing a short email."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                import json
                content = json.loads(data["choices"][0]["message"]["content"])
                return content
            else:
                logger.error(f"OpenRouter error: {response.text}")
                return None
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        return None
