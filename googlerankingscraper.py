import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os

# Competitors to track
primary_site = "collegedekho.com"
competitors = ["collegedunia.com", "shiksha.com", "getmyuni.com", "careers360.com"]

# Global variables
results_file_path = "serp_results.xlsx"
scraping_in_progress = False
start_time = None

# Function to perform Google SERP scraping
def scrape_google_serp(keywords):
    global scraping_in_progress, results_file_path

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    data = []

    # Loop through each keyword
    for keyword in keywords:
        driver.get("https://www.google.com")
        search_box = driver.find_element("name", "q")
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(u'\ue007')  # Press Enter
        time.sleep(2)  # Wait for the results page to load

        # Fetch results and analyze rankings for primary site and competitors
        search_results = driver.find_elements("css selector", 'div.g')
        for idx, result in enumerate(search_results[:10]):
            try:
                title = result.find_element("tag name", 'h3').text
                url = result.find_element("tag name", 'a').get_attribute('href')
                rank = idx + 1
                is_primary = primary_site in url
                is_competitor = any(comp in url for comp in competitors)
                data.append({
                    'Keyword': keyword,
                    'Rank': rank,
                    'Title': title,
                    'URL': url,
                    'Is Primary': is_primary,
                    'Is Competitor': is_competitor
                })
            except:
                continue

    driver.quit()

    # Convert to DataFrame and save as Excel
    df = pd.DataFrame(data)
    df.to_excel(results_file_path, index=False)
    scraping_in_progress = False  # Mark scraping as complete

# Function to check for existing results and return the download link
def check_results_file():
    if os.path.exists(results_file_path):
        return True
    return False

# Streamlit App UI
st.title("Google SERP Scraper")

# File uploader for keywords
uploaded_file = st.file_uploader("Upload Keywords Excel File", type="xlsx")

if uploaded_file:
    keywords_df = pd.read_excel(uploaded_file)
    keywords = keywords_df['Keyword'].tolist()

    if st.button("Start Scraping") and not scraping_in_progress:
        scraping_in_progress = True
        start_time = time.time()

        # Start background scraping process
        st.write(f"Scraping started with {len(keywords)} keywords.")
        with st.spinner("Scraping in progress... Please wait."):
            scrape_google_serp(keywords)

        st.success("Scraping completed!")

# Show progress or results
if scraping_in_progress:
    st.warning("Scraping is currently in progress... Please check back later.")
else:
    if check_results_file():
        st.success("Scraping completed. You can download the results below:")
        st.download_button(label="Download Results", data=open(results_file_path, 'rb'), file_name="serp_results.xlsx")
    else:
        st.info("No scraping results found. Please start the scraping process.")
