from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from DataBase import Category, Product, session, engine
from unidecode import unidecode
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Table ,MetaData
from time import sleep
import os

def clear_screen():
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

def drop_database():
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)

def shorten_link(link):
    valid = link.split("/")[:6]
    return "/".join(valid)

def close_popup(wait):
    close_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='modal-root']/div[3]/div/div/div/div[1]/div/div[3]")))
    close_button.click()

def add_to_database(objects):
    session.add_all(objects)
    session.commit()
    clear_screen()
    print("[+] Add ", len(objects), "Objects in DataBase") ## LOG

def read_all_categories_from_database():
    table = Table('category', MetaData(), autoload_with=engine)
    connection = engine.connect()
    result = connection.execute(table.select())

    clear_screen()

    objects = []
    for row in result:
        objects.append(row)

    return objects

def read_categories_url_from_database():
    table = Table('category', MetaData(), autoload_with=engine)
    connection = engine.connect()
    result = connection.execute(table.select())

    clear_screen()

    urls = []
    for row in result:
        urls.append(row[2])

    return urls

def read_all_products_from_database():
    table = Table('product', MetaData(), autoload_with=engine)
    connection = engine.connect()
    result = connection.execute(table.select())

    clear_screen()

    for row in result:
        print(row)

def extract_categories(driver):
    wait = WebDriverWait(driver, 10)

    #Wait untill the first image of the categories icons loaded
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div[1]/div[3]/div[3]/div[1]/div[3]/div/div[2]/div/div/div[1]/div[1]/div/span[1]/a/div/img")))

    #Wait for the slider's next button to be clickable
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='__next']/div[1]/div[3]/div[3]/div[1]/div[3]/div/div[2]/div/div/div[2]")))
    #Click on the next button of the slider until we reach the end of slider
    while not "lg:hidden" in next_button.get_attribute("class"):
        next_button.click()

    sliders = driver.find_elements(By.CLASS_NAME, "swiper-container")
    categories = sliders[2].find_elements(By.TAG_NAME, "a")

    objects = []
    
    for category in categories:
        href = category.get_attribute("href")

        img = category.find_element(By.TAG_NAME, "img").get_attribute("src")
        alt = category.find_element(By.TAG_NAME, "img").get_attribute("alt")

        objects.append(Category(asset_id="",link=href, photo=img, name=alt))

    return objects

def extract_products(driver, category_id):
    wait = WebDriverWait(driver, 10)
    #Wait untill pagination of the page loaded
    pagination = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-list_ProductList__pagination__vx69z")))
    driver.execute_script("arguments[0].scrollIntoView();", pagination)
    sleep(1)

    product_list = driver.find_elements(By.CLASS_NAME, "product-list_ProductList__item__LiiNI")

    products = []
    for product in product_list:
        price = -1
        discount = 0

        try:

            link = product.find_element(By.TAG_NAME, "a").get_attribute("href")

            name = product.find_element(By.TAG_NAME, "h3").text

            spans = product.find_elements(By.TAG_NAME, "span")
            for span in spans:
                data_testeid = span.get_attribute("data-testid")
                if 'price-final' in data_testeid:
                    price = unidecode(span.text)
                    price = ''.join([char for char in price if char.isdigit()])

                if 'price-discount-percent' in data_testeid:
                    discount = unidecode(span.text)
                    discount = ''.join([char for char in discount if char.isdigit()])

            try:
                price = unidecode(product.find_element(By.CSS_SELECTOR, "[data-testid='price-no-discount']").text)
                price = ''.join([char for char in price if char.isdigit()])
            except:
                pass

            products.append(Product(asset_id='', link=shorten_link(link), name=name, price=price, discount=discount, category_id=category_id))
        except:
            pass

    return products

def main():
    driver = webdriver.Chrome()
    driver.get("https://www.digikala.com/fresh/")
    wait = WebDriverWait(driver, 10)

    #Close first page popup
    close_popup(wait=wait)
    sleep(1)

    #Scroll to the fresh categories in the middle of fist page
    driver.execute_script("window.scrollBy(0, 500)")
    sleep(1)

    categories = extract_categories(driver=driver)
    add_to_database(objects=categories)
    # categories_url = read_categories_url_from_database()
    categories = read_all_categories_from_database()
    for category in categories:
        url = category[2]
        driver.get(url+"?page=1")
        products = extract_products(driver=driver, category_id=category[0])
        add_to_database(objects=products)
        
    driver.quit()


clear_screen()
main()
# drop_database()