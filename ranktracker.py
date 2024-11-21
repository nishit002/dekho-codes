import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime

# Use Streamlit secrets to securely fetch the API key
SCRAPERAPI_KEY = st.secrets["SCRAPERAPI_KEY"]

# Function to encode uule for location-based search
def get_uule(latitude, longitude):
    loc_string = f"w+CAIQICI{latitude},{longitude}"
    uule_encoded = base64.urlsafe_b64encode(loc_string.encode()).decode('utf-8').rstrip('=')
    return uule_encoded

# Function to scrape Google SERP
def scrape_keyword(keyword, primary_site, competitors, latitude, longitude):
    uule = get_uule(latitude, longitude)
    api_url = f'http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url=https://www.google.com/search?q={keyword}&gl=in&hl=en&uule={uule}&num=100&device=mobile'
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15A372 Safari/604.1'
    }

    for attempt in range(3):
        try:
            response = requests.get(api_url, headers=headers, timeout=60)
            if response.status_code == 200:
                return response.text
        except:
            time.sleep(2)
    return None

# Streamlit App
def main():
    st.title("Google SERP Ranking Scraper")
    st.write("Upload an Excel file with keywords and specify the primary website and competitors to extract ranking details.")

    # File uploader for keywords
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    primary_site = st.text_input("Enter Primary Website (e.g., collegedekho.com)")
    competitors_input = st.text_input("Enter Competitor Websites (comma-separated, e.g., getmyuni.com,shiksha.com)")
    latitude = st.number_input("Enter Latitude", value=28.4595)
    longitude = st.number_input("Enter Longitude", value=77.0266)
    max_workers = st.slider("Number of Parallel Requests", min_value=1, max_value=20, value=10)

    if st.button("Start Scraping"):
        if uploaded_file and primary_site:
            keywords_df = pd.read_excel(uploaded_file)
            if 'Keyword' not in keywords_df.columns:
                st.error("Uploaded file must have a 'Keyword' column.")
                return

            # Parse competitors
            competitors = [comp.strip() for comp in competitors_input.split(',') if comp.strip()]

            if not competitors:
                st.error("Please enter at least one competitor.")
                return

            keywords = keywords_df['Keyword'].tolist()
            total_keywords = len(keywords)
            results = []
            progress = 0

            # Scraping process
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(scrape_keyword, keyword, primary_site, competitors, latitude, longitude): keyword
                    for keyword in keywords
                }

                for idx, future in enumerate(as_completed(futures)):
                    keyword = futures[future]
                    html = future.result()
                    if html:
                        # Process and extract data here
                        pass

                    # Update progress
                    progress = ((idx + 1) / total_keywords) * 100
                    st.progress(int(progress))

if __name__ == "__main__":
    main()
