import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime

# Function to process uploaded file and handle case-insensitive columns
def process_uploaded_file(uploaded_file):
    try:
        # Read the uploaded Excel file
        df = pd.read_excel(uploaded_file)

        # Normalize column names (convert to lowercase for case-insensitivity)
        df.columns = df.columns.str.lower()

        # Ensure 'keyword' and 'url' columns are present
        if 'keyword' not in df.columns or 'url' not in df.columns:
            st.error("Uploaded file must have 'Keyword' and 'URL' columns.")
            return None

        # Return the keywords and URLs as a list of tuples
        return df[['keyword', 'url']].values.tolist()

    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# Function to scrape Google SERP for a batch of keywords
def scrape_keywords_batch(keywords_batch):
    combined_query = '+OR+'.join([kw.replace(" ", "+") for kw in keywords_batch])
    api_url = f"https://www.google.com/search?q={combined_query}&num=100&gl=in&hl=en&device=mobile"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15A372 Safari/604.1'
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=30)
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
        # Process the uploaded file
        keywords_and_urls = process_uploaded_file(uploaded_file)
        if keywords_and_urls:
            st.success(f"File uploaded successfully with {len(keywords_and_urls)} rows.")

    # Slider for parallel requests and batch size
    max_workers = st.slider("Number of Parallel Requests", min_value=1, max_value=10, value=5)
    batch_size = st.slider("Batch Size (Keywords per Request)", min_value=5, max_value=20, value=10)

    if st.button("Start Scraping"):
        if not keywords_and_urls:
            st.error("Please upload a valid file with 'Keyword' and 'URL' columns.")
            return

        total_keywords = len(keywords_and_urls)
        results = []
        urls_checked = 0  # Counter for URLs checked

        # Split keywords and URLs into batches
        keyword_batches = [keywords_and_urls[i:i + batch_size] for i in range(0, len(keywords_and_urls), batch_size)]

        # Scraping process
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(scrape_keywords_batch, [kw[0] for kw in batch]): batch
                for batch in keyword_batches
            }

            for future in as_completed(futures):
                batch = futures[future]
                html = future.result()
                if html:
                    # Extract rankings for the batch
                    batch_results = extract_ranking_from_html(html, batch)
                    results.extend(batch_results)
                    urls_checked += len(batch)  # Update count of URLs checked
                    st.write(f"URLs Checked: {urls_checked}")  # Display count

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
