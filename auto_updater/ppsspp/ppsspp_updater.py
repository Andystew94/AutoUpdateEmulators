import re
from selenium import webdriver
from selenium.webdriver.common.by import By


class PPSSPPScraper:
    def __init__(self, url, download_name_contains):
        self.url = url
        self.download_name_contains = download_name_contains
        self.driver = self._configure_headless_chrome()

    def _configure_headless_chrome(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        return webdriver.Chrome(options=options)

    def _get_ppsspp_download_url(self):
        try:
            self.driver.get(self.url)
            self.driver.implicitly_wait(10)
            download_links = self.driver.find_elements(By.XPATH, "//a[@href]")

            for link in download_links:
                href = link.get_attribute("href")
                if self.download_name_contains in href:
                    return href  # Return the first matching link

            return None  # Return None if no matching link is found
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _extract_version_from_url(self, url):
        pattern = r'rev=(.*?)&'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def _print_results(self, ppsspp_win_zip_link):
        if ppsspp_win_zip_link:
            print(
                f"PPSSPP download URL containing {self.download_name_contains}:")
            print(ppsspp_win_zip_link)

            # Extract version information from the URL
            version = self._extract_version_from_url(ppsspp_win_zip_link)
            if version:
                print(f"Extracted version: {version}")
            else:
                print("Version information not found in the URL.")
        else:
            print(
                f"No PPSSPP download URL containing {self.download_name_contains} found.")

    def scrape_ppsspp_download_info(self):
        # Get the first PPSSPP download URL containing the specified string
        ppsspp_win_zip_link = self._get_ppsspp_download_url()

        # Print results
        self._print_results(ppsspp_win_zip_link)

        # Close the browser
        self.driver.quit()


if __name__ == "__main__":
    # Example usage of the PPSSPPScraper class
    scraper = PPSSPPScraper(
        url="https://buildbot.orphis.net/ppsspp/index.php?m=fulllist",
        download_name_contains="windows-amd64"
    )
    scraper.scrape_ppsspp_download_info()
