"""
Script generation via Claude API.
Returns a structured JSON dict with narration_text, scene_descriptions, and call_to_action.
"""
import json
import anthropic
from app.config import settings

client = anthropic.Anthropic(
    api_key=settings.anthropic_api_key,
    base_url="https://www.open-claude.com/v1"
)

SYSTEM_PROMPT = """You are an expert mobile app marketing copywriter specializing in App Store and Google Play preview videos.
Generate compelling, concise video scripts that highlight the app's key features and drive downloads.
Always respond with valid JSON only — no markdown, no extra text."""

SCRIPT_TEMPLATE = """\
Generate a {duration}-second app store preview video script for the following app:

App Name: {app_name}
Category: {category}
Style: {style}
Target Store: {store}
Description: {description}
Keywords: {keywords}

Return JSON with this exact structure:
{{
  "narration_text": "Full voiceover narration (max 50 words for 25s, proportional for longer)",
  "scene_descriptions": [
    {{"duration": 3, "description": "What to show visually", "text_overlay": "Short on-screen text"}},
    ...
  ],
  "call_to_action": "Download now on the App Store",
  "hook": "Opening 3-second hook statement"
}}

Scene descriptions should map to the uploaded screenshots in order.
Keep language energetic and benefit-focused. Match the {style} tone."""


def generate_script(
    app_name: str,
    description: str,
    category: str,
    keywords: list[str],
    style_theme: str,
    target_store: str,
    num_screenshots: int = 4,
    duration: int = 25,
) -> dict:
    prompt = SCRIPT_TEMPLATE.format(
        duration=duration,
        app_name=app_name,
        category=category or "App",
        style=style_theme,
        store=target_store,
        description=description or "",
        keywords=", ".join(keywords or []),
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    try:
        script = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: extract JSON from response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        script = json.loads(raw[start:end])

    # Ensure scene_descriptions has entries for each screenshot
    scenes = script.get("scene_descriptions", [])
    while len(scenes) < num_screenshots:
        scenes.append({"duration": 3, "description": "App screenshot", "text_overlay": ""})
    script["scene_descriptions"] = scenes[:num_screenshots]

    return script
