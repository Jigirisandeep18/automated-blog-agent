import os
import pandas as pd

def safe_flatten(df, max_items=None):
    """Flatten dataframe values into a unique list of strings."""
    if df is None or df.empty:
        return []
    s = df.astype(str).apply(lambda col: col.str.strip()).stack().dropna()
    s = s[s.str.lower() != "nan"]
    out = []
    for v in s:
        v = v.strip()
        if v == "" or v.lower() in ("nan", "none"):
            continue
        if v not in out:
            out.append(v)
        if max_items and len(out) >= max_items:
            break
    return out

def map_keywords_and_deeplinks(topics, seo_keywords, llm_keywords, deeplinks):
    mapped_topics = []
    for topic in topics:
        topic_lower = topic["topic"].lower()
        description_lower = topic["description"].lower()

        relevant_seo = [kw for kw in seo_keywords if kw.lower() in topic_lower][:5]
        relevant_llm = [kw for kw in llm_keywords if kw.lower() in description_lower][:5]

        mapped_topics.append({
            "topic": topic["topic"],
            "description": topic["description"],
            "seo_keywords": relevant_seo or seo_keywords[:5],
            "llm_keywords": relevant_llm or llm_keywords[:5],
            "deeplinks": deeplinks[:5]  # Simplified mapping
        })

    return mapped_topics

def clean_and_save(data_dir="data"):
    seo_path = os.path.join(data_dir, "seo_-_keywords.csv")
    llm_path = os.path.join(data_dir, "llm_-_keywords.csv")
    website_path = os.path.join(data_dir, "website.csv")
    topics_path = os.path.join(data_dir, "key_topics.csv")

    def _read(p):
        try:
            return pd.read_csv(p)
        except Exception:
            return pd.DataFrame()

    seo_df = _read(seo_path)
    llm_df = _read(llm_path)
    website_df = _read(website_path)
    topics_df = _read(topics_path)

    seo_keywords = safe_flatten(seo_df, max_items=30)
    llm_keywords = safe_flatten(llm_df, max_items=30)

    deeplinks = []
    if not website_df.empty:
        if "URL" in website_df.columns:
            deeplinks = website_df["URL"].dropna().astype(str).tolist()
        elif "Link" in website_df.columns:
            deeplinks = website_df["Link"].dropna().astype(str).tolist()
        else:
            first_col = website_df.columns[0]
            deeplinks = website_df[first_col].dropna().astype(str).tolist()

    topics = []
    if not topics_df.empty:
        title_col = None
        desc_col = None

        for c in topics_df.columns:
            cname = c.strip().lower()
            if "topic" in cname:
                title_col = c
            if "description" in cname:
                desc_col = c

        if title_col is None and len(topics_df.columns) >= 1:
            title_col = topics_df.columns[0]
        if desc_col is None and len(topics_df.columns) >= 2:
            desc_col = topics_df.columns[1]

        for _, row in topics_df.iterrows():
            title = str(row.get(title_col, "")).strip()
            desc = str(row.get(desc_col, "")).strip() if desc_col else ""
            if title and title.lower() not in ("nan", "none"):
                topics.append({"topic": title, "description": desc})

    # Perform mapping
    mapped_topics = map_keywords_and_deeplinks(topics, seo_keywords, llm_keywords, deeplinks)

    # Save cleaned lists
    os.makedirs(data_dir, exist_ok=True)
    pd.DataFrame({"keyword": seo_keywords}).to_csv(os.path.join(data_dir, "clean_seo_keywords.csv"), index=False)
    pd.DataFrame({"keyword": llm_keywords}).to_csv(os.path.join(data_dir, "clean_llm_keywords.csv"), index=False)
    pd.DataFrame({"deeplink": deeplinks}).to_csv(os.path.join(data_dir, "clean_deeplinks.csv"), index=False)
    pd.DataFrame(mapped_topics).to_csv(os.path.join(data_dir, "clean_topics.csv"), index=False)

    return {
        "seo_keywords": seo_keywords,
        "llm_keywords": llm_keywords,
        "deeplinks": deeplinks,
        "topics": mapped_topics
    }

if __name__ == "__main__":
    out = clean_and_save()
    print("Cleaned data summary:")
    print(f"- SEO keywords: {len(out['seo_keywords'])}")
    print(f"- LLM keywords: {len(out['llm_keywords'])}")
    print(f"- Deeplinks: {len(out['deeplinks'])}")
    print(f"- Topics: {len(out['topics'])}")
    if out["topics"]:
        print("Sample mapped topic:", out["topics"][0])
