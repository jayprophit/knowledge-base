"""
Web Automation Module for the Knowledge Base Assistant
Supports browser automation tasks for intelligent agents, including:
- Automated navigation and interaction
- Form filling and submission
- Screenshot capture
- Task scripting
- Headless and visible browser modes
- Playwright and Selenium support
"""

import logging
import os
from typing import Dict, Any, Optional

# Try Playwright first
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Try Selenium as fallback
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)

class WebAutomation:
    def __init__(self, headless: bool = True, use_playwright: bool = True):
        self.headless = headless
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.browser = None
        self.context = None
        self.page = None
        self.driver = None
        if not self.use_playwright and not SELENIUM_AVAILABLE:
            raise ImportError("Neither Playwright nor Selenium is available.")

    def __enter__(self):
        if self.use_playwright:
            self._start_playwright()
        else:
            self._start_selenium()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.use_playwright:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
        else:
            if self.driver:
                self.driver.quit()

    def _start_playwright(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        logger.info("Started Playwright browser")

    def _start_selenium(self):
        chrome_options = ChromeOptions()
        if self.headless:
            chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info("Started Selenium Chrome driver")

    def goto(self, url: str, wait_selector: Optional[str] = None, timeout: int = 10000):
        logger.info(f"Navigating to {url}")
        if self.use_playwright:
            self.page.goto(url, timeout=timeout)
            if wait_selector:
                self.page.wait_for_selector(wait_selector, timeout=timeout)
        else:
            self.driver.get(url)
            # Selenium does not have native wait_for_selector, but can be extended

    def fill_form(self, selectors_and_values: Dict[str, str]):
        logger.info(f"Filling form fields: {selectors_and_values}")
        if self.use_playwright:
            for selector, value in selectors_and_values.items():
                self.page.fill(selector, value)
        else:
            for selector, value in selectors_and_values.items():
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    elem.clear()
                    elem.send_keys(value)
                except Exception as e:
                    logger.error(f"Selenium failed to fill {selector}: {e}")

    def click(self, selector: str):
        logger.info(f"Clicking element: {selector}")
        if self.use_playwright:
            self.page.click(selector)
        else:
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                elem.click()
            except Exception as e:
                logger.error(f"Selenium failed to click {selector}: {e}")

    def screenshot(self, path: str = "screenshot.png"):
        logger.info(f"Capturing screenshot to {path}")
        if self.use_playwright:
            self.page.screenshot(path=path)
        else:
            self.driver.save_screenshot(path)

    def get_content(self) -> str:
        if self.use_playwright:
            return self.page.content()
        else:
            return self.driver.page_source

    def run_script(self, script: str) -> Any:
        logger.info(f"Running script: {script[:60]}")
        if self.use_playwright:
            return self.page.evaluate(script)
        else:
            return self.driver.execute_script(script)

# Example automation workflow
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = "https://example.com/login"
    form = {"#username": "testuser", "#password": "secret"}
    with WebAutomation(headless=True, use_playwright=True) as bot:
        bot.goto(url)
        bot.fill_form(form)
        bot.click("button[type='submit']")
        bot.screenshot("login_result.png")
        html = bot.get_content()
        print(f"Page content length: {len(html)}")
