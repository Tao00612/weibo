import math
import scrapy
from urllib import parse


# str1 = 'haha哈哈'
# str2 = parse.quote(str1)  # quote()将字符串进行编码
# str3 = parse.unquote(str2)  # 解码字符串


class WbSpider(scrapy.Spider):
	name = 'wb'
	# allowed_domains = ['weibo.com']
	start_urls = ['https://s.weibo.com/top/summary?cate=realtimehot']

	def parse(self, response, **kwargs):
		li_list = response.xpath('//*[@id="pl_top_realtimehot"]/table/tbody/tr')[1:]
		print(len(li_list))
		for li in li_list:
			top_word = li.xpath('./td[2]/a/text()').extract_first()
			top_word = f'=1&q=#{top_word}#'
			top_word_str = parse.quote(top_word)
			# top_word_str = parse.quote('=1&q=#李子柒另一半得会挖地#')
			url = f'https://m.weibo.cn/api/container/getIndex?containerid=231522type{top_word_str}&page_type=searchall&page=1'
			yield scrapy.Request(
				url=url,
				callback=self.parse_url_list,
				meta={"url": url}
			)

	def parse_url_list(self, response):
		url = response.meta.get('url')
		json_data = response.json()
		content_list = json_data['data']['cards']
		count_content = json_data.get('data').get('cardlistInfo')
		if count_content:
			count_content = int(count_content.get('page_size'))
			page_count = math.ceil(json_data['data']['cardlistInfo']['total'] / count_content)
			for content in content_list:
				item = {}
				if content.get('mblog',None):
					item['hot_word'] = json_data['data']['cardlistInfo']['cardlist_title']
					item['time'] = content['mblog']['created_at']
					item['content'] = content['mblog']['raw_text'].replace('\u200b', '')
					item['p_tool'] = content['mblog']['source']
					item['comment_count'] = content['mblog']['comments_count']
					item['like_count'] = content['mblog']['attitudes_count']
					item['forward_count'] = content['mblog']['reposts_count']
					item['Upload'] = content['mblog']['user']['screen_name']
					item['fans_count'] = content['mblog']['user']['followers_count']
					item['follower_count'] = content['mblog']['user']['follow_count']
					item['weibo_id'] = content['mblog']['user']['id']
					item['url'] = content['scheme']
					yield item

			page_url, page_now = url.split('page=')
			if page_count > int(page_now):
				page_now = str(int(page_now) + 1)
				next_url = page_url + 'page=' + page_now
				yield scrapy.Request(
					url=next_url,
					callback=self.parse_url_list,
					meta={"url": next_url}
				)
