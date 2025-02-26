# Sam Arkle. See events_spider.py for more

import scrapy


class CommentsSpider(scrapy.Spider):
    name = 'comments'
    start_urls = ['https://roysviewfrom.com/']

    def parse(self, response):
        comment_page_link = response.css('h4 a::attr(href)')
        yield from response.follow_all(comment_page_link, self.parse_comment)

        next_page = response.css('.next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_comment(self, response):
        for block in response.css('main'):
            if block.css('blockquote p::text') is not None:
                for comment in block.css('blockquote p::text'):
                    yield {
                        'url': str(response).split(" ")[1][:-1],
                        'title': block.css('h1.title a::text').get().strip(),
                        'comment': comment.get().strip(),

                    }
            else:
                for comment in block.css('p::text'):
                    yield {
                        'url': str(response).split(" ")[1][:-1],
                        'title': block.css('h1.title a::text').get().strip(),
                        'comment': comment.get().strip(),

                    }
