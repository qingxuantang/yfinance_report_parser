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

# Creating the class with full functionality
class ReportScraper:

    def __init__(self):
        self.config = utils.config
        self.data_path = self.config['data_path']
        self.pkg_path = 'yfinance_report_parser/'
        self.folder_path = 'grpStockReportSummary/'
        self.time_value_yfinance = self.config['time_value_yfinance'] #0 Last Week,1 Last Month,2 Last Year


    async def main(self,end_page):
        # 启动浏览器
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        url = self.config['yfinance_report_url'] #Accessable only with US IP
        await page.goto(url)
        print('Yahoo Finance research report site is opened.')
        await asyncio.sleep(5)


        #****************************************

        # xpath method
        # XPath to find the "Date Range" button which contains the text "Date Range"
        date_range_button_xpath = "//div[contains(@class, 'Pos(r)') and contains(@class, 'D(ib)') and contains(@class, 'Cur(p)') and contains(., 'Date Range')]"
        # Find the "Date Range" element to trigger the dropdown using XPath
        await page.waitForXPath(date_range_button_xpath)
        button = await page.xpath(date_range_button_xpath)
        await button[0].click()
        
        # css method
        # Wait for the button to be available using the data-test attribute
        #await page.waitForSelector('div[data-test="dropdown"]')
        # Click the button using the data-test attribute
        #await page.click('div[data-test="dropdown"]')
        
        await asyncio.sleep(10)
        """
        #await page.waitForSelector('div[data-test="dropdown-dd-menu"]', options={'visible': True})
        #await page.waitForXPath('//div[@id="dropdown-menu"]', visible=True)
        await page.waitForSelector('div[data-test="dropdown-dd-menu"]')
        dropdown_menu_visible = await page.evaluate('''() => {
            const elem = document.querySelector('#dropdown-menu');
            if (elem) {
                const style = window.getComputedStyle(elem);
                return style && style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
            }
            return false;
        }''')

        if dropdown_menu_visible:"""

        

        # The dropdown menu is visible
        # Click the button with the desired 'data-value'
        time_value = self.time_value_yfinance[1]

        #*************
        await page.waitForSelector('button[data-field="report_date"][data-value="Last Week"]')
        await page.click('button[data-field="report_date"][data-value="Last Week"]')
        await asyncio.sleep(5)
        print("Date range '" + time_value + "' selected.")
        #*************

        #await page.click(f'button[data-value="{time_value}"]')
        #button = await page.querySelector('button[data-value="{time_value}"]')
        #if button:
        #    await button.click()
        #    await asyncio.sleep(5)
        #    print("Date range '" + time_value + "' selected.")
        #else:
        #    print("Couldn't find " + time_value + "!")

        #****************************************


        pagenumber_range = range(1, end_page+1)
        for pagenumber in pagenumber_range:
            
            print(f'开始翻页，现在是第{pagenumber}页')
            if pagenumber != 1:
                # Use a more specific XPath based on the button's classes and structure
                button_xpath = "//button[contains(@class, 'Va(m)') and contains(@class, 'C($linkColor)')]/span/span[text()='Next']"
                # Wait for the button to be visible
                next_button = await page.waitForXPath(button_xpath, timeout=10000)
                if next_button:
                    # Before clicking, ensure the button is clickable
                    await page.waitForSelector('button[aria-disabled="false"]', visible=True, timeout=10000)
                    await next_button.click()  # Click the button
                    await asyncio.sleep(5)  # Introduce a delay after clicking to allow the page to load
            else: 
                await asyncio.sleep(3)

            print(f'翻到第{pagenumber}页完成')
            
            
            # Extract the content of the page
            content = await page.content()
            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            # Lists to hold the extracted data
            data_list = []
            # Extract table rows
            rows = soup.find_all("tr")
            # Iterate over the rows and extract required data
            for row in rows[1:]:  # Skipping the header row
                columns = row.find_all("td")
                if len(columns) > 4:  # To ensure we have the required columns
                    report_data = columns[0].text
                    # Extracting rating and price target
                    rating = None
                    price_target = None
                    if "Rating:" in report_data:
                        rating_data = report_data.split("Rating:")[1].split("Price Target:")
                        rating = rating_data[0].strip().split('\n')[0] if len(rating_data) > 0 else None
                        price_target = rating_data[1].strip() if len(rating_data) > 1 else None
                    
                    report_name = report_data.split("Rating:")[0].strip()
                    symbols = columns[1].text.strip()
                    sector = columns[2].text.strip()
                    provider = columns[3].text.strip()
                    date = columns[4].text.strip()
                    data_list.append([report_name, symbols, sector, provider, date, rating, price_target])
            
            print('数据读取完成')

            # 保存到Excel
            # File path for the CSV
            csv_path = self.data_path + self.pkg_path + self.folder_path + f"yahoofinance_{pagenumber}.csv"
            # Write the extracted data to the CSV file
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                # Write the headers
                writer.writerow(['report_name', 'symbols', 'sector', 'provider', 'date', 'rating', 'price_target'])
                # Write the extracted data
                for row in data_list:
                    writer.writerow(row)

            print(f'保存为yahoofinance_{pagenumber}.xlsx完成') #'''
            

        await browser.close()
        
        # Merge tables: only merge the latest downloaded tables.
        path = self.data_path + self.pkg_path + self.folder_path
        file_used = [f"yahoofinance_{i}.xlsx" for i in range(1,end_page+1)]
        
        all_dfs = []
        for file in file_used:
            df = pd.read_excel(path+file)
            df = df.drop(df.index[0])  # 删除第一行
            all_dfs.append(df)

        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_excel(os.path.join(path, "stock.xlsx"), index=False)
        print('所有表格合并完成') 


    
    
        

    def run_async_code(self,end_page):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.main(end_page=end_page))

    
    def run(self,end_page):
        process = Process(target=self.run_async_code, args=(end_page,))
        process.start()
        process.join()


    


