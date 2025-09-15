import scrapy
import logging
from abc import ABC, abstractmethod

class BaseJobSpider(scrapy.Spider, ABC):
    """
    Base spider class for job scraping
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fix: Không sử dụng @property cho logger
        self._logger = logging.getLogger(self.name)
    
    @property
    def logger(self):
        return self._logger
    
    @abstractmethod
    def parse_job_list(self, response):
        """
        Parse job list page and extract job links
        """
        pass
    
    @abstractmethod
    def parse_job_detail(self, response):
        """
        Parse job detail page and extract job information
        """
        pass
    
    def start_requests(self):
        """
        Start scraping from the main page
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_job_list,
                meta={'dont_cache': True}
            )
    
    def parse(self, response):
        """
        Main parsing method
        """
        return self.parse_job_list(response)