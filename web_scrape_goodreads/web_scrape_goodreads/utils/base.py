import logging
import csv
import boto3
import io
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup

# Conditionally import ChromeDriverManager if not running on AWS Lambda
# if "AWS_LAMBDA_FUNCTION_NAME" not in os.environ:
#     from webdriver_manager.chrome import ChromeDriverManager

class UtilBaseScrape:
    """Base class for web scrape."""

    def __init__(self) -> None:
        # Define the logger object
        self.logger = logging.getLogger(__name__)

    # def generate_chrome_options(self) -> webdriver.ChromeOptions:
    #     """
    #     Generates Chrome options for WebDriver.

    #     Returns:
    #         webdriver.ChromeOptions: Configured Chrome options.
    #     """
    #     chrome_options = webdriver.ChromeOptions()
    #     chrome_options.add_argument('--headless')
    #     chrome_options.add_argument('--no-sandbox')
    #     chrome_options.add_argument('--disable-gpu')
    #     chrome_options.add_argument('--window-size=1280x1696')
    #     chrome_options.add_argument('--disable-dev-shm-usage')
    #     chrome_options.add_argument("--verbose")
    #     chrome_options.add_argument('--disable-software-rasterizer')
    #     chrome_options.add_argument('--disable-setuid-sandbox')
    #     chrome_options.add_argument('--single-process')
    #     return chrome_options

    # def local_chrome_driver(self):
    #     """
    #     Initialize a headless Chrome WebDriver for local testing with custom options and capabilities.
    #     """
    #     service = Service(ChromeDriverManager().install())
    #     chrome_options = self.generate_chrome_options()
    #     driver = webdriver.Chrome(service=service, options=chrome_options)
    #     return driver

    # def chrome_driver(self):
    #     """
    #     Initialize a headless Chrome WebDriver with custom options and capabilities for AWS Lambda or similar environments.
    #     """
    #     options = self.generate_chrome_options()
    #     options.binary_location = '/opt/chrome/chrome'
        
    #     caps = DesiredCapabilities.CHROME
    #     caps['goog:loggingPrefs'] = {'browser': 'ALL', 'driver': 'ALL'}
    #     service = Service(
    #         executable_path="/opt/chromedriver",
    #         log_path='/tmp/chromedriver.log',
    #         service_args=["--verbose"]
    #     )

    #     try:
    #         chrome = webdriver.Chrome(service=service, options=options)
    #         self.logger.info("WebDriver initialized successfully")
    #         return chrome
    #     except WebDriverException as e:
    #         self.logger.error(f"ChromeDriver failed to start: {e}")
    #         raise

    def chrome_driver(self):
        options = webdriver.ChromeOptions()
        options.binary_location = '/opt/chrome/chrome'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--verbose")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--single-process')

        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL', 'driver': 'ALL'}
        service = Service(
            executable_path="/opt/chromedriver",
            log_path='/tmp/chromedriver.log',
            service_args=["--verbose"]
        )

        try:
            chrome = webdriver.Chrome(service=service, options=options)
            logging.info("WebDriver initialized successfully")
            return chrome
        except WebDriverException as e:
            logging.error(f"ChromeDriver failed to start: {e}")
            raise

    def page_to_soup(self, url:str, sleep_time:int, driver:any) -> BeautifulSoup:
        # Navigate to the page
        driver.get(url)

        # Wait for JavaScript to load
        time.sleep(sleep_time)

        # Extract the page's content
        page_content = driver.page_source

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(page_content, 'html.parser')
        return(soup)

    def read_existing_s3_files(self, bucket_name: str, s3_file_name: str) -> list:
        """Reads contents of .csv or .txt files stored on an S3 bucket."""
        s3 = boto3.client('s3')
        try:
            response = s3.get_object(Bucket=bucket_name, Key=s3_file_name)
            lines = response['Body'].read().decode('utf-8').splitlines()

            # Check file extension and process accordingly
            if s3_file_name.endswith('.csv'):
                reader = csv.DictReader(lines)
                data = list(reader)
                self.logger.info("CSV data successfully read from S3")
            elif s3_file_name.endswith('.txt'):
                data = [line.strip() for line in lines]
                self.logger.info("Text data successfully read from S3")
            else:
                self.logger.error("Unsupported file format")
                return []

            return data

        except Exception as e:
            self.logger.error(f"Could not read from S3: {e}")
            return []

    def write_to_s3_csv(self, s3_bucket_name: str, s3_file_name: str, header, data):
        """
        Writes data to a .csv file on an S3 bucket. This class will replace the file if it exists.

        Parameters:
        - s3_bucket_name: The name of the S3 bucket.
        - s3_file_name: The name of the file in the S3 bucket.
        - header: A list of column headers for the CSV file.
        - data: A list of dictionaries, each representing a row of data matching the headers.
        """
        s3 = boto3.client('s3')
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

        # Write the updated CSV back to S3
        s3.put_object(Bucket=s3_bucket_name, Key=s3_file_name, Body=csv_buffer.getvalue())
        self.logger.info(f"CSV file updated successfully in S3 bucket '{s3_bucket_name}' with the file name '{s3_file_name}'")