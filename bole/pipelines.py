# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from scrapy.exporters import JsonItemExporter

class BolePipeline(object):
    def process_item(self, item, spider):
        return item


#自定义导出到本地Json文件
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file=codecs.open("article.json","w",encoding='utf-8')
    def process_item(self,item,spider):
        lines=json.dumps(dict(item))