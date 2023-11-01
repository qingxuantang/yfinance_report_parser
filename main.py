
from yfinance_report_parser import yfinance_report_parser
from yfinance_report_parser import utils
from importlib import reload
utils = reload(utils)
yfinance_report_parser = reload(yfinance_report_parser)


if __name__ == "__main__":
    config = utils.config
    end_page = config['end_page']
    scraper = yfinance_report_parser.ReportScraper()
    scraper.run(end_page=end_page)