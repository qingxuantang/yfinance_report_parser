from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
from pyppeteer import launch
import pyppeteer.errors
import pandas as pd
import os
from bs4 import BeautifulSoup
from multiprocessing import Process
import csv
import re
from importlib import reload
from . import utils
utils = reload(utils)

filename = re.findall('(.*).py', os.path.basename(__file__)) #仅包括扩展名前的部分
utils.errorLog(pkg_path=utils.pkg_path,filename=filename)

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


# Creating the class with full functionality
class ReportScraper:

    def __init__(self):
        self.config = utils.config
        self.data_path = self.config['data_path']
        self.pkg_path = 'yfinance_report_parser/'
        self.folder_path = 'grpStockReportSummary/'
        self.time_value_yfinance = self.config['time_value_yfinance'] #0 Last Week,1 Last Month,2 Last Year


    async def main(self):

        try:
            # Corrected instantiation of Chrome with options
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        except:
            # Set up the Selenium WebDriver with the headless option
            driver = webdriver.Chrome(options=options)
        print(1)
        # Navigate to the page
        driver.get('https://finance.yahoo.com/research?investment_rating=Bullish')
        print(2)
        # Find the button using its XPath and click it
        date_range_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Date Range')]")
        print(3)
        date_range_button.click()
        print(4)
        # Wait for the dropdown to appear
        dropdown_menu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dropdown-menu"))
        )

        # Check if the dropdown is displayed
        if dropdown_menu.is_displayed():
            print("Dropdown menu is displayed.")
        else:
            print("Dropdown menu is not displayed.")

        # Locate the 'Last Week' button using its data-value attribute and click it
        time_period_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-value='Last Week']"))
        )
        time_period_button.click()
        print(5)


        driver.quit()






    def run_async_code(self):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.main())

    
    def run(self):
        process = Process(target=self.run_async_code)
        process.start()
        process.join()
