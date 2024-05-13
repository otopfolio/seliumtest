from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import streamlit as st
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime

def scrape_data_with_selenium() -> pd.DataFrame:
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensures no UI is shown
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Start the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://dtm.iom.int/reports?search=&sort_by=field_published_date&sort_order=DESC")
        try:
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".report-item1")))
        except TimeoutException:
            st.error("Failed to load the page elements within the timeout period.")
            return pd.DataFrame()  # Return an empty DataFrame or handle this case differently.
        
        report_items = driver.find_elements(By.CSS_SELECTOR, ".report-item1")
        reports_data = []
        for item in report_items:
            title = item.find_element(By.CSS_SELECTOR, 'a.title').text.strip()
            link = item.find_element(By.CSS_SELECTOR, 'a.title').get_attribute('href')
            date_info = item.find_element(By.CSS_SELECTOR, 'div.date').text.split('·')
            date = pd.to_datetime(date_info[0].strip(), errors='coerce', format='%b %d %Y')
            if pd.isna(date):
                continue
            region = date_info[1].strip() if len(date_info) > 1 else 'Unknown'
            country_name = date_info[2].strip() if len(date_info) > 2 else 'Unknown'
            report_type = date_info[3].strip() if len(date_info) > 3 else 'Unknown'
            summary_content = item.find_element(By.CSS_SELECTOR, 'div.content').text.strip()
            reports_data.append({
                'Title': title,
                'Summary': summary_content,
                'Link': link,
                'Published Date': date,
                'Country Name': country_name,
                'Region': region,
                'Report Type': report_type
            })
    finally:
        driver.quit()  # Ensure the driver is closed after the scraping
    return pd.DataFrame(reports_data)

def app():
    st.title('DTM Report Dashboard')
    df = scrape_data_with_selenium()
    if not df.empty:
        st.write("## Head of the DataFrame")
        st.write(df.head())
    else:
        st.write("No data available.")

if __name__ == '__main__':
    app()
