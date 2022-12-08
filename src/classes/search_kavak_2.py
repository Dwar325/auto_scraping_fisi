from .auto import Auto
from .search import Search

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from re import split


class SearchKavak2(Search):

    def __init__(self, brand: str, model: str, from_year: int, until_year: int, quantity: int):
        Search.__init__(self, brand, model, from_year, until_year, quantity)
        self.__site = "https://www.kavak.com/pe/carros-usados"
        self.__driver = None
        self.autos = []

    def _filter(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--window-size=1920,1080")
        self.__driver = webdriver.Chrome(service=Service(self._path), options=options)
        self.__site = self.__get_site_fixed(self._model)
        self.__driver.get(self.__site)

    def __get_url(self):
        elements_with_urls = self.__driver.find_elements(
            By.XPATH, value="//a[@class='card-inner']")
        urls = [url.get_attribute('href') for url in elements_with_urls]
        return urls

    def __get_price(self):
        new_prices = []
        elements_with_prices = self.__driver.find_elements(
            By.XPATH, value="//div[1][@class='payment-tax-wrapper']//span[@class='payment-total payment-highlight']")
        prices = [price.text for price in elements_with_prices]
        for text in prices:
            no_dollar = text.replace('US$ ', '')
            no_dollar_coma = no_dollar.replace(',', '.')
            new_prices.append(no_dollar_coma)
        return new_prices

    def __get_year(self):
        only_years = []
        elements_with_years = self.__driver.find_elements(
            By.XPATH, value="//p[@class='car-details']")
        years = [year.text for year in elements_with_years]
        for text in years:
            result = split('\D+ ', text)
            only_years.append(result[0])
        return only_years

    def get_autos(self):
        i = 0
        self._filter()
        link_list = self.__get_url()
        price_list = self.__get_price()
        year_list = self.__get_year()
        while i < len(price_list):
            link = link_list[i]
            price = price_list[i]
            year = year_list[i]
            auto = Auto(self._brand, self._model, year, price, link)
            if (int(auto.get_year()) >= self._from_year) and (int(auto.get_year()) <= self._until_year):
                self.autos.append(auto)
            i += 1
        correct_list = self.__order_by_price(self.autos)
        correct_list = self.__split_list(correct_list, self._quantity)
        return correct_list

    def __order_by_price(self, cars: list):
        less = []
        equal = []
        greater = []
        if len(cars) > 1:
            pivot = float(cars[0].get_price())
            for x in cars:
                if float(x.get_price()) < pivot:
                    less.append(x)
                elif float(x.get_price()) == pivot:
                    equal.append(x)
                elif float(x.get_price()) > pivot:
                    greater.append(x)
            return self.__order_by_price(less) + equal + self.__order_by_price(greater)
        else:
            return cars

    def __get_site_fixed(self, model: str):
        site = f"https://www.kavak.com/pe/autos-{model}/orden-menor-precio/carros-usados"
        if ' ' in model:
            words = split(' ', model)
            site = f"https://www.kavak.com/pe/autos-{words[0]}_{words[1]}/orden-menor-precio/carros-usados"
        return site

    def __split_list(self, objects: list, until):
        return objects[:until]
