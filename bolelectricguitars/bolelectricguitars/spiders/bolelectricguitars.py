import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from selenium.common.exceptions import NoSuchElementException
import sys
import ssl

# Define a custom Scrapy spider for scraping guitar information from bol.com
class BolGuitarSpider(scrapy.Spider):
    # Name of the spider, used for running it
    name = 'bolelectricguitars'
    # Restrict the spider to a specific domain
    allowed_domains = ['bol.com']
    # URLs where the spider begins crawling
    start_urls = ['https://www.bol.com/nl/nl/l/elektrische-gitaren/43388/']

    # Custom settings for the spider
    custom_settings = {
        'ROBOTSTXT_OBEY': True,  # Respect the robots.txt file
        'AUTOTHROTTLE_ENABLED': True,  # Enable dynamic download delay
        'AUTOTHROTTLE_START_DELAY': 5,  # Initial delay before start (in seconds)
        'DOWNLOAD_DELAY': 2,  # Delay between requests (in seconds)
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,  # Maximum concurrent requests per domain
    }

    # Initialize the spider
    def __init__(self, *args, **kwargs):
        chrome_options = Options()
        # Uncomment to run Chrome in headless mode (no browser UI)
        # chrome_options.add_argument("--headless")

        # Setup proxy settings for the browser
        proxy_url = "127.0.0.1:24000"
        chrome_options.add_argument(f'--proxy-server={proxy_url}')
        # Set a custom user-agent for the browser
        chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"')
        # Ignore SSL and certificate errors
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')

        # Define the path to the ChromeDriver
        chrome_url = r'C:\Users\yunus\Downloads\chromedriver-win64\chromedriver.exe'
        chrome_service = Service(chrome_url)
        # Initialize Selenium WebDriver with Chrome
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    # Method to parse the response and extract data
    def parse(self, response):
        # Loop through each product item and extract details
        for product in response.css('li.product-item--row.js_item_root'):
            yield {
                'title': product.css('a.product-title::text').get(default='').strip(),
                'brand': product.css('a[data-test="party-link"]::text').get(),
                'price': product.css('span.promo-price::text').get(),
                'reviews_count': product.css('div.star-rating::attr(data-count)').get(),
                'product_link': response.urljoin(product.css('a.product-title::attr(href)').get()),
                'stock_availability': product.css('div.product-delivery-highlight::text').get().strip() if product.css('div.product-delivery-highlight::text').get() else None,
            }

        # Handle pagination by following the next page link
        next_page = response.css('.pagination__controls--next a::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            # Make a request to the next page and continue parsing
            yield scrapy.Request(next_page_url, callback=self.parse)

# Proxy setup
if sys.version_info[0] == 2:
    import six
    from six.moves.urllib import request
elif sys.version_info[0] == 3:
    import urllib.request

    def setup_proxy():        
        ctx = ssl.create_default_context()
        ctx.verify_flags = ssl.VERIFY_DEFAULT

        if sys.version_info[0] == 2:
            opener = request.build_opener(
                request.ProxyHandler({'http': 'http://127.0.0.1:24000'}),
                request.HTTPSHandler(context=ctx)
            )
        elif sys.version_info[0] == 3:
            opener = urllib.request.build_opener(
                urllib.request.ProxyHandler({'http': 'http://127.0.0.1:24000'}),
                urllib.request.HTTPSHandler(context=ctx)
            )
    
    setup_proxy()
    
    from w3lib.http import basic_auth_header

    class CustomProxyMiddleware(object):
        def process_request(self, request, spider):
            request.meta['proxy'] = "http://127.0.0.1:24000"
    
    # Conditional import and setup for proxy support based on Python version
if sys.version_info[0] == 2:
    # Python 2 specific imports
    import six
    from six.moves.urllib import request
elif sys.version_info[0] == 3:
    # Python 3 specific import
    import urllib.request

    # Function to setup a proxy server
    def setup_proxy():        
        # Create a default SSL context for handling HTTPS requests
        ctx = ssl.create_default_context()
        # Set default verification flags for SSL
        ctx.verify_flags = ssl.VERIFY_DEFAULT

        # For Python 2, configure an opener with proxy settings
        if sys.version_info[0] == 2:
            opener = request.build_opener(
                request.ProxyHandler({'http': 'http://127.0.0.1:24000'}),  # Set up HTTP proxy
                request.HTTPSHandler(context=ctx)  # Add handler for HTTPS with SSL context
            )
        # For Python 3, configure an opener with proxy settings
        elif sys.version_info[0] == 3:
            opener = urllib.request.build_opener(
                urllib.request.ProxyHandler({'http': 'http://127.0.0.1:24000'}),  # Set up HTTP proxy
                urllib.request.HTTPSHandler(context=ctx)  # Add handler for HTTPS with SSL context
            )
    
    # Execute the proxy setup function
    setup_proxy()
    
    # Import basic authentication header utility
    from w3lib.http import basic_auth_header

    # Custom middleware class for Scrapy
    class CustomProxyMiddleware(object):
        # Method to process each request made by the Scrapy spider
        def process_request(self, request, spider):
            # Set up the proxy for the request using meta attribute
            request.meta['proxy'] = "http://127.0.0.1:24000"