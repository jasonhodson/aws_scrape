import re
import os
import logging
from utils.base import UtilBaseScrape

def lambda_handler(event, context):
    scrape_util = UtilBaseScrape()

    url = 'https://www.goodreads.com/group/popular'
    s3_bucket_name = 'web-scrape-goodreads'
    s3_file_name = 'group_goodreads.csv'
    header = ['group_name', 'group_description']
    groups_data = []
    sleep_time = 5

    driver = scrape_util.chrome_driver()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Get the BeautifulSoup object from the page
    soup = scrape_util.page_to_soup(url, sleep_time, driver)

    # Find all div elements with class 'elementList'
    element_lists = soup.find_all('div', class_='elementList')

    # Iterate through the found divs
    for element in element_lists:
        # Find the group name
        group_name_element = element.find('a', class_='groupName')
        group_name = group_name_element.text.strip() if group_name_element else "No Group Name Found"

        # Find the description
        description_element = element.find('span', id=re.compile("^freeTextContainergroup"))
        group_description = description_element.text.strip() if description_element else "No Description Found"
        # Clean up group_description to remove newlines, carriage returns, and consolidate whitespace
        group_description = re.sub(r'\s+', ' ', group_description).strip()

        groups_data.append({'group_name': group_name, 'group_description': group_description})
        logger.info(f"Group Name: {group_name}, Description: {group_description}")

    # Write the list of dictionaries to a CSV file in S3
    if groups_data:
        scrape_util.write_to_s3_csv(s3_bucket_name, s3_file_name, header, groups_data)
        logger.info(f"Successfully wrote {len(groups_data)} quotes to {s3_file_name} in {s3_bucket_name}.")