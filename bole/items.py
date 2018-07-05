# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BoleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title=scrapy.Field()    #标题
    url=scrapy.Field()      #获取文章url
    front_image_url=scrapy.Field()  #封面图url
    front_image_path = scrapy.Field()  # 封面图保存路径
    create_date=scrapy.Field()  #发布日期
    pare_num=scrapy.Field()     #点赞数
    collect_num=scrapy.Field()  #收藏数
    comment_num=scrapy.Field()  #评论数
    content=scrapy.Field()      # 文章内容
    tags=scrapy.Field()         #文章类别

    url_object_id=scrapy.Field()  #文章id

    pass
