import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import AndbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class AndbankSpider(scrapy.Spider):
	name = 'andbank'
	start_urls = ['https://www.andbank.com/sobre-nosotros/sala-de-prensa/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news-list"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('(//div[@class="new-content wysiwyg"]/p)[1]//text()').get().split(', ')[1]
		title = response.xpath('(//h1)[1]//text()').get().strip()
		content = response.xpath('//div[@class="new-excerpt"]//text()').getall() + response.xpath('//div[@class="new-content wysiwyg"]/p[1]/following-sibling::*//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=AndbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
