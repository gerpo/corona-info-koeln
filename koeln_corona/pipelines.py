# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import jsonlines
import requests
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class KoelnCoronaPipeline:

    channel_id = '-1001348915542'
    token = ''

    def __init__(self):
        self.feed = self._get_feed_headers()
        self.headers = [obj['header'] for obj in self.feed]
        self.new_items = list()

    def process_item(self, item, spider):
        if item['header'] in self.headers:
            raise DropItem(f'Already in feed: {item["header"]}')

        self.new_items.append(item)

        return item

    def _get_feed_headers(self):
        feed = list()
        try:
            with jsonlines.open('feed.jl') as reader:
                for obj in reader:
                    feed.append(obj)
        except:
            pass

        return feed

    def close_spider(self, spider):
        if len(self.new_items) == 0:
            print('Nothing new!!')
            return

        with jsonlines.open('feed.jl', 'w') as writer:
            writer.write_all(self.new_items + self.feed)

        self._send_telegram_messages()

    def _send_telegram_messages(self):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        messages = self._format_messages()
        messages.reverse()

        for message in messages:
            params = {"chat_id": self.channel_id,
                      "text": message,
                      "parse_mode": "markdown"}
            requests.post(url, params=params)

    def _format_messages(self):
        messages = list()
        for new_item in self.new_items:
            header = new_item['header']
            article = '\n'.join(new_item['article'])

            messages.append(f'*{header}* \n \n {article}')

        return messages
