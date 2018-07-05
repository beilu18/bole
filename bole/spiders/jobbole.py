# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse

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
        front_image=response.meta.get("front_image_url","")



        #标题
        title=response.css(".entry-header h1::text").extract_first()

        #文章封面图
        front_image_url = response.meta.get("front_image_url", "")

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




