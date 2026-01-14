# Post_Analytics.py
import streamlit as st
from notion_client import Client
import pandas as pd
import os

# ---- NOTION SETUP ----
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
PAGE_ID = os.getenv("NOTION_PAGE_ID")  # page containing inline database

if not NOTION_TOKEN or not PAGE_ID:
    st.error("Please set NOTION_TOKEN and NOTION_PAGE_ID in environment variables or Streamlit secrets.")
    st.stop()

notion = Client(auth=NOTION_TOKEN)

# ---- FETCH INLINE DATABASE ----
def fetch_inline_database(page_id):
    posts = []

    # Use the correct method in latest SDK
    blocks = notion.blocks.children.list(block_id=page_id)  # block_id instead of page_id
    for block in blocks["results"]:
        if block["type"] == "child_database":
            db_id = block["id"]
            rows = notion.databases.query(database_id=db_id)
            for page in rows.get("results", []):
                props = page["properties"]
                posts.append({
                    "Post title": props.get("Post title", {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                    "Platform": props.get("Platform", {}).get("select", {}).get("name", ""),
                    "Post type": props.get("Post type", {}).get("select", {}).get("name", ""),
                    "Content": props.get("Content", {}).get("select", {}).get("name", ""),
                    "Date": props.get("Date", {}).get("date", {}).get("start", ""),
                    "Reach": props.get("Reach", {}).get("number", 0),
                    "Likes": props.get("Likes", {}).get("number", 0),
                    "Comments": props.get("Comments", {}).get("number", 0),
                    "Shares": props.get("Shares", {}).get("number", 0),
                    "Saves": props.get("Saves", {}).get("number", 0),
                    "Repost": props.get("Repost", {}).get("number", 0),
                })
            break  # only first inline database

    df = pd.DataFrame(posts)
    if not df.empty:
        df["Total Engagement"] = df["Likes"] + df["Comments"] + df["Shares"] + df["Saves"]
        df["Engagement Rate"] = df.apply(lambda x: (x["Total Engagement"]/x["Reach"]*100) if x["Reach"] else 0, axis=1)

    return df

# ---- STREAMLIT APP ----
st.title("Post Analytics Dashboard")

df = fetch_inline_database(PAGE_ID)

if df.empty:
    st.info("No posts found in the inline database.")
else:
    st.dataframe(df)
    st.markdown("### Summary")
    st.write(f"Total Posts: {len(df)}")
    st.write(f"Average Reach: {int(df['Reach'].mean())}")
    st.write(f"Average Engagement Rate: {df['Engagement Rate'].mean():.2f}%")
