import streamlit as st
import pandas as pd
from serpapi import GoogleSearch
from urllib.parse import urlparse

# Function to get the base domain from a URL (to avoid matching issues due to query params)
def get_base_domain(url):
    if not url.startswith("http"):  # Handle cases where 'http' or 'https' is missing
        url = "http://" + url  # Add a default scheme to ensure proper parsing
    parsed_url = urlparse(url)
    # Extract base domain, remove "www." if it exists
    domain = parsed_url.netloc.replace('www.', '')
    return domain

# Function to get SERP rank using SerpAPI directly from JSON response
def get_serp_rank_serpapi(keyword, target_websites, api_key):
    params = {
        "q": keyword,
        "num": 100,  # Get up to 100 results
        "device": "mobile",  # Use mobile search
        "gl": "in",  # Set location to India
        "hl": "en",  # Set language to English
        "uule": "w+CAIQICINV1JUwzBQbVlJMVyCF9ZYk9MQkFWTnA=",  # Approximate location for Gurgaon
        "api_key": api_key,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    rankings = {website: None for website in target_websites}

    if "organic_results" in results:
        for index, result in enumerate(results["organic_results"], 1):
            link = result["link"]
            base_link = get_base_domain(link)
            for website in target_websites:
                base_website = get_base_domain(website)
                if base_website == base_link and rankings[website] is None:  # Capture first instance only
                    rankings[website] = index

    return rankings

# Function to calculate pixel rank based on position on SERP
def calculate_pixel_rank(rank):
    if rank is None:
        return None
    return 100 + (rank - 1) * 60  # Assuming each result occupies 60 pixels

# Streamlit UI
st.title("🎯 Mobile Google SERP Crawler and Pixel Rank Calculator (SerpAPI)")
st.markdown("""
<style>
    .reportview-container {
        background: #f0f0f0;
        color: #333333;
    }
    .sidebar .sidebar-content {
        background: #f7f7f7;
    }
</style>
""", unsafe_allow_html=True)

# Step 1: API Key (entered directly in the code for local use)
api_key = st.text_input("Enter your SerpAPI Key", type="password")

# Step 2: File Upload
uploaded_file = st.file_uploader("Upload a CSV file with keywords", type=["csv"])

# Step 3: Input Competitors and Primary Website
competitors = st.text_input("Enter Competitor Websites (comma-separated)", placeholder="e.g., collegedekho.com, collegedunia.com, shiksha.com")
primary_website = st.text_input("Enter Primary Website", placeholder="e.g., yourwebsite.com")

if api_key and uploaded_file and competitors and primary_website:
    keywords_df = pd.read_csv(uploaded_file)

    if 'Keyword' not in keywords_df.columns:
        st.error("CSV file must contain 'Keyword' column")
    else:
        competitors_list = [primary_website] + [website.strip() for website in competitors.split(',')]

        # Initialize empty list to store results
        serp_data = []

        st.markdown("### 📊 Fetching Rankings...")
        
        for keyword in keywords_df['Keyword']:
            st.info(f"Fetching rankings for: **{keyword}**")
            rankings = get_serp_rank_serpapi(keyword, competitors_list, api_key)
            
            # Calculate pixel rank for primary website
            pixel_rank = calculate_pixel_rank(rankings[primary_website])
            
            # Store the data for each keyword
            row = [keyword] + [rankings[website] for website in competitors_list] + [pixel_rank]
            serp_data.append(row)

        # Create a DataFrame to display results
        columns = ['Keyword'] + [f'Ranking of {website}' for website in competitors_list] + ['Pixel Rank (Primary Website)']
        result_df = pd.DataFrame(serp_data, columns=columns)

        # Apply styling to the table
        def style_ranking(val):
            color = 'green' if pd.notnull(val) and val <= 10 else 'red'
            return f'color: {color}'
        
        st.markdown("### 🎯 SERP Rankings and Pixel Rank")
        styled_df = result_df.style.applymap(style_ranking, subset=[f'Ranking of {website}' for website in competitors_list])
        st.dataframe(styled_df)

        # Option to download results
        csv = result_df.to_csv(index=False)
        st.download_button(label="📥 Download Results as CSV", data=csv, mime="text/csv")
