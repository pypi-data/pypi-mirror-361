# Eagle-Eye Scraper

Eagle-Eye Scraper 是一个高效灵活的 Python 数据采集框架。它以原生分布式设计为核心，具有通用性强、框架运行逻辑与采集业务逻辑解耦等特点，非常适合各种数据采集需求。

## 安装

通过 pip 安装 Eagle-Eye Scraper：

```bash
pip install eagle-eye-scraper
```

## 开发指南

* 继承eagle-eye-scraper框架的Spider基类

```python
from eagle_eye_scraper import Spider


class ExampleSpider(Spider):

    def __init__(self):
        # 构造函数严禁传参
        pass

    def crawl(self, **kwargs):
        # 虚函数的实现，可通过kwargs接收入参。
        # 体现采集功能具体逻辑，采集的数据必须写入数据库
        pass

    def parse(self, **kwargs):
        # 虚函数的实现，可通过kwargs接收入参。
        # 体现解析功能功能具体逻辑，从采集的数据库中获取待解析原始数据
        pass
```

* 配置调度规则
    1. 在工程根目录下创建resources目录
    2. 创建一个yml文件，该文件名字以需配置调度的项目业务命名。按照调度配置文件规范，配置相关spider的调度计划。  
       这里以数据采集样例项目的配置文件example-spider-dispatch.yml为例

   ``` yaml
       group_name: 数据采集样例项目  
       dispatchers:
            - cron_exp: '0/3 * * * *'
              spider_class: 'app.spiders.ExampleSpider'
              func_call: 'crawl'
              func_kwargs:
                  - start_time: '2024-10-20'
                  - end_time: '2024-10-26'
  ```

  配置参数解释：
*        group_name：项目名称
*        dispatchers:  调度器列表
*        cron_exp：cron表达式，调度器计划调度时间
*        spider_class：调度执行的spider类的全路径名称
*        func_call：调度执行的函数名称
*        func_kwargs：调度执行的函数入参字典


* 在根包下创建main.py文件，启用eagle-eye-scraper的单机内存调度功能。

```python
import logging
import time
from eagle_eye_scraper.dispatch.dispatcher_selector import enable_ram_dispatch

logger = logging.getLogger()

if __name__ == '__main__':
    enable_ram_dispatch()
    while True:
        logger.info("public procurement collector running...")
        time.sleep(10)
``` 

* docker打包，以main.py文件作为python程序的入口。

```dockerfile
FROM python:3.8.11  
ENV PATH=/opt/nodejs/bin:/usr/local/bin:$PATH 	TimeZone=Asia/Shanghai PYTHONPATH=/code NODE_PATH=/opt/node_modules  
RUN ln -snf /usr/share/zoneinfo/$TimeZone /etc/localtime && echo $TimeZone > /etc/timezone  
ADD debian-bulleye-sources.list /etc/apt/sources.list  
RUN apt-get update -y && apt-get install -y --allow-unauthenticated apt-transport-https supervisor 
RUN mkdir -p /data/logs
WORKDIR /code
COPY app app
COPY resources resources
COPY requirements.txt ./
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/  -r requirements.txt
RUN pip install -i https://test.pypi.org/simple/ eagle-eye-scraper
CMD python /code/app/main.py
```

* 单机运行工程

```shell
docker build . -t public-procurement-collector:latest

docker run -d --name public-procurement-collector -t public-procurement-collector:latest --env-file  .env
```
    	
    	




   	
 

