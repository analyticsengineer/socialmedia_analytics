# Post_Analytics.py
import streamlit as st
from notion_client import Client
import pandas as pd
import os

# ---- NOTION SETUP ----
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

# ---- FETCH POSTS ----
def fetch_posts():
    results = notion.databases.query(database_id=DATABASE_ID)
    posts = []
    for page in results["results"]:
        props = page["properties"]
        posts.append({
            "Post title": props["Post title"]["title"][0]["text"]["content"] if props["Post title"]["title"] else "",
            "Platform": props["Platform"]["select"]["name"] if props["Platform"]["select"] else "",
            "Post type": props["Post type"]["select"]["name"] if props["Post type"]["select"] else "",
            "Content": props["Content"]["select"]["name"] if props["Content"]["select"] else "",
            "Date": props["Date"]["date"]["start"] if props["Date"]["date"] else "",
            "Reach": props["Reach"]["number"] if props["Reach"]["number"] else 0,
            "Likes": props["Likes"]["number"] if props["Likes"]["number"] else 0,
            "Comments": props["Comments"]["number"] if props["Comments"]["number"] else 0,
            "Shares": props["Shares"]["number"] if props["Shares"]["number"] else 0,
            "Saves": props["Saves"]["number"] if props["Saves"]["number"] else 0,
        })
    df = pd.DataFrame(posts)
    if not df.empty:
        df["Total Engagement"] = df["Likes"] + df["Comments"] + df["Shares"] + df["Saves"]
        df["Engagement Rate"] = df.apply(lambda x: (x["Total Engagement"]/x["Reach"]*100) if x["Reach"] else 0, axis=1)
    return df

# ---- STREAMLIT APP ----
st.title("Post Analytics Dashboard")
df = fetch_posts()

st.dataframe(df)

st.markdown("### Summary")
st.write(f"Total Posts: {len(df)}")
st.write(f"Average Reach: {int(df['Reach'].mean())}")
st.write(f"Average Engagement Rate: {df['Engagement Rate'].mean():.2f}%")
