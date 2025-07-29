# Eagle-Eye Scraper

**Eagle-Eye Scraper** 是一个高效、灵活且具备原生分布式特性的 Python 数据采集框架。它支持静态/动态网页、API 数据采集，并通过模块化架构实现采集逻辑与业务逻辑的彻底解耦，适合构建可维护、可扩展的数据抓取系统。

---

## ✨ 核心特点

* **原生分布式设计**
  内置对分布式任务调度的支持，轻松扩展至多节点并发采集，适用于大规摸爬取任务。

* **通用采集能力**
  支持静态网页、JavaScript 渲染页面和 API 接口等多种数据源类型，适应各类业务需求。

* **逻辑解耦架构**
  采集引擎逻辑与业务处理逻辑完全分离，便于测试、维护与功能演进。

* **高性能任务调度**
  集成 `APScheduler` 提供异步高效的定时调度能力，支持复杂的任务管理。

* **模块化与插件化设计**
  支持自定义采集器、过滤器、解析器等组件，方便二次开发和集成。

---

## 📦 安装方式

### 基础安装

```bash
pip install eagle-eye-scraper
```

### 安装可选依赖项

根据使用场景，可选择安装如下依赖：

| 组件        | 安装命令                                                   |
| --------- | ------------------------------------------------------ |
| Redis     | `pip install "eagle-eye-scraper[redis]"`               |
| MongoDB   | `pip install "eagle-eye-scraper[mongodb]"`             |
| MySQL     | `pip install "eagle-eye-scraper[mysql]"`               |
| MinIO     | `pip install "eagle-eye-scraper[minio]"`               |
| Pulsar MQ | `pip install "eagle-eye-scraper[mq]"`                  |
| 多组件组合安装   | `pip install "eagle-eye-scraper[redis,mongodb,minio]"` |


> 💡 如果使用的是旧版 pip，请将 `[]` 用引号括起来，例如：
>
> ```bash
> pip install "eagle-eye-scraper[mongo,redis]"
> ```

---

## 🧰 示例用法

```python
from eagle_eye_scraper import Spider

class SimpleSpider(Spider):
    def crawl(self, **kwargs):
        # 模拟从网络抓取数据
        self.raw_data = "<html><title>示例页面</title><body>Hello World</body></html>"
        print("抓取完成")

    def parse(self, **kwargs):
        # 模拟对抓取数据的解析
        title_start = self.raw_data.find("<title>") + 7
        title_end = self.raw_data.find("</title>")
        title = self.raw_data[title_start:title_end]
        print(f"解析得到标题：{title}")

if __name__ == "__main__":
    spider = SimpleSpider()
    spider.run()

```

---

## 📄 License

MIT License


