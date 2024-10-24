import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
import random
from time import sleep

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service('/Users/bisosad/bi_webscraper/chromedriver')
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_main_page(driver):
    driver.get("https://www.lazada.vn/dien-thoai-di-dong/?page=1")
    sleep(random.randint(5, 10))

    # Get titles and links
    elems = driver.find_elements(By.CSS_SELECTOR, ".RfADt [href]")
    titles = [elem.text for elem in elems]
    links = [elem.get_attribute('href') for elem in elems]

    # Get prices
    elems_price = driver.find_elements(By.CSS_SELECTOR, ".aBrP0")
    prices = [elem_price.text for elem_price in elems_price]

    # Create DataFrame
    df1 = pd.DataFrame(list(zip(titles, prices, links)), columns=['title', 'price', 'link_item'])
    df1['index_'] = np.arange(1, len(df1) + 1)

    # Get discounts
    discount_list, discount_percent_list = [], []
    for i in range(1, len(titles) + 1):
        try:
            discount = driver.find_element(By.XPATH, f"//div[@data-index='{i}']//span[@class='WNoq3']//del").text
            discount_list.append(discount)
            discount_percent = driver.find_element(By.XPATH, f"//div[@data-index='{i}']//span[@class='WNoq3']//span[2]").text
            discount_percent_list.append(discount_percent)
        except NoSuchElementException:
            discount_list.append(None)
            discount_percent_list.append(None)

    df1['discount'] = discount_list
    df1['discount_percent'] = discount_percent_list

    # Get review counts
    elems_countReviews = driver.find_elements(By.CSS_SELECTOR, "._6uN7R")
    countReviews = [elem.text for elem in elems_countReviews]
    df1['countReviews'] = countReviews

    return df1

def scrape_comments(driver, link):
    driver.get(link)
    wait = WebDriverWait(driver, 20)  # Increased wait time
    name_comment, content_comment, skuInfo_comment, like_count = [], [], [], []
    count = 1

    while True:
        try:
            print(f"Crawl Page {count}")
            elems_name = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".middle")))
            name_comment += [elem.text for elem in elems_name]

            elems_content = driver.find_elements(By.CSS_SELECTOR, ".item-content .content")
            content_comment += [elem.text for elem in elems_content]

            elems_skuInfo = driver.find_elements(By.CSS_SELECTOR, ".item-content .skuInfo")
            skuInfo_comment += [elem.text for elem in elems_skuInfo]

            elems_likeCount = driver.find_elements(By.CSS_SELECTOR, ".item-content .bottom .left .left-content")
            like_count += [elem.text for elem in elems_likeCount]

            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]")))
            next_button.click()
            print("Clicked on button next page!")
            sleep(random.randint(1, 3))
            count += 1
        except TimeoutException:
            print("TimeoutException: Unable to find elements, current URL:", driver.current_url)
            break
        except ElementNotInteractableException:
            print("Element Not Interactable Exception!")
            break

    return pd.DataFrame(list(zip(name_comment, content_comment, skuInfo_comment, like_count)),
                        columns=['name_comment', 'content_comment', 'skuInfo_comment', 'like_count'])

def main():
    driver = setup_driver()
    try:
        df1 = scrape_main_page(driver)
        all_comments = []

        for link in df1['link_item']:
            comments_df = scrape_comments(driver, link)
            comments_df['link_item'] = link
            all_comments.append(comments_df)

        final_comments_df = pd.concat(all_comments, ignore_index=True)

        # Save DataFrames to CSV
        df1.to_csv('products_data.csv', index=False)
        final_comments_df.to_csv('comments_data.csv', index=False)

        print("Data saved to products_data.csv and comments_data.csv.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
