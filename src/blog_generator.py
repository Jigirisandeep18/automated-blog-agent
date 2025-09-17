import os
import yaml
import openai
from typing import List


def load_config(path="config/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_prompt(topic: str, description: str, seo_keywords: List[str], llm_keywords: List[str], deeplinks: List[str]):
    seo_sample = ", ".join(seo_keywords[:8]) if seo_keywords else "None"
    llm_sample = ", ".join(llm_keywords[:8]) if llm_keywords else "None"
    deeplink_sample = "\n".join([f"- {u}" for u in deeplinks[:6]]) if deeplinks else "None"

    prompt = f"""
You are an expert SEO blog writer and LLM-friendly content creator.

Topic: {topic}
Brief: {description}

Primary instructions (strict):
- Produce full long-form blog in Markdown.
- Start with a meta title (<=70 chars) and meta description (<=160 chars).
- Use H1 for title, H2/H3 for subheadings.
- Include 2-3 image placeholders with suggested alt text (format: [Image: alt text]).
- Include an FAQ section (3–5 Q&A).
- End with a strong call-to-action (1 short paragraph).
- Naturally use the provided SEO keywords and LLM keywords; keep keyword stuffing out — use them logically.

SEO Keywords (sample): {seo_sample}
LLM Keywords (sample): {llm_sample}

Use these internal links where relevant:
{deeplink_sample}

Required output format in Markdown:
---
<meta_title>: <meta title here>
<meta_description>: <meta description here>

# <Main blog title>
<blog body here with headings, images, links, FAQ, CTA>

--- 
Write in an informative, authoritative tone, accessible to both technical and non-technical readers.
"""
    return prompt


def generate_blog(topic, description, seo_keywords, llm_keywords, deeplinks, config_path="config/config.yaml"):
    cfg = load_config(config_path)
    mock = cfg.get("mock_mode", True)

    prompt = build_prompt(topic, description, seo_keywords, llm_keywords, deeplinks)

    if mock:
        meta_title = f"{topic} — Key insights"
        meta_desc = f"Short summary: {description[:120]}"
        body = f"# {topic}\n\n{description}\n\n## Overview\nThis is a mocked blog for testing the pipeline. Use real OpenAI in production.\n\n[Image: illustrative image for {topic}]\n\n## FAQ\nQ: What is {topic}?\nA: Brief answer.\n\n**CTA:** Contact us to learn more."
        full = f"<meta_title>: {meta_title}\n<meta_description>: {meta_desc}\n\n{body}"
        return full

    openai.api_key = cfg.get("openai_api_key")
    model = cfg.get("model_name", "gpt-5")

    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert SEO blog writer and content strategist."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=3000,
            temperature=0.2,
        )
        content = resp["choices"][0]["message"]["content"].strip()
        return content

    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return f"# {topic}\n\nFailed to generate blog due to API error."


if __name__ == "__main__":
    # Local test example
    from data_cleaning import clean_and_save

    data = clean_and_save()
    topics = data["topics"]
    if not topics:
        print("❌ No topics found in data.")
    else:
        out = generate_blog(
            topic=topics[0]["topic"],
            description=topics[0]["description"],
            seo_keywords=data["seo_keywords"],
            llm_keywords=data["llm_keywords"],
            deeplinks=data["deeplinks"]
        )
        print("=== GENERATED OUTPUT SAMPLE ===")
        print(out[:2000])  # Show first 2000 characters
