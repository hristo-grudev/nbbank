import scrapy

from scrapy.loader import ItemLoader

from ..items import NbbankItem
from itemloaders.processors import TakeFirst
base = 'https://nbbank.com/Channel?ChannelID=130&Page={}'


class NbbankSpider(scrapy.Spider):
	name = 'nbbank'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		print(response)
		post_links = response.xpath('//div[contains(@class, "article ")]')
		for post in post_links:
			url = 'https://nbbank.com' + post.xpath('.//a[@class="article_title"]/@href').get()
			date = post.xpath('.//div[@class="article_date"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		if post_links:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date):
		print(response)
		title = response.xpath('//span[@class="page_heading_inner"]/text()').get()
		description = response.xpath('//div[@class="page_content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=NbbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
