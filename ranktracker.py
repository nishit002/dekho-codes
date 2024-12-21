import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import urllib.parse
import time
from urllib.parse import urlparse

# Function to process uploaded file and handle case-insensitive columns
def process_uploaded_file(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.lower()
        if 'keyword' not in df.columns:
            st.error("Uploaded file must have a 'Keyword' column.")
            return None
        if 'url' in df.columns:
            return df[['keyword', 'url']].values.tolist()
        else:
            return [(kw, None) for kw in df['keyword'].tolist()]
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# Function to scrape Google SERP using ScraperAPI
def scrape_google(keyword, site_search=None):
    SCRAPERAPI_KEY = st.secrets["SCRAPERAPI_KEY"]  # Get ScraperAPI key from Streamlit secrets
    query = urllib.parse.quote_plus(keyword)
    if site_search:
        query = f"site:{site_search} {query}"
    api_url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url=https://www.google.com/search?q={query}&num=100&gl=in&hl=en&device=mobile&uule=w+CAIQICIwMjguNDU5NSAwNzcuMDI2Ng"  # Gurgaon coordinates

    try:
        time.sleep(2)  # Add delay to avoid overloading ScraperAPI
        response = requests.get(api_url, timeout=30)
        st.write(f"Scraping Keyword: {keyword}")  # Debug
        st.write(f"Response Status Code: {response.status_code}")  # Debug
        if response.status_code == 200:
            return response.text
        else:
            st.warning(f"Failed to fetch data for keyword: {keyword}")
            st.write(response.text[:500])  # Debug: Print response content
    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
    return None

# Function to extract rankings
def extract_ranking(html, keyword, primary_domain, primary_url, competitors):
    soup = BeautifulSoup(html, "html.parser")
    search_results = soup.find_all("div", class_="tF2Cxc")  # Google SERP search result container
    st.write(f"HTML Parsed Results: {len(search_results)} found.")  # Debug
    rank_counter = 0
    primary_rank = None
    primary_ranking_url = None
    competitor_ranks = {comp: None for comp in competitors}  # Initialize all competitors with None
    best_url_rank = None
    best_url = None

    for result in search_results:
        rank_counter += 1
        link_element = result.find("a")
        if link_element:
            link = link_element["href"]
            domain = urlparse(link).netloc.lower()

            # Check for primary URL or domain
            if primary_url and primary_url in link and not primary_rank:
                primary_rank = rank_counter
                primary_ranking_url = link
            elif primary_domain in domain and not primary_rank:
                primary_rank = rank_counter
                primary_ranking_url = link

            # Check for competitor rankings
            for comp in competitors:
                if comp in domain:
                    # Keep the best-ranked URL for the competitor
                    if competitor_ranks[comp] is None or rank_counter < competitor_ranks[comp]["Rank"]:
                        competitor_ranks[comp] = {"Competitor": comp, "Rank": rank_counter, "URL": link}

            # Track the best URL
            if not best_url_rank or rank_counter < best_url_rank:
                best_url_rank = rank_counter
                best_url = link

    # Convert competitor_ranks to a list, replacing None with null entries
    competitors_list = [v if v else {"Competitor": comp, "Rank": None, "URL": None} for comp, v in competitor_ranks.items()]

    return {
        "Keyword": keyword,
        "Primary Rank": primary_rank,
        "Primary URL": primary_ranking_url,
        "Best URL Rank": best_url_rank,
        "Best URL": best_url,
        "Competitors": competitors_list,  # Return as a list
    }

# Function to get crawled URL if primary rank is None
def fetch_crawled_url(primary_domain):
    html = scrape_google("", site_search=primary_domain)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        search_results = soup.find_all("div", class_="tF2Cxc")
        if search_results:
            link_element = search_results[0].find("a")
            if link_element:
                crawled_url = link_element["href"]
                st.write(f"Crawled URL for domain {primary_domain}: {crawled_url}")  # Debug statement
                return crawled_url
    st.write(f"No crawled URL found for domain {primary_domain}.")  # Debug statement
    return None

# Streamlit App
def main():
    st.title("Google SERP Ranking Scraper")
    st.write("Upload a file or paste keywords to get rankings for a primary website and optional competitors.")

    if "proceed_full_scraping" not in st.session_state:
        st.session_state.proceed_full_scraping = False

    # File upload or text input
    input_option = st.radio("Choose input method:", ("Upload Excel File", "Paste Keywords"))
    keywords_and_urls = []

    if input_option == "Upload Excel File":
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
        if uploaded_file:
            keywords_and_urls = process_uploaded_file(uploaded_file)
            if keywords_and_urls:
                st.success(f"File uploaded successfully with {len(keywords_and_urls)} rows.")
    elif input_option == "Paste Keywords":
        pasted_text = st.text_area("Paste Keywords (one per line)")
        if pasted_text.strip():
            keywords = [kw.strip() for kw in pasted_text.split("\n") if kw.strip()]
            keywords_and_urls = [(kw, None) for kw in keywords]
            st.success(f"{len(keywords)} keywords added.")

    # Input for primary and competitor domains
    primary_domain = st.text_input("Enter Primary Domain (e.g., example.com)").strip()
    competitors_input = st.text_input(
        "Enter Competitor Domains (comma-separated, e.g., competitor1.com, competitor2.com)"
    ).strip()
    competitors = [comp.strip().lower() for comp in competitors_input.split(",") if comp.strip()]

    # Slider for parallel requests and batch size
    max_workers = st.slider("Number of Parallel Requests", min_value=1, max_value=10, value=5)
    batch_size = st.slider("Batch Size (Keywords per Request)", min_value=5, max_value=20, value=10)

    if st.button("Start Scraping"):
        if not keywords_and_urls:
            st.error("Please provide keywords.")
            return
        if not primary_domain:
            st.error("Please provide the primary domain.")
            return

        # Process the first keyword as a sample
        first_keyword, primary_url = keywords_and_urls[0]
        html = scrape_google(first_keyword)
        if html:
            sample_result = extract_ranking(html, first_keyword, primary_domain, primary_url, competitors)
            st.write("Sample Result for First Keyword:")
            st.write(sample_result)
            st.session_state.proceed_full_scraping = True

    if st.session_state.proceed_full_scraping:
        st.write("Proceeding with full scraping...")
        results = []
        total_keywords = len(keywords_and_urls)
        processed_count = 0  # Counter for processed keywords

        # Split into batches
        keyword_batches = [keywords_and_urls[i:i + batch_size] for i in range(0, len(keywords_and_urls), batch_size)]

        # Scraping process
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    scrape_google, keyword
                ): (keyword, primary_url) for keyword, primary_url in keywords_and_urls
            }

            for idx, future in enumerate(as_completed(futures)):
                keyword, primary_url = futures[future]
                html = future.result()
                if html:
                    result = extract_ranking(html, keyword, primary_domain, primary_url, competitors)
                    if result["Primary Rank"] is None:  # Fetch crawled URL if primary rank is not found
                        crawled_url = fetch_crawled_url(primary_domain)
                        result["Crawled URL"] = crawled_url
                    results.append(result)
                    processed_count += 1
                    st.write(f"Processed {processed_count}/{total_keywords} keywords.", end="\r", flush=True)

        # Display results in a table
        if results:
            flat_results = []
            for res in results:
                entry = {
                    "Keyword": res["Keyword"],
                    "Primary Rank": res["Primary Rank"],
                    "Primary URL": res["Primary URL"],
                    "Best URL Rank": res["Best URL Rank"],
                    "Best URL": res["Best URL"],
                    "Crawled URL": res.get("Crawled URL"),
                }
                for comp in res["Competitors"]:
                    entry[f"{comp['Competitor']} Rank"] = comp["Rank"]
                    entry[f"{comp['Competitor']} URL"] = comp["URL"]
                flat_results.append(entry)

            results_df = pd.DataFrame(flat_results)
            st.write("### Results Table:")
            st.dataframe(results_df)

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
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
        else:
            st.warning("No ranking data found.")

if __name__ == "__main__":
    main()
