# 🕷️ Scrapy Project: Test1

Welcome to the **Test1 Scrapy Project**! 🚀 This project is designed to scrape data from websites using the powerful [Scrapy](https://scrapy.org/) framework. It includes custom spiders, middleware, and configurations to make web scraping efficient and scalable. 🎉

---

## 📂 Project Structure

Here's an overview of the project structure:

```
test1/
├── test1/items.py          # Define the data structure for scraped items
├── test1/middlewares.py    # Custom middleware for processing requests and responses
├── pipelines.py            # Define pipelines to process scraped data
├── settings.py             # Project settings for Scrapy
├── spiders/                # Directory containing all spiders
│   ├── test_spider.py      # Example spider for testing
│   └── AmazonJobsSpider.py # Spider for scraping Amazon job listings
scrapy.cfg                  # Scrapy configuration file
```

---

## 🛠️ Features

- **Custom Spiders** 🕷️: Includes spiders like `TestSpider` and `AmazonJobsSpider` for targeted scraping.
- **Middleware** 🔧: Custom middleware to handle requests and responses efficiently.
- **Playwright Integration** 🎭: Uses `scrapy-playwright` for handling JavaScript-heavy websites.
- **Data Pipelines** 📦: Process and store scraped data seamlessly.

---

## 🚀 Getting Started

### 1️⃣ Prerequisites

Ensure you have the following installed:

- Python 3.10+ 🐍
- Scrapy 🕷️
- Playwright 🎭

### 2️⃣ Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd test1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install
   ```

### 3️⃣ Running a Spider

Run the `test_spider` to test the setup:
```bash
scrapy crawl test_spider
```

Run the `AmazonJobsSpider` to scrape job listings:
```bash
scrapy crawl AmazonJobsSpider
```

---

## ⚙️ Configuration

### Scrapy Settings

The project settings are defined in `test1/settings.py`. Key configurations include:

- **User-Agent**: Customize the user agent for requests.
- **Middleware**: Enable `PlaywrightMiddleware` for JavaScript rendering.
- **Pipelines**: Configure data pipelines for processing scraped items.

### Playwright Integration

Ensure `scrapy-playwright` is installed and configured in the settings:
```python
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
```

---

## 📊 Output

Scraped data can be exported in various formats:
```bash
scrapy crawl <spider_name> -o output.json
```

---

## 🐛 Troubleshooting

- **ModuleNotFoundError**: Ensure `scrapy-playwright` is installed:
  ```bash
  pip install scrapy-playwright
  ```

- **Playwright Issues**: Ensure Playwright browsers are installed:
  ```bash
  playwright install
  ```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. 🛠️

---

## 📜 License

This project is licensed under the MIT License. 📄

---

## 🌟 Acknowledgments

- [Scrapy](https://scrapy.org/)
- [Playwright](https://playwright.dev/)

Happy Scraping! 🎉