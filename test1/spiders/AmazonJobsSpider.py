import scrapy
from scrapy_playwright.page import PageMethod

class AmazonJobsSpider(scrapy.Spider):
    name = "amazon_jobs"
    allowed_domains = ["amazon.jobs"]
    start_urls = [
        "https://www.amazon.jobs/content/en/job-categories/software-development"
    ]

    def start_requests(self):
        for url in self.start_urls:
            self.logger.info("Starting request for %s", url)
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.job-card-module_root__QYXVA", timeout=60000),
                        PageMethod("evaluate", """
                            () => {
                                // Click all "read more" buttons to expand snippets.
                                document.querySelectorAll('button.footer-module_expando__1hi-H')
                                    .forEach(btn => btn.click());
                            }
                        """),
                        PageMethod("wait_for_timeout", 1000)
                    ],
                },
            )

    async def parse(self, response):
        page = response.meta.get("playwright_page")
        self.logger.info("Inside parse. Playwright page: %s", page)
        if not page:
            self.logger.error("No playwright page found in response meta!")
            return

        job_cards = response.xpath('//*[@id="search"]/div/div[2]/ul/li')
        self.logger.info("Found %d job cards", len(job_cards))
        for card in job_cards:
            title = card.css("a.header-module_title__9-W3R::text").get()
            relative_url = card.css("a.header-module_title__9-W3R::attr(href)").get()
            job_url = response.urljoin(relative_url) if relative_url else None
            location = card.css("span.job-location::text").get()
            snippet_list = card.xpath(".//div[contains(@class, 'job-card-module_content__8sS0J')]/div/text()").getall()
            snippet = " ".join(s.strip() for s in snippet_list if s.strip())
            updated = card.css("span.updated::text").get()
            
            if job_url:
                self.logger.info("Job found: %s at %s", title, job_url)
                yield scrapy.Request(
                    url=job_url,
                    callback=self.parse_job_detail,
                    meta={
                        "title": title.strip() if title else "",
                        "location": location.strip() if location else "",
                        "job_url": job_url,
                        "snippet": snippet,
                        "updated": updated.strip() if updated else "",
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "#job-detail-body", timeout=60000)
                        ],
                    },
                )

        # Pagination: check for next page button.
        self.logger.info("Looking for the next page button.")
        try:
            next_button = await page.query_selector("button[data-test-id='next-page']:not([disabled])")
        except Exception as e:
            self.logger.error("Error querying next page button: %s", e)
            next_button = None

        if next_button:
            self.logger.info("Next page button found, clicking to load more jobs...")
            await next_button.click()
            self.logger.info("Button clicked, waiting for new job cards to load...")
            await page.wait_for_timeout(2000)
            await page.wait_for_selector("div.job-card-module_root__QYXVA", timeout=60000)
            new_html = await page.content()
            self.logger.info("NEW HTML snippet: %s", new_html[:100])
            
            # Create a new meta that explicitly passes the page object.
            new_meta = response.meta.copy()
            new_meta["playwright_page"] = page
            new_response = response.replace(body=new_html)
            new_response.request.meta.update(new_meta)
            async for item in self.parse(new_response):
                yield item
        else:
            self.logger.info("No next page button found. Pagination complete.")
            await page.close()

    async def parse_job_detail(self, response):
        title = response.meta.get("title", "")
        job_url = response.meta.get("job_url", "")
        updated = response.meta.get("updated", "")
        snippet = response.meta.get("snippet", "")
        
        job_id = job_url.split('/')[-1] if job_url else None
        
        location_elements = response.xpath("//*[@id='job-detail-body']//ul//li//text()").getall()
        location_detail = " ".join(loc.strip() for loc in location_elements if loc.strip())
        if not location_detail:
            location_detail = response.meta.get("location", "")
        
        description_list = response.xpath(
            "//div[contains(@class,'section') and h2[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'DESCRIPTION')]]//p//text()"
        ).getall()
        basic_quals_list = response.xpath(
            "//div[contains(@class,'section') and h2[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'BASIC QUALIFICATIONS')]]//p//text()"
        ).getall()
        preferred_quals_list = response.xpath(
            "//div[contains(@class,'section') and h2[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'PREFERRED QUALIFICATIONS')]]//p//text()"
        ).getall()
        
        description = " ".join(d.strip() for d in description_list if d.strip())
        basic_quals = " ".join(b.strip() for b in basic_quals_list if b.strip())
        preferred_quals = " ".join(p.strip() for p in preferred_quals_list if p.strip())
        
        self.logger.info("Parsed job detail for job: %s", title)
        yield {
            "title": title,
            "location": location_detail,
            "job_url": job_url,
            "snippet": snippet,
            "updated": updated,
            "description": description,
            "basic_qualifications": basic_quals,
            "preferred_qualifications": preferred_quals,
            "job_id": job_id,
        }
