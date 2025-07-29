# version 1.0.0

from selenium import webdriver
import os

class WebPageExtractor:
    def __init__(self, driver:webdriver.Chrome, save_to_file=False, save_to_file_name="webpage.html"):
        self.driver : webdriver.Chrome = driver
        self.save_to_file : bool = save_to_file
        self.save_to_file_name : str = save_to_file_name

    def extract(self, url: str):
        try:
            self.driver.get(url)

            # save the page source
            html = self.driver.page_source

            if self.save_to_file:
                WebPageExtractor.save_html_to_file(html, filename=self.save_to_file_name)

            # self.driver.quit()

            return html
        except Exception as ex:
            print(ex)
            return ""

    @staticmethod
    def save_html_to_file(html, filename):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(html)

    @staticmethod
    def load_html_from_file(filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"File not found: {filename}")

        with open(filename, "r", encoding="utf-8") as file:
            html_content = file.read()

        return html_content