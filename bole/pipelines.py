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


#自定义导出到本地json文件
"""
__init__（）构建对象，打开文件，scrapy调用process_item函数，对数据进行处理，
将数据已json格式写入文件，操作完成，关闭文件。
"""
class JsonWithEncodingPipeline(object):
    #爬虫初始化调用
    def __init__(self):
        #打开json文件，使用encode解决编码问题
        self.file=codecs.open("article.json","w",encoding='utf-8')

    #重写item处理
    def process_item(self,item,spider):
        # 处理字典，输出中文
        lines=json.dumps(dict(item),ensure_ascii=False)+"\n"
        #一行数据写入
        self.file.write(lines)
        return item
    #爬虫结束调用
    def spider_close(self,spider):
        #关闭文件句柄
        self.file.close()

#scrapy自带的的写入本地json文件的类
class JsonExportPipline(object):
    def __init__(self):
        self.file=open('crticleExport.json','wb')
        self.exporter=JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item