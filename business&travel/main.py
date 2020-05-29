# -*- coding: utf-8 -*-
"""
@author: jmartorell
"""
import operator
import os
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class App:
    def __init__(self, username='business.travel', password='Busi2016', target_destination='new york',
                 path='/home/jmartorell/Booking'):
        self.username = username
        self.password = password
        self.target_destination = target_destination
        self.path = path
        self.browser = webdriver.Firefox(
            executable_path='/usr/local/bin/geckodriver')
        self.error = False
        self.url = 'https://pro.w2m.travel'
        self.all_hotels = []
        self.all_prices = []
        self.browser.get(self.url)
        self.log_in()
        if self.error is False:
            self.search_engine_insert()
        if self.error is False:
            self.scroll_down()
        if self.error is False:
            if not os.path.exists(path):
                os.mkdir(path)
            # todo: self.reach_target()
        # close the browser
        sleep(1)
        self.browser.quit()

    def log_in(self, ):
        try:
            input_element = self.browser.find_element_by_id("email")
            input_element.clear()
            input_element.send_keys("business.travel")
            input_element = self.browser.find_element_by_id("password")
            input_element.clear()
            print('Logging in with username and password ...')
            input_element.send_keys("Busi2016")
            input_element.submit()

            # print(self.browser.current_url)
        except Exception:
            print('Some exception occurred while trying to find username or password field')
            self.error = True

    def cookies_popup(self):
        print('closing cookies window ...')
        WebDriverWait(self.browser, 100).until(EC.visibility_of_element_located((
            By.CSS_SELECTOR,
            '.cookie-policy__close'))).click()
        sleep(1)

    def search_engine_insert(self):
        # wait to load the search engine
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((
            By.XPATH,
            '//*[@id="hotel-searcher-_ctl1__ctl1__ctl1_pageBody_pageBody_searcher__ctl0_ctlZoneSelector-input"]'))).click()
        self.cookies_popup()
        element = self.browser.find_element_by_xpath(
            '//*[@id="hotel-searcher-_ctl1__ctl1__ctl1_pageBody_pageBody_searcher__ctl0_ctlZoneSelector-input"]')
        element.clear()

        # check access
        # assert "Hoteles | W2M" in self.browser.title

        # enter data in input field
        element.send_keys(self.target_destination)

        # TODO:
        # drop-down item selection
        actions = ActionChains(self.browser)
        for _ in range(1):
            actions.send_keys(Keys.ARROW_DOWN).perform()
            sleep(1)

        # enter destination city
        target_city = element.find_element_by_xpath(
            "//div[3]/div[1]")
        target_city.click()

        # press the search button
        login_attempt = element.find_element_by_xpath(
            "//div[2]/div[2]/button")
        print('loading page ...')
        login_attempt.click()

    # todo: def reach_target(self):
    #     element = WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((
    #         By.XPATH,
    #         '//main/div[1]/div/div[1]/article/div[1]/div[2]/h2'))).click()

    def scroll_down(self):
        self.browser.implicitly_wait(15)

        # todo REF: https://stackoverflow.com/questions/48006078/how-to-scroll-down-in-python-selenium-step-by-step
        # FIXME 1: two ways to scroll down,
        #  1) go down to the bottom of the page at once.
        # self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # FIXME 2:
        #  2) Descend from item to item to the bottom of the page.
        # in this example and item is the text of the button "See options":
        read_mores = self.browser.find_elements_by_xpath('//button[text()="Ver más opciones"]')
        for read_more in read_mores:
            self.browser.execute_script("arguments[0].scrollIntoView();", read_more)
            # read_more.click()

        soup = BeautifulSoup(self.browser.page_source, 'lxml')
        hotel_list = soup.find_all('div', {'class': 'results-list__item'})
        euro_symbol = '€'

        print("\n\tdisplay:\n")
        try:
            for i, hotel in enumerate(hotel_list):
                hotel_name = hotel.find('h2', {'class': 'info-card__title'}).getText()
                # fixme: remove whitespaces REF: https://stackoverrun.com/es/q/743639
                hotel_name = ' '.join(hotel_name.split())
                # notice that instead of .getText().strip('€') here we work with .getText().replace('€', ''):
                hotel_price = hotel.find('a', {'tabindex': '0'}).getText().replace('€', '')
                hotel_price = hotel_price.replace('.', '')
                hotel_price = hotel_price.replace(',', '.')
                hotel_price = float(hotel_price)
                hotel_price = "{0:.2f}".format(hotel_price)
                self.all_prices.append(hotel_price)

                if len(hotel_price) == 6:
                    hotel_price = "  " + hotel_price
                if len(hotel_price) == 7:
                    hotel_price = " " + hotel_price
                self.all_hotels.append(hotel_name)
                if i < 9:
                    print(" %d - %s %s %s" % (i + 1, hotel_price, euro_symbol, hotel_name))
                else:
                    print("%d - %s %s %s" % (i + 1, hotel_price, euro_symbol, hotel_name))

            print("\n\tranking:\n")
            # float cast
            new_prices_2 = []
            for element in self.all_prices:
                rank = float(element)
                new_prices_2.append(rank)

            # final list
            list = dict(zip(self.all_hotels, new_prices_2))
            ranking_2 = sorted(list.items(), key=operator.itemgetter(1))
            for k, v in ranking_2:
                if v < 1000.00:
                    print("  ", "{0:.2f}".format(v), k)
                if 999.00 < v < 10000.00:
                    print(" ", "{0:.2f}".format(v), k)
                if v > 9999.00:
                    print("", "{0:.2f}".format(v), k)

            sleep(2)
        except Exception as e:
            self.error = True
            print(e)
            print('Some error occurred while trying to scroll down')


if __name__ == '__main__':
    app = App()

# FIXME: descending design
# 1) init method initializes variables that will be accessible by self from any method of the class
# 2) log in method allows us to log in to access the provider's services
# 3) search engine insert method fills in the search engine fields and clicks on the search button
# 4) the reach target method systematically selects the first objective by clicking on it
