# version 1.0.0

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

class HbLinksFromMediatorPage:
    def __init__(self, driver, page_url):
        self.driver : webdriver.Chrome = driver
        self.page_url : str = page_url
        self.max_attempts : int = 10
        self.target_url_part = "https://hblinks.pro/archives"

    def __check_valid_url(self):
        for i in ['techyboy4u']:
            if i in self.page_url:
                return True
        return False

    def __get_hblinks(self):
        if not self.__check_valid_url():
            return None
        try:
            wait = WebDriverWait(self.driver, 30)
            self.driver.get(self.page_url)
            main_window = self.driver.current_window_handle

            # STEP 1: Click "Click to Continue"
            verify_btn = wait.until(EC.element_to_be_clickable((By.ID, "verify_btn")))
            verify_btn.click()

            # STEP 2: Close ad tab if it opens
            time.sleep(2)
            for handle in self.driver.window_handles:
                if handle != main_window:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
            self.driver.switch_to.window(main_window)

            # STEP 3: Wait for "Get Links"
            time.sleep(11)

            # STEP 4: Try clicking until correct redirect tab opens
            for attempt in range(1, self.max_attempts + 1):

                try:
                    verify_btn = self.driver.find_element(By.ID, "verify_btn")
                    if verify_btn.text.strip().lower() == "get links":
                        verify_btn.click()
                        time.sleep(3)

                        for handle in self.driver.window_handles:
                            if handle != main_window:
                                self.driver.switch_to.window(handle)
                                current_url = self.driver.current_url

                                if self.target_url_part in current_url:
                                    return current_url
                                else:
                                    self.driver.close()
                                self.driver.switch_to.window(main_window)
                                break
                except Exception as e:
                    print("Error during click or tab check:", e)
                    break

                time.sleep(2)

            print("Failed to get correct redirect after max attempts.")
            return None

        except Exception as ex:
            print(ex)
            return None

    def __get_hubcloud_links_from_hblinks(self) -> str | None:
        try:
            hblinks_url = self.__get_hblinks()
            if not hblinks_url:
                return None
            wait = WebDriverWait(self.driver, 30)

            self.driver.get(hblinks_url)
            entry_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "entry-content")))
            links = entry_div.find_elements(By.TAG_NAME, "a")
            hubcloud_links = [link.get_attribute("href") for link in links if "hubcloud" in link.get_attribute("href")]

            if hubcloud_links:
                self.driver.get(hubcloud_links[0])
                download_link_btn = wait.until(EC.presence_of_element_located((By.ID, "download")))
                direct_download_url = download_link_btn.get_attribute("href")

                return direct_download_url
            else:
                return ""
        except Exception as e:
            print(e)
            return ""

    def get_hubcloud_download_links(self) -> list[tuple[str, str]] | None:
        try:
            url = self.__get_hubcloud_links_from_hblinks()
            if not url:
                return None
            self.driver.get(url)
            time.sleep(2)

            a_tags = self.driver.find_elements(By.TAG_NAME, "a")

            links:list[tuple[str, str]] = []
            for a in a_tags:
                href = a.get_attribute("href")
                text = a.text.strip()
                if href and text:
                    for j in ['pixeldrain.dev', 'storage.googleapis.com', 'pub']:
                        if j in href:
                            links.append((text, href))
                            break
            return links
        except Exception as e:
            print(e)
            return []

    def __get_hubdrive_links_from_hblinks(self) -> str | None:
        try:
            hblinks_url = self.__get_hblinks()
            if not hblinks_url:
                return None
            wait = WebDriverWait(self.driver, 30)

            self.driver.get(hblinks_url)
            entry_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "entry-content")))
            links = entry_div.find_elements(By.TAG_NAME, "a")
            hubdrive_links = [link.get_attribute("href") for link in links if "hubdrive" in link.get_attribute("href")]

            if hubdrive_links:
                return hubdrive_links[0]
            else:
                return ""
        except Exception as e:
            print(e)
            return ""

    def get_hubdrive_download_links(self) -> str | None:
        try:
            url = self.__get_hubdrive_links_from_hblinks()
            if not url:
                return None

            return url
        except Exception as e:
            print(e)
            return ""
