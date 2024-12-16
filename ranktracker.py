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
def scrape_keywords_batch(keywords_batch, primary_site, competitors):
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
def extract_ranking_from_html(html, primary_site, competitors, keywords_batch):
    soup = BeautifulSoup(html, 'html.parser')
    search_results = soup.find_all('div', class_='tF2Cxc')  # Google SERP search result container
    rank_counter = 0
    results = []

    for keyword in keywords_batch:
        keyword_found = False
        primary_rank = None
        primary_url = None
        competitor_ranks = []

        for result in search_results:
            link_element = result.find('a')
            if link_element:
                rank_counter += 1
                link = link_element['href']

                # Check for primary website ranking
                if primary_site in link and not primary_rank:
                    primary_rank = rank_counter
                    primary_url = link
                    keyword_found = True

                # Check for competitor rankings (if competitors exist)
                if competitors:
                    for comp in competitors:
                        if comp in link:
                            competitor_ranks.append({
                                "Competitor": comp,
                                "Rank": rank_counter,
                                "URL": link
                            })
                            keyword_found = True

        # Append results for each keyword
        if keyword_found:
            results.append({
                "Keyword": keyword,
                "Primary Rank": primary_rank,
                "Primary URL": primary_url,
                "Competitors": competitor_ranks
            })
    return results

# Streamlit App
def main():
    st.title("Google SERP Ranking Scraper (Optimized)")
    st.write("Upload an Excel file or paste keywords to extract ranking details for a primary website with optional competitors.")

    # Options for keyword input
    input_option = st.radio(
        "Choose Keyword Input Method:",
        ("Upload Excel File", "Paste Keywords in Text Box")
    )

    # Variables to store keywords
    keywords = []

    if input_option == "Upload Excel File":
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
        if uploaded_file:
            keywords_df = pd.read_excel(uploaded_file)
            if 'Keyword' in keywords_df.columns:
                keywords = keywords_df['Keyword'].tolist()
            else:
                st.error("Uploaded file must have a 'Keyword' column.")
    elif input_option == "Paste Keywords in Text Box":
        pasted_text = st.text_area("Paste Keywords (one per line)")
        if pasted_text.strip():
            keywords = [kw.strip() for kw in pasted_text.split('\n') if kw.strip()]

    # Inputs for primary site and competitors
    primary_site = st.text_input("Enter Primary Website (e.g., collegedekho.com)")
    competitors_input = st.text_input("Enter Competitor Websites (comma-separated, optional)")
    competitors = [comp.strip() for comp in competitors_input.split(',') if comp.strip()]

    # Slider for parallel requests and batch size
    max_workers = st.slider("Number of Parallel Requests", min_value=1, max_value=10, value=5)
    batch_size = st.slider("Batch Size (Keywords per Request)", min_value=5, max_value=20, value=10)

    if st.button("Start Scraping"):
        if not keywords:
            st.error("Please provide keywords either by uploading a file or pasting them in the text box.")
            return
        if not primary_site:
            st.error("Please enter the primary website.")
            return

        total_keywords = len(keywords)
        results = []
        progress = 0

        # Split keywords into batches
        keyword_batches = [keywords[i:i + batch_size] for i in range(0, len(keywords), batch_size)]

        # Scraping process
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(scrape_keywords_batch, batch, primary_site, competitors): batch
                for batch in keyword_batches
            }

            for idx, future in enumerate(as_completed(futures)):
                batch = futures[future]
                html = future.result()
                if html:
                    # Extract rankings for the batch
                    batch_results = extract_ranking_from_html(html, primary_site, competitors, batch)
                    results.extend(batch_results)

                # Update progress
                progress = ((idx + 1) / len(keyword_batches)) * 100
                st.progress(int(progress))

        # Save results
        if results:
            flat_results = []
            for result in results:
                entry = {
                    "Keyword": result["Keyword"],
                    "Primary Rank": result["Primary Rank"],
                    "Primary URL": result["Primary URL"]
                }
                # Add competitor rankings
                if competitors:
                    for comp in result["Competitors"]:
                        entry[f"{comp['Competitor']} Rank"] = comp["Rank"]
                        entry[f"{comp['Competitor']} URL"] = comp["URL"]
                flat_results.append(entry)

            results_df = pd.DataFrame(flat_results)
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
            st.warning("No ranking data found for the primary site.")

if __name__ == "__main__":
    main()
