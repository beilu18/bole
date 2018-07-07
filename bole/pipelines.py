# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from scrapy.exporters import JsonItemExporter
import pymysql
from scrapy.pipelines.images import ImagesPipeline




class BolePipeline(object):
    def process_item(self, item, spider):
        return item



"""
__init__（）构建对象，打开文件，scrapy调用process_item函数，对数据进行处理，
将数据已json格式写入文件，操作完成，关闭文件。
"""
#自定义导出到本地json文件
class JsonWithEncodingPipeline(object):
    #爬虫初始化调用
    def __init__(self):
        #打开json文件，使用encode解决编码问题
        self.file=codecs.open("article.json","w",encoding='utf-8')

    #重写item处理
    def process_item(self,item,spider):
        # 处理字典，输出中文
        lines=json.dumps(dict(item),ensure_ascii=False)+'\n'
        #一行数据写入
        self.file.write(lines)
        return item
    #爬虫结束调用
    def spider_close(self,spider):
        #关闭文件句柄
        self.file.close()

#scrapy自带的的json export导出json文件
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


#获取图片文件的路径
class ArticleImagePipeline(ImagesPipeline):
    #继承ImagesPipeline 获取保存路径必须重置item_completed函数
    def item_completed(self,results,item,info):
        if 'front_image_url' in item:       #判断路径是否存在
            for ok,value in results:
                image_file_path=value["path"]
                item["front_image_path"]=image_file_path
                return item




"""
存入数据库,一种是同步，一种是异步
1、同步操作一条语句不执行完不会执行下一条语句。但是我们scrapy的解析速度很快如果入库的速度很慢的话就会造成阻塞
"""
#同步写入mysql数据库
class mysqlExportPipline(object):
    def __init__(self):
        self.conn=pymysql.connect('localhost','root','123456','Crawler',charset='utf8',use_unicode=True)
        self.cursor=self.conn.cursor()  #获取连接对象

    def process_item(self,item,spider):
        insert_sql="""insert into Bole(url_object_id,title,url,front_image_url,front_image_path,
create_date,pare_num,collect_num,comment_num,tags)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
        self.cursor.execute(insert_sql, (item["url_object_id"], item["title"], item["url"], item["front_image_url"], item["front_image_path"],
        item["create_date"], item["pare_num"], item["collect_num"], item["comment_num"],item["tags"]))

        self.conn.commit()

        #可以添加判断sql执行情况，添加回滚机制rollback()

    def spider_closed(self,spider):
        self.conn.close()

