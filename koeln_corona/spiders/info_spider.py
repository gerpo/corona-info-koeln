import scrapy


class InfoSpider(scrapy.Spider):
    name = "info"

    def start_requests(self):
        urls = [
            'https://www.koeln.de/koeln/nachrichten/lokales/coronavirus-in-koeln-der-aktuelle-stand_1144487.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        header = None
        article = list()
        for p in response.css('div.e-content')[0].css('p'):
            text = p.xpath('normalize-space(.)').extract_first().strip()
            if text.startswith('++'):
                if header:
                    yield {'header': header, 'article': article}
                header = text
                article = list()

            if header and not text.startswith('++'):
                article.append(text)
