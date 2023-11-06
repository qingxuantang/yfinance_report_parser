
from yfinance_report_parser import new_yfinance_report_parser
from yfinance_report_parser import utils
from importlib import reload
utils = reload(utils)
new_yfinance_report_parser = reload(new_yfinance_report_parser)


if __name__ == "__main__":
    config = utils.config
    end_page = config['end_page']
    scraper = new_yfinance_report_parser.ReportScraper()
    scraper.run()