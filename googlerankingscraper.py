from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Example using a Remote WebDriver (e.g., BrowserStack or Selenium Grid)
def scrape_google_serp_remote(keywords):
    # Remote WebDriver setup
    remote_url = "http://your-selenium-grid-url/wd/hub"  # Replace with actual Selenium Grid URL
    capabilities = DesiredCapabilities.CHROME.copy()

    driver = webdriver.Remote(
        command_executor=remote_url,
        desired_capabilities=capabilities,
    )

    data = []
    
    for keyword in keywords:
        driver.get("https://www.google.com")
        search_box = driver.find_element("name", "q")
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

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
    df.to_excel("serp_results.xlsx", index=False)
