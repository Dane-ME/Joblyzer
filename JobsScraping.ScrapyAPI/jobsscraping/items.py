import scrapy

class JobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    posted_date = scrapy.Field()
    job_type = scrapy.Field()
    salary = scrapy.Field()
    experience_level = scrapy.Field()
    industry = scrapy.Field()
    employment_type = scrapy.Field()
    required_skills = scrapy.Field()
    benefits = scrapy.Field()
    source = scrapy.Field()