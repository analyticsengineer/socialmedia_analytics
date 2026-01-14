# Post_Analytics.py
import streamlit as st
from notion_client import Client
import pandas as pd
import os

# ---- NOTION SETUP ----
# Use environment variables or Streamlit Secrets
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    st.error("Notion token or database ID missing. Please set them as environment variables or in Streamlit secrets.")
    st.stop()

notion = Client(auth=NOTION_TOKEN)

# ---- FUNCTION TO FETCH DATABASE ENTRIES ----
def fetch_posts():
    posts = []
    try:
        results = notion.databases.query(database_id=DATABASE_ID)
        for page in results.get("results", []):
            props = page.get("properties", {})
            posts.append({
                "Post title": props.get("Post title", {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                "Platform": props.get("Platform", {}).get("select", {}).get("name", ""),
                "Post type": props.get("Post type", {}).get("select", {}).get("name", ""),
                "Content": props.get("Content", {}).get("select", {}).get("name", ""),
                "Date": props.get("Date", {}).get("date", {}).get("start", ""),
                "Reach": props.get("Reach", {}).get("number", 0),
                "Impressions": props.get("Impressions", {}).get("number", 0),
                "Likes": props.get("Likes", {}).get("number", 0),
                "Comments": props.get("Comments", {}).get("number", 0),
                "Shares": props.get("Shares", {}).get("number", 0),
                "Saves": props.get("Saves", {}).get("number", 0),
                "Repost": props.get("Repost", {}).get("number", 0),
            })
    except Exception as e:
        st.error(f"Error fetching data from Notion: {e}")
        return pd.DataFrame()

    df = pd.DataFrame(posts)

    if not df.empty:
        df["Total Engagement"] = df["Likes"] + df["Comments"] + df["Shares"] + df["Saves"]
        df["Engagement Rate"] = df.apply(
            lambda x: (x["Total Engagement"] / x["Reach"] * 100) if x["Reach"] else 0, axis=1
        )

    return df

# ---- STREAMLIT APP ----
st.title("Post Analytics Dashboard")

df = fetch_posts()

if df.empty:
    st.info("No posts found in the Notion database.")
else:
    # Display table
    st.dataframe(df)

    # Display summary metrics
    st.markdown("### Summary")
    st.metric("Total Posts", len(df))
    st.metric("Average Reach", int(df["Reach"].mean()))
    st.metric("Average Engagement Rate", f"{df['Engagement Rate'].mean():.2f}%")

    # Optional: bar chart for engagement by platform
    st.markdown("### Total Engagement by Platform")
    platform_df = df.groupby("Platform")["Total Engagement"].sum().reset_index()
    st.bar_chart(platform_df.rename(columns={"Platform": "index"}).set_index("index"))
