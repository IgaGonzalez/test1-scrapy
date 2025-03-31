import scrapy
from scrapy import Request

class AmazonJobsSpider(scrapy.Spider):
    name = "amazon_jobs"
    allowed_domains = ["amazon.jobs"]
    start_urls = [
        "https://www.amazon.jobs/content/en/job-categories/software-development"
    ]
    
    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                meta={
                    'playwright': True,
                    # Wait for the job cards to load and click the snippet expander buttons
                    'playwright_page_methods': [
                        {"method": "wait_for_selector", "args": ["div.job-card-module_root"]},
                        {"method": "evaluate", "args": ["""
                            () => {
                                // Click all the "read more" buttons so that the full snippet is expanded.
                                document.querySelectorAll('button.footer-module_expando__1hi-H').forEach(btn => btn.click());
                            }
                        """]},
                        {"method": "wait_for_timeout", "args": [1000]}
                    ]
                }
            )
    
    def parse(self, response):
        self.logger.info("Parse method called for: %s", response.url)
        # Adjust the XPath as needed; here we assume each job card is an <li> element
        job_cards = response.xpath('//*[@id="search"]/div/div[2]/ul/li')
        self.logger.info("Found %d job cards", len(job_cards))
        
        for card in job_cards:
            title = card.css("a.header-module_title__9-W3R::text").get()
            relative_url = card.css("a.header-module_title__9-W3R::attr(href)").get()
            job_url = response.urljoin(relative_url) if relative_url else None
            location = card.css("span.job-location::text").get()
            # Extract the snippet text from the listing page.
            # (Because we clicked the expander buttons in start_requests, this should now be fully expanded.)
            snippet_list = card.xpath(".//div[contains(@class, 'job-card-module_content__8sS0J')]/div/text()").getall()
            snippet = " ".join(s.strip() for s in snippet_list if s.strip())
            updated = card.css("span.updated::text").get()
            
            self.logger.info("Position found: %s | URL: %s", title.strip() if title else "N/A", job_url)
            
            if job_url:
                yield Request(
                    url=job_url,
                    callback=self.parse_job_detail,
                    meta={
                        "title": title.strip() if title else "",
                        "location": location.strip() if location else "",
                        "job_url": job_url,
                        "snippet": snippet,
                        "updated": updated.strip() if updated else "",
                        'playwright': True,
                        # Optionally wait for the job detail container on the detail page
                        'playwright_page_methods': [
                            {"method": "wait_for_selector", "args": ["div.job-detail"]}
                        ]
                    }
                )
        
        # --- Handle Pagination (if needed) ---
        next_button = response.css("button[data-test-id='next-page']:not([disabled])")
        if next_button:
            self.logger.info("Next page button found, clicking to load more jobs...")
            yield scrapy.Request(
                response.url,
                callback=self.parse,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        {"method": "click", "args": ["button[data-test-id='next-page']"]},
                        {"method": "wait_for_selector", "args": ["div.job-card-module_root__QYXVA"]},
                        {"method": "wait_for_timeout", "args": [2000]}  # adjust timeout as needed
                    ]
                }
            )
        else:
            self.logger.info("No next page button found. Pagination complete.")
    
    def parse_job_detail(self, response):
        # Retrieve data passed from the listing page
        title = response.meta.get("title", "")
        job_url = response.meta.get("job_url", "")
        updated = response.meta.get("updated", "")
        snippet = response.meta.get("snippet", "")
        
        # Use the job id from the job URL by splitting it (e.g., "https://www.amazon.jobs/jobs/2941522" -> "2941522")
        job_id = job_url.split('/')[-1] if job_url else None
        
        # Optionally, try to extract more precise location details from the detail page
        location_elements = response.xpath("//*[@id='job-detail-body']//ul//li//text()").getall()
        location_detail = " ".join(loc.strip() for loc in location_elements if loc.strip())
        if not location_detail:
            location_detail = response.meta.get("location", "")
        
        # Extract the detailed job data.
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
        
        self.logger.info("Job Detail - Title: %s, Job ID: %s", title, job_id)
        
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
