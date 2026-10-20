import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_video_content(topic: str, duration: str, tone: str) -> dict:
    is_short_format = "Shorts" in duration or "Reel" in duration
    scene_count = 5 if is_short_format else 7

    prompt = f"""
Create a professional AI video content package.

Topic: {topic}
Duration: {duration}
Tone: {tone}

Return only valid JSON.

Use exactly this structure:
{{
    "viral_titles": ["title 1", "title 2", "title 3"],
    "video_script": {{
        "hook": "engaging opening hook",
        "intro": "short introduction",
        "outro": "strong conclusion with call to action"
    }},
    "storyboard": [
        {{
            "scene_number": 1,
            "narration": "voiceover narration",
            "visual_prompt": "ultra short 5-6 word exact visual description matching this scene for AI image generation"
        }}
    ],
    "seo_metadata": {{
        "description": "SEO optimized YouTube description",
        "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
    }}
}}

Requirements:
- Generate exactly 3 viral titles.
- Generate exactly {scene_count} storyboard scenes.
- Every scene must contain meaningful narration and a unique visual_prompt tailored to a {tone} vibe.
- Each visual_prompt must be extremely concise (max 6 words) so the image generator creates an exact matching visual without failing.
- Return only the JSON object without markdown.
"""

    models_to_try = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-20b"
    ]

    response_content = None
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict JSON response generator. Return only valid JSON without markdown or additional explanation."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_completion_tokens=6000
            )
            response_content = response.choices[0].message.content
            if response_content:
                break
        except Exception as e:
            last_error = str(e)
            continue

    if not response_content:
        return {"error": f"All models failed. Last error: {last_error}"}

    try:
        response_content = response_content.strip()
        if response_content.startswith("```json"):
            response_content = response_content.replace("```json", "", 1)
        if response_content.startswith("```"):
            response_content = response_content.replace("```", "", 1)
        if response_content.endswith("```"):
            response_content = response_content.rsplit("```", 1)[0]

        response_content = response_content.strip()
        start_index = response_content.find("{")
        end_index = response_content.rfind("}")

        if start_index == -1 or end_index == -1:
            return {"error": "Invalid JSON response structure returned by AI."}

        json_content = response_content[start_index:end_index + 1]
        data = json.loads(json_content)

        if not data.get("viral_titles"):
            data["viral_titles"] = [f"Discover {topic}", f"The Story Behind {topic}", f"Everything About {topic}"]

        if not data.get("video_script"):
            data["video_script"] = {
                "hook": f"Discover the fascinating world of {topic}.",
                "intro": f"Welcome to this story about {topic}.",
                "outro": "Thank you for watching. Subscribe for more amazing content."
            }

        if not data.get("seo_metadata"):
            data["seo_metadata"] = {}

        seo_metadata = data["seo_metadata"]
        if not seo_metadata.get("description"):
            seo_metadata["description"] = f"Explore {topic} in this engaging video. Designed in a {tone.lower()} style."

        if not seo_metadata.get("tags"):
            seo_metadata["tags"] = [topic.lower(), "ai video", "cinematic video", "storytelling", "viral video", "youtube"]

        return data

    except json.JSONDecodeError as error:
        return {"error": f"Invalid JSON received from AI: {str(error)}"}
    except Exception as error:
        return {"error": str(error)}