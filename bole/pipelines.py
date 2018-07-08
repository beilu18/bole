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
import pymongo




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
class MysqlExportPipline(object):
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

#使用Twisted 框架提供的异步方法入库mysql
class MysqlTwistedPipline(object):
    def __int__(self,dbpool):
        self.dbpool=dbpool

    @classmethod

    def from_settings(cls,settings):
        dbparms=dict(
            host=settings["MYSQL_HOST"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            db=settings["MYSQL_DBNAME"],
            charset="utf8",
            cussorclass=pymysql.cursors.DictCursor,
            use_unicode = True
        )

        dbpool = pymysql.connect("pymysql", **dbparms)
        return cls(dbpool)

    def process_item(self,item,spider):
        # 使用twisted将mysql插入变成一部执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 处理异常

    def handle_error(self, failure):
        print(failure)

        # 处理异步插入的异常

    def do_insert(self,cursor,item):
        insert_sql = """insert into Bole(url_object_id,title,url,front_image_url,front_image_path,
        create_date,pare_num,collect_num,comment_num,tags)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
        cursor.execute(insert_sql, (
        item["url_object_id"], item["title"], item["url"], item["front_image_url"], item["front_image_path"],
        item["create_date"], item["pare_num"], item["collect_num"], item["comment_num"], item["tags"]))


#使用MongoDB存储数据
class MongoPipline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_settings(cls, settings):
        return cls(
            mongo_uri=settings.get('MONGO_URI'),
            mongo_db=settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # 这里通过mongodb进行了一个去重的操作，每次更新插入数据之前都会进行查询，判断要插入的url是否已经存在，如果不存在再进行数据插入，否则放弃数据
        self.db['bole'].update({'url': item["url"]}, {'$set': item}, True)
        return item


