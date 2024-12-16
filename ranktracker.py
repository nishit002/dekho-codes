import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import requests_cache

# Use Streamlit secrets to securely fetch the API key
SCRAPERAPI_KEY = st.secrets["SCRAPERAPI_KEY"]

# Setup caching to avoid redundant requests
session = requests_cache.CachedSession('google_serp_cache', expire_after=3600)

# Function to scrape Google SERP (batched keywords)
def scrape_keywords_batch(keywords_batch):
    combined_query = '+OR+'.join([kw.replace(" ", "+") for kw in keywords_batch])
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url=https://www.google.com/search?q={combined_query}&num=100&gl=in&hl=en&device=mobile"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15A372 Safari/604.1'
    }

    try:
        response = session.get(api_url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
    return None

# Function to extract rankings from HTML
def extract_ranking_from_html(html, keywords_and_urls):
    soup = BeautifulSoup(html, 'html.parser')
    search_results = soup.find_all('div', class_='tF2Cxc')  # Google SERP search result container
    results = []

    for keyword, provided_url in keywords_and_urls:
        rank_counter = 0
        primary_rank = None
        ranking_url = None

        for result in search_results:
            link_element = result.find('a')
            if link_element:
                rank_counter += 1
                link = link_element['href']

                # Check if ranking URL matches the provided URL
                if provided_url in link and not primary_rank:
                    primary_rank = rank_counter
                    ranking_url = link

        results.append({
            "Keyword": keyword,
            "Provided URL": provided_url,
            "Ranking URL": ranking_url,
            "Rank": primary_rank
        })

    return results

# Streamlit App
def main():
    st.title("Google SERP Ranking Scraper with URL Matching")
    st.write("Upload an Excel file to extract rankings for specific keywords and URLs.")

    # File uploader
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    keywords_and_urls = []

    if uploaded_file:
        keywords_df = pd.read_excel(uploaded_file)
        if {'Keyword', 'URL'}.issubset(keywords_df.columns.str.lower()):
            keywords_df.columns = keywords_df.columns.str.lower()
            keywords_and_urls = keywords_df[['keyword', 'url']].values.tolist()
        else:
            st.error("Uploaded file must have 'Keyword' and 'URL' columns.")

    # Inputs for parallel requests and batch size
    max_workers = st.slider("Number of Parallel Requests", min_value=1, max_value=10, value=5)
    batch_size = st.slider("Batch Size (Keywords per Request)", min_value=5, max_value=20, value=10)

    if st.button("Start Scraping"):
        if not keywords_and_urls:
            st.error("Please upload a file with valid 'Keyword' and 'URL' columns.")
            return

        total_keywords = len(keywords_and_urls)
        results = []
        progress = 0

        # Split keywords and URLs into batches
        keyword_batches = [keywords_and_urls[i:i + batch_size] for i in range(0, len(keywords_and_urls), batch_size)]

        # Scraping process
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(scrape_keywords_batch, [kw[0] for kw in batch]): batch
                for batch in keyword_batches
            }

            for idx, future in enumerate(as_completed(futures)):
                batch = futures[future]
                html = future.result()
                if html:
                    # Extract rankings for the batch
                    batch_results = extract_ranking_from_html(html, batch)
                    results.extend(batch_results)

                # Update progress
                progress = ((idx + 1) / len(keyword_batches)) * 100
                st.progress(int(progress))

        # Save results
        if results:
            results_df = pd.DataFrame(results)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"SERP_Ranking_Results_{timestamp}.xlsx"
            results_df.to_excel(output_file, index=False)

            st.success("Scraping Completed!")
            st.write("Download Results Below:")
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download Results",
                    data=file,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No ranking data found for the provided URLs.")

if __name__ == "__main__":
    main()
