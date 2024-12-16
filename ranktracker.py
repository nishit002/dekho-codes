import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime

# Use Streamlit secrets to securely fetch the API key
SCRAPERAPI_KEY = st.secrets["SCRAPERAPI_KEY"]

# Function to scrape Google SERP
def scrape_keyword(keyword, primary_site, competitors):
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url=https://www.google.com/search?q={keyword}&num=100&gl=in&hl=en&device=mobile"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15A372 Safari/604.1'
    }

    for attempt in range(3):
        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            time.sleep(2)
    return None

# Function to extract rankings from HTML
def extract_ranking_from_html(html, primary_site, competitors):
    soup = BeautifulSoup(html, 'html.parser')
    search_results = soup.find_all('div', class_='tF2Cxc')  # Google SERP search result container
    rank_counter = 0
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

            # Check for competitor rankings (only if competitors are provided)
            if competitors:
                for comp in competitors:
                    if comp in link:
                        # Ensure no duplicates for the same rank
                        if not any(c['Rank'] == rank_counter for c in competitor_ranks):
                            competitor_ranks.append({
                                "Competitor": comp,
                                "Rank": rank_counter,
                                "URL": link
                            })

    return {
        "Primary Rank": primary_rank,
        "Primary URL": primary_url,
        "Competitors": competitor_ranks if competitors else None
    }

# Streamlit App
def main():
    st.title("Google SERP Ranking Scraper")
    st.write("Upload an Excel file or paste keywords to extract ranking details for a primary website and optionally its competitors.")

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

    # Slider for parallel requests
    max_workers = st.slider("Number of Parallel Requests", min_value=1, max_value=20, value=10)

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

        # Scraping process
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(scrape_keyword, keyword, primary_site, competitors): keyword
                for keyword in keywords
            }

            for idx, future in enumerate(as_completed(futures)):
                keyword = futures[future]
                html = future.result()
                if html:
                    # Extract ranking details
                    rankings = extract_ranking_from_html(html, primary_site, competitors)
                    result = {
                        "Keyword": keyword,
                        "Primary Rank": rankings["Primary Rank"],
                        "Primary URL": rankings["Primary URL"],
                    }

                    # Add competitor rankings if applicable
                    if competitors:
                        for comp in rankings["Competitors"]:
                            result[f"{comp['Competitor']} Rank"] = comp["Rank"]
                            result[f"{comp['Competitor']} URL"] = comp["URL"]

                    results.append(result)

                # Update progress
                progress = ((idx + 1) / total_keywords) * 100
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
            st.warning("No ranking data found for the primary site.")

if __name__ == "__main__":
    main()
