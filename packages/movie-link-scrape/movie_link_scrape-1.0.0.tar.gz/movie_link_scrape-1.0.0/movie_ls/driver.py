# version 1.0.0

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

class SeleniumDriver:
    def __init__(self, browser_path: str, driver_path: str, headless: bool = True):
        self.browser_path = browser_path
        self.driver_path = driver_path
        self.__headless = headless

        # Checks for legit path
        if not os.path.isfile(self.browser_path):
            raise FileNotFoundError(f"Browser not found at: {self.browser_path}")

        if not os.path.isfile(driver_path):
            raise FileNotFoundError(f"Chromedriver not found at: {self.driver_path}")

    def get_driver(self) -> webdriver.Chrome:
        options = Options()
        options.binary_location = self.browser_path
        if self.__headless:
            options.add_argument("--headless")
        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
