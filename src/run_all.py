import os
import pandas as pd
from data_ingestion import ingest_excel
from blog_generator import generate_blog
from google_sheets import append_blog

def save_blog_to_file(topic, blog_md, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in topic)[:60].strip().replace(" ", "_")
    file_path = os.path.join(output_dir, f"{safe_name}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(blog_md)
    print(f"✅ Blog saved: {file_path}")
    return file_path

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(__file__))
    input_file = os.path.join(project_root, "input", "Key Insights.xlsx")
    data_dir = os.path.join(project_root, "data")

    # Step 1 – Ingest Excel and extract sheets as CSV
    ingest_excel(input_file=input_file, output_dir=data_dir)

    # Step 2 – Load key topics CSV
    topics_csv = os.path.join(data_dir, "key_topics.csv")
    if not os.path.exists(topics_csv):
        print(f"❌ Missing {topics_csv}")
        exit(1)

    df = pd.read_csv(topics_csv)
    print(f"🚀 Loaded {len(df)} topics.")

    for index, row in df.iterrows():
        topic = row.get("Topic")
        description = row.get("Description")

        if not topic or not description:
            print(f"⚠️ Skipping empty topic at row {index}")
            continue

        print(f"👉 Generating blog for topic: {topic}")

        # Step 3 – Generate blog content (mock or real depending on config)
        blog_md = generate_blog(
            topic=topic,
            description=description,
            seo_keywords=[],      # Adjust if you have these available
            llm_keywords=[],
            deeplinks=[]
        )

        # Step 4 – Save generated blog to a markdown file
        blog_path = save_blog_to_file(topic, blog_md)

        # Step 5 – Append blog metadata + content to Google Sheets
        meta_title = ""         # Could parse from blog_md if available
        meta_description = ""   # Same as above

        row_data = [
            topic,
            meta_title,
            meta_description,
            "", "", "",  # SEO, LLM, Deeplinks (empty or later logic)
            blog_md,
            "",          # FAQs
            "Contact us to learn more."  # CTA
        ]

        append_blog(row_data)

    print("🎉 All blogs processed and uploaded successfully.")
