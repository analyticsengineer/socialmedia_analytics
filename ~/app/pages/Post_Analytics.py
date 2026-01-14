import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date

# Load environment variables
load_dotenv()

# Notion setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")  # Page containing your inline database

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Function to find the first inline database in the page
def get_inline_database_id(page_id):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=50"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        st.error(f"❌ Failed to fetch page blocks: {response.status_code} {response.text}")
        return None
    blocks = response.json().get("results", [])
    for block in blocks:
        if block.get("type") == "child_database":
            return block["id"]
    st.info("No inline database found on this page.")
    return None

# Function to add a post to the database
def add_post(data, database_id):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Post title": {"title": [{"text": {"content": data["title"]}}]},
            "Platform": {"select": {"name": data["platform"]}},
            "Post type": {"select": {"name": data["post_type"]}},
            "Content": {"select": {"name": data["content"]}},
            "Date": {"date": {"start": data["date"]}},
            "Reach": {"number": data["reach"]},
            "Impressions": {"number": data["impressions"]},
            "Likes": {"number": data["likes"]},
            "Comments": {"number": data["comments"]},
            "Shares": {"number": data["shares"]},
            "Saves": {"number": data["saves"]},
            "Repost": {"number": data["repost"]}
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code not in [200, 201]:
        st.error(f"❌ Error {response.status_code}: {response.text}")
        return False
    return True

# --- Page UI ---
st.set_page_config(page_title="📊 Post Analytics", layout="centered")
st.title("📈 Log Social Media Post Analytics")

# Form default values
default_values = {
    "title": "",
    "platform": "",
    "post_type": "",
    "content": "",
    "date": date.today(),
    "reach_str": "",
    "impressions_str": "",
    "likes_str": "",
    "comments_str": "",
    "shares_str": "",
    "saves_str": "",
    "repost_str": ""
}

# Initialize session state
for key, val in default_values.items():
    st.session_state.setdefault(key, val)
st.session_state.setdefault("submitted", False)

# Clear form if just submitted
if st.session_state.submitted:
    for key in default_values:
        st.session_state[key] = default_values[key]
    st.session_state.submitted = False
    st.success("✅ Post logged successfully!")

# --- Form ---
with st.form("post_analytics_form"):
    st.text_input("Post Title", key="title")
    st.selectbox("Platform", ["X", "Threads", "Instagram", "LinkedIn", "Facebook", "Snapchat", "TikTok"], key="platform")
    st.selectbox("Post Type", ["Image", "Story", "Carousel", "Text", "Video", "Reel"], key="post_type")
    st.selectbox("Content Type", ["Job recruitment", "Webinars", "Entertainment", "Personal", "Promotion", "Data/Insights", "Announcement", "Education"], key="content")
    date_value = st.date_input("Date", value=st.session_state.date)
    st.text_input("Reach", key="reach_str")
    st.text_input("Impressions", key="impressions_str")
    st.text_input("Likes", key="likes_str")
    st.text_input("Comments", key="comments_str")
    st.text_input("Shares", key="shares_str")
    st.text_input("Saves", key="saves_str")
    st.text_input("Repost", key="repost_str")
    submit = st.form_submit_button("Submit")

    if submit:
        try:
            data = {
                "title": st.session_state.title,
                "platform": st.session_state.platform,
                "post_type": st.session_state.post_type,
                "content": st.session_state.content,
                "date": str(date_value),
                "reach": int(st.session_state.reach_str.replace(",", "")),
                "impressions": int(st.session_state.impressions_str.replace(",", "")),
                "likes": int(st.session_state.likes_str.replace(",", "")),
                "comments": int(st.session_state.comments_str.replace(",", "")),
                "shares": int(st.session_state.shares_str.replace(",", "")),
                "saves": int(st.session_state.saves_str.replace(",", "")),
                "repost": int(st.session_state.repost_str.replace(",", ""))
            }

            db_id = get_inline_database_id(NOTION_PAGE_ID)
            if db_id:
                success = add_post(data, db_id)
                if success:
                    st.session_state.submitted = True
                    st.experimental_rerun()
        except ValueError:
            st.error("❌ Invalid number format. Use numbers only (e.g., 5000).")
