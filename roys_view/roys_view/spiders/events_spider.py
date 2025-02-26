# Sam Arkle. Resources used: https://roysviewfrom.com/ for scraping. https://docs.scrapy.org/en/latest/intro/tutorial.html for code tutorials
# Beyond a B: I have created two spiders and output the scraped data to two different files. The comments spider
# carries scrapes data from all relevant pages within the initial page before moving onto the next page.
# I scrape ten attributes per event and three per comment. Due to a format change by the creator of the roysview website,
# I use different scrape methods for certain older pages.
# In summary: Scrape more attributes than needed. Scrape different types of page. Accumulate different items to different files.

import scrapy


class EventsSpider(scrapy.Spider):
    name = 'events'
    start_urls = ['https://roysviewfrom.com/']

    def parse(self, response):

        for event in response.css('article'):
            yield {
                'url': event.css('h4 a::attr(href)').get(),
                'title': event.css('h4.entry-title a::text').get(),
                'team': event.css('h4.entry-title a::text').get().split(' ')[-1],
                'date': event.css('span.mg-blog-date ::text').extract()[1].strip(),
                'categories': [s.strip() for s in event.css('a.newsup-categories ::text').getall()],
                'sample_comment': event.css('div.mg-content p::text').get(),
                'author': event.css('a.auth ::text').get().strip(),
                'date_accessed': response.css('ul.info-left li::text').get().strip(),
                'author_twitter': response.css('ul.mg-social a::attr(href)').get(),
                'background_image_url': response.css('.mg-nav-widget-area-back').get().split('"')[3]

            }

        next_page = response.css('.next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
