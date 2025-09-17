import os
import re
import pandas as pd
from data_cleaning import clean_and_save
from blog_generator import generate_blog
from google_sheets import append_blog

def ensure_dirs(d):
    os.makedirs(d, exist_ok=True)

def save_blog_to_files(blog_md: str, topic: str, out_dir="outputs"):
    ensure_dirs(out_dir)
    safe_name = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in topic)[:60].strip().replace(" ", "_")
    filename = f"{safe_name}.md"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(blog_md)
    return path

def append_metadata(metadata: dict, out_dir="outputs"):
    ensure_dirs(out_dir)
    meta_path = os.path.join(out_dir, "blogs_metadata.csv")
    df = pd.DataFrame([metadata])
    if os.path.exists(meta_path):
        df_existing = pd.read_csv(meta_path)
        df_final = pd.concat([df_existing, df], ignore_index=True)
        df_final.to_csv(meta_path, index=False)
    else:
        df.to_csv(meta_path, index=False)
    return meta_path

def extract_meta(blog_md: str):
    title_match = re.search(r"<meta_title>:\s*(.*)", blog_md)
    desc_match = re.search(r"<meta_description>:\s*(.*)", blog_md)
    return {
        "meta_title": title_match.group(1) if title_match else "",
        "meta_description": desc_match.group(1) if desc_match else ""
    }

def main():
    print("1) Cleaning data and extracting lists...")
    data = clean_and_save()
    topics = data.get("topics", [])

    if not topics:
        print("❌ No topics found - add topic rows in the Key Insights Excel 'key topics' sheet.")
        return

    print(f"✅ Found {len(topics)} topics to process.")

    for idx, topic_entry in enumerate(topics):
        topic = topic_entry["topic"]
        description = topic_entry["description"]
        print(f"\n👉 Generating blog #{idx + 1}: {topic}")

        blog_md = generate_blog(
            topic,
            description,
            data["seo_keywords"],
            data["llm_keywords"],
            data["deeplinks"]
        )

        saved_path = save_blog_to_files(
            blog_md,
            topic,
            out_dir=os.path.join(os.getcwd(), "outputs")
        )
        print(f"✅ Blog saved at: {saved_path}")

        extracted_meta = extract_meta(blog_md)

        metadata = {
            "topic": topic,
            "title_meta": extracted_meta["meta_title"],
            "meta_description": extracted_meta["meta_description"],
            "seo_keywords": ";".join(data["seo_keywords"][:8]),
            "llm_keywords": ";".join(data["llm_keywords"][:8]),
            "deeplinks_used": ";".join(data["deeplinks"][:5]),
            "file_path": saved_path
        }

        meta_csv = append_metadata(
            metadata,
            out_dir=os.path.join(os.getcwd(), "outputs")
        )
        print(f"✅ Metadata updated at: {meta_csv}")

        # === NEW STEP: Push to Google Sheets ===
        row_data = [
            topic,
            extracted_meta["meta_title"],
            extracted_meta["meta_description"],
            ", ".join(data["seo_keywords"][:8]),
            ", ".join(data["llm_keywords"][:8]),
            ", ".join(data["deeplinks"][:5]),
            blog_md,
            "Q: Sample FAQ?\nA: Sample answer.",  # can be parsed later
            "Contact us to learn more."           # CTA
        ]
        append_blog(row_data)

    print("\n🎉 All topics processed and uploaded to Google Sheets successfully.")

if __name__ == "__main__":
    main()
