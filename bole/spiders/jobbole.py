# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from bole.items import BoleItem
from bole.utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/114185//']

    def parse(self, response):
        """
        1、获取文章列表url，交给scrapy解析
        2、获取下一页url交给scrapy下载，下载完parse
        3、使用xpath解析
        4、当获取的url不完整的时候，一般response.url+post_url拼接完整url地址

        :param response:
        :return:
        """
        #获取文章列表url
        article_notes=response.xpath("//div[@class='post floated-thumb']/div[@class='post-thumb']/a")
        for article_note in article_notes:
            #每篇文章url
            article_url=article_note.xpath("./@href").extract_first()
            #每篇文章封面图url
            article_img_url=article_note.xpath("./img/@src").extract_first()

            #callback回调函数，回调到parse_detail函数，对每个网页进行解析
            yield Request(url=parse.urljoin(response.url,article_url),meta={"front_image_url":article_img_url},callback=self.parse_detail)

        #下一页
        next_url=response.xpath("//a[@class='next page-numbers']/@href").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)

    def parse_detail(self, response):
        #文章封面图,通过回调函数callback，从parse函数中拿到图片url
        front_image_url=response.meta.get("front_image_url","")

        #标题
        title=response.css(".entry-header h1::text").extract_first()

        #发布日期
        create_date=response.css(".entry-meta-hide-on-mobile::text").extract_first().strip().replace('·','').strip()
        #正则写法
        # create_date=re.match("([0-9/].*)",response.css(".entry-meta-hide-on-mobile::text").extract()[0].strip())

        #点赞数
        parse_nums=response.css(".vote-post-up h10::text").extract_first()
        if parse_nums:
            pare_num=int(parse_nums)
        else:
            pare_num=0

        #收藏数
        collect_nums=re.match(".*?(\d+).*",response.css(".bookmark-btn::text").extract_first())
        if collect_nums:
            collect_num=int(collect_nums.group(1))
        else:
            collect_num=0

        #评论数
        comment_nums=re.match(".*?(\d).*",response.css("a[href='#article-comment'] span::text").extract_first())
        if comment_nums:
            comment_num=int(comment_nums.group(1))
        else:
            comment_num=0

        #文章内容
        content=response.css(".entry ::text").extract()

        #文章类别
        tag_lists=response.css(".entry-meta-hide-on-mobile a::text").extract()
        #去掉重复评论
        tag_list=[element for element in tag_lists if not element.strip().endswith("评论")]
        tags=",".join(tag_list)

        #保存到items字典中
        article_item=BoleItem()
        article_item["title"]=title
        article_item["pare_num"]=pare_num
        article_item["collect_num"]=collect_num
        article_item["comment_num"]=comment_num
        article_item["content"]=content
        article_item["tags"]=tags
        article_item["url"]=response.url
        article_item["front_image_url"]=[front_image_url]   #图片下载默认接受数组
        article_item["url_object_id"]=get_md5(response.url)

        #对创建日期特殊处理
        from datetime import datetime
        try:
            create_date=datetime.strptime(create_date,'%Y/%m/%d').date()
        except Exception as e:
            create_date=datetime.now().date()

        article_item["create_date"]=create_date

        yield article_item




