import scrapy
from datetime import datetime


class TopDevSpider(scrapy.Spider):
    name = 'topdev'
    allowed_domains = ['api.topdev.vn']
    start_page = 1

    # Endpoint API
    api_url = (
        "https://api.topdev.vn/td/v2/jobs?"
        "fields[job]=id,slug,title,salary,company,extra_skills,skills_str,skills_arr,"
        "skills_ids,job_types_str,job_levels_str,job_levels_arr,job_levels_ids,"
        "addresses,status_display,detail_url,job_url,salary,published,refreshed,"
        "applied,candidate,requirements_arr,packages,benefits,content,features,"
        "is_free,is_basic,is_basic_plus,is_distinction&"
        "fields[company]=slug,tagline,addresses,skills_arr,industries_arr,industries_str,"
        "image_cover,image_galleries,benefits&page={page}&locale=en_US&ordering=jobs_new"
    )

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def start_requests(self):
        """Bắt đầu crawl từ page 1"""
        yield scrapy.Request(
            url=self.api_url.format(page=self.start_page),
            callback=self.parse_api,
            meta={'page': self.start_page}
        )

    def parse_api(self, response):
        """Parse JSON từ API"""
        try:
            data = response.json()
            jobs = data.get("data", [])
            current_page = response.meta['page']

            if not jobs:
                self.logger.info(f"Page {current_page} empty, stopping crawl.")
                return

            for job in jobs:
                company = job.get("company", {})

                job_data = {
                    "id": job.get("id"),
                    "title": job.get("title"),
                    "company": company.get("slug") or "Company Not Found",
                    "location": job.get("addresses"),
                    "description": job.get("content"),
                    "url": job.get("detail_url") or job.get("job_url"),
                    "posted_date": job.get("published"),
                    "job_type": job.get("job_types_str"),
                    "salary": job.get("salary"),
                    "experience_level": job.get("job_levels_str"),
                    "industry": company.get("industries_str"),
                    "employment_type": job.get("job_types_str"),
                    "required_skills": job.get("skills_str"),
                    "benefits": job.get("benefits"),
                    "source": "topdev",
                    "scraped_at": datetime.utcnow(),
                }

                yield job_data

            # Crawl page tiếp theo
            next_page = current_page + 1
            yield scrapy.Request(
                url=self.api_url.format(page=next_page),
                callback=self.parse_api,
                meta={'page': next_page}
            )

        except Exception as e:
            self.logger.error(f"Error parsing API response: {e}")
