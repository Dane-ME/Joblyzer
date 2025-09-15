import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Get settings
settings = get_project_settings()

# Test spider discovery
from spiders.topdev_spider import TopDevSpider

print("Spider found successfully!")
print(f"Spider name: {TopDevSpider.name}")