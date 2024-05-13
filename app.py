import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Function to scrape data using Selenium
@st.cache
def scrape_data(pages=10):
    base_url = 'https://dtm.iom.int/reports'
    options = Options()
    options.add_argument('--headless')  # to run chrome in the background
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    reports_data = []

    for page in range(pages):
        url = base_url if page == 0 else f'{base_url}?page={page}'
        driver.get(url)
        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "report-item1"))
            )
        except TimeoutException:
            print("Timed out waiting for page to load")
            continue

        dtm_reports = driver.find_elements(By.CLASS_NAME, "report-item1")

        for report in dtm_reports:
            title = report.find_element(By.CLASS_NAME, 'title').text.strip()
            date_info = report.find_element(By.CLASS_NAME, 'date').text.split('·')
            date = pd.to_datetime(date_info[0].strip(), errors='coerce', format='%b %d %Y')

            reports_data.append({'Title': title, 'Published Date': date})

    driver.quit()
    return pd.DataFrame(reports_data)

# Streamlit app setup
def app():
    st.set_page_config(page_title='DTM Report Dashboard', page_icon='📊', layout="wide")
    st.title('DTM Report Dashboard')

    # Get data
    df = scrape_data()

    # Display head of the DataFrame
    st.write("## Head of the DataFrame")
    st.write(df.head())

if __name__ == '__main__':
    app()
