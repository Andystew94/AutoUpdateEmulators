import logging
from subprocess import check_call

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
except ImportError as e:
    print(f"Error importing required module: {e}")
    print("Installing necessary modules...")
    try:
        check_call(['pip', 'install', 'selenium'])
        check_call(["pip", "install", "--upgrade", "selenium"])
        from selenium import webdriver
        from selenium.webdriver.common.by import By
    except Exception as install_error:
        print(f"Error installing module: {install_error}")
        exit(1)


class WebScrapper:
    def __init__(self):
        try:
            logging.info("Initialising selenium for scraping...")
            self.driver = self._configure_headless_chrome()
            logging.info("Initialisation complete")
        except Exception as e:
            logging.error(f"Failed to initialise selenium: {e}")
            raise SystemError("Failed to initialise selenium")

    def _configure_headless_chrome(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        return webdriver.Chrome(options=options)

    def get_URL(self, url):
        self.driver.get(url)

    def wait(self, time=10):
        self.driver.implicitly_wait(time)

    def find_elements(self, reference="//a[@href]"):
        return self.driver.find_elements(By.XPATH, reference)

    def quit(self):
        self.driver.quit()


def main():
    try:
        scrapper = WebScrapper()
        sample_url = "https://example.com"  # Replace with your desired URL
        scrapper.get_URL(sample_url)
        # You can modify the XPath as required
        elements = scrapper.find_elements("//a[@href]")
        for element in elements:
            # Print URLs for demonstration
            print(element.get_attribute("href"))
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
    finally:
        scrapper.quit()


if __name__ == "__main__":
    main()
