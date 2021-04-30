# -*- coding: utf-8 -*-
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import logging
import traceback
from nltk.corpus import wordnet as wn

MAX_WAIT = 10
MAX_RETRY = 5
MAX_SCROLLS = 40


class SeamlessScraper:

    def __init__(self, debug=False):
        self.debug = debug
        self.driver = self.__get_driver()
        self.logger = self.__get_logger()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

        self.driver.close()
        self.driver.quit()

        return True

    def initialize(self, url):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, MAX_WAIT)

        # wait to load review (ajax call)
        time.sleep(5)

        return 0

    def parse_menu(self, url):
        time.sleep(4)
        self.set_food_list()
        response = BeautifulSoup(self.driver.page_source, 'html.parser')
        results = []
        menu_items = response.find_all(
            'span', {'data-testid': re.compile('restaurant-menu-item')})
        for item in menu_items:
            row = []
            title = item.find_all(title=True)
            ingredient = []
            if title and len(title[0]['title']) > 0:
                row.append(title[0]['title'])
                ingredient += self.get_ingredients(title[0]['title'])
            else:
                row.append("")
            price = item.find('span', class_='menuItem-displayPrice')
            if price and len(price.text) > 0:
                row.append(price.text)
            else:
                row.append("")
            description = item.find_all(attrs={"data-testid": "description"})
            if description and len(description[0].get_text()) > 0:
                row.append(description[0].get_text())
                ingredient += self.get_ingredients(description[0].get_text())
            else:
                row.append("")
            row.append(list(set(ingredient)))
            row.append(self.get_restaurant_id(url))
            # print(row)
            results.append(row)
        return results

    def set_food_list(self):
        food = wn.synset('food.n.01')
        foodList = []
        foodList += list(set([w for s in food.closure(lambda s:s.hyponyms())
                              for w in s.lemma_names()]))
        food = wn.synset('food.n.02')
        foodList += list(set([w for s in food.closure(lambda s:s.hyponyms())
                              for w in s.lemma_names()]))
        food = wn.synset('food.n.03')
        foodList += list(set([w for s in food.closure(lambda s:s.hyponyms())
                              for w in s.lemma_names()]))
        self.foodSet = set(foodList)

    def get_ingredients(self, description):
        wordList = set(re.sub("[^\w]", " ",  description.lower()).split())
        return list(self.foodSet.intersection(wordList))

    def get_restaurant_urls(self, url):

        self.driver.get(url)

        time.sleep(4)

        resp = BeautifulSoup(self.driver.page_source, 'html.parser')
        restaurant_blocks = resp.find_all(
            'div', {'class': 'cardTextWrapper u-width-full'})
        results = []
        for restaurant in restaurant_blocks:
            url = 'https://www.seamless.com' + restaurant.div.a['href']
            restaurant_name = restaurant.div.a.get_text()
            cuisine = restaurant.div.div.div.get_text()
            id = int(url.split('/')[-1])
            print('('+str(id) + ', \''+restaurant_name + '\', \'' + cuisine+'\'),')
            results.append(url)
        return results

    def get_restaurant_id(self, url):
        return int(url.split('/')[-1])

    def __scroll(self):
        SCROLL_PAUSE_TIME = 0.5

        # Get scroll height
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def __get_logger(self):
        logger = logging.getLogger('seamless-scraper')
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('gm-scraper.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        return logger

    def __get_driver(self, debug=False):
        options = Options()

        if not self.debug:
            options.add_argument("--headless")
        else:
            options.add_argument("--window-size=1366,768")

        options.add_argument("--disable-notifications")
        options.add_argument("--lang=en-GB")
        input_driver = webdriver.Chrome(chrome_options=options)

        return input_driver

    # util function to clean special characters

    def __filter_string(self, str):
        strOut = str.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        return strOut
