from selenium import webdriver
from selenium_stealth import stealth
from dotenv import load_dotenv
import os

load_dotenv()
URL = os.getenv('URL')

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Optional: run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    firefoxOptions = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disabe-dev-shm-usage")


    # Create driver
    driver = webdriver.Chrome(options=options)

    #firefox kullananlar için. Sonradan if kontrolü eklenir.
    moz = webdriver.Firefox(options=firefoxOptions)

    # Apply stealth mode
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    
    driver.get(URL)
    # Your code here
    
    driver.quit()


if __name__ == "__main__":
    main()