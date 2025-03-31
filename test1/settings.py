BOT_NAME = 'test1'

SPIDER_MODULES = ['test1.spiders']
NEWSPIDER_MODULE = 'test1.spiders'
# Use the AsyncioSelectorReactor (required for Playwright)
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Enable the Playwright middleware
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# (Optional) Set some Playwright launch options if needed:
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,  # Set to False to see the browser window
    # Add any other browser launch options you need
}

# Optional: Set logging and feed exports
LOG_LEVEL = "INFO"
FEEDS = {
    "jobs.jsonl": {"format": "jsonlines"},
}