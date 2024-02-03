import re
import os
import logging
from utils.base import UtilBaseScrape

def lambda_handler(event, context):
    scrape_util = UtilBaseScrape()

    url = 'https://www.goodreads.com/quotes'
    s3_bucket_name = 'web-scrape-goodreads'
    s3_file_name = 'quote_goodreads.csv'
    header = ['quote_text', 'quote_author']
    quotes_data = []
    sleep_time = 5

    driver = scrape_util.chrome_driver()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    soup = scrape_util.page_to_soup(url, sleep_time, driver)

    # Find all div elements with class 'quoteDetails'
    quote_divs = soup.find_all('div', class_='quoteDetails')

    # Iterate through the divs and extract quoteText and authorOrTitle
    for quote_div in quote_divs:
        quote_text_element = quote_div.find('div', class_='quoteText')
        quote_text = quote_text_element.get_text(strip=True) if quote_text_element else None

        author_title_element = quote_div.find('span', class_='authorOrTitle')
        author_title = author_title_element.get_text(strip=True) if author_title_element else None

        quoted_text = re.search(r'“(.*?)”', quote_text)
        quoted_text = quoted_text.group(1) if quoted_text else None

        if quoted_text and author_title:
            quotes_data.append({'quote_text': quoted_text, 'quote_author': author_title})

    # Write the list of dictionaries to a CSV file in S3
    if quotes_data:
        scrape_util.write_to_s3_csv(s3_bucket_name, s3_file_name, header, quotes_data)
        logger.info(f"Successfully wrote {len(quotes_data)} quotes to {s3_file_name} in {s3_bucket_name}.")