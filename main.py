from selenium import webdriver
from selenium_stealth import stealth
from dotenv import load_dotenv
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep

load_dotenv()
URL = os.getenv('URL')
TC_ID = os.getenv('TC_ID')
PASSWORD = os.getenv('PASSWORD')

menu_css_selector = "li.ng-scope:nth-child(1)"
grades_css_selector = ".pre-scrollable > div:nth-child(1) > li:nth-child(1) > a:nth-child(1)"

def main():
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")  # Optional: run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    """
    #firefox kullananlar için. Sonradan if kontrolü eklenir.

    firefoxOptions = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Firefox(options=firefoxOptions)
    """

    # Create driver
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    # Apply stealth mode
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    # LOGIN
    driver.get(URL)
    wait.until(EC.presence_of_element_located((By.ID, "username")))

    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")

    username_field.send_keys(TC_ID)
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.RETURN)

    # click menu and grades
    driver.find_element(By.CSS_SELECTOR, menu_css_selector).click()
    driver.find_element(By.CSS_SELECTOR, grades_css_selector).click()

    sleep(5) # grade table info ...

    driver.quit()

if __name__ == "__main__":
    main()