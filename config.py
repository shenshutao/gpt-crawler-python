class Config:
    def __init__(self, url, match, selector, max_pages_to_crawl, output_file_name, cookie=None):
        """
        初始化配置类。

        :param url: str - 爬虫开始抓取的初始URL。
        :param match: str - 用于匹配链接的模式字符串，通常使用通配符。
        :param selector: str - 页面中要提取内容的CSS选择器。
        :param max_pages_to_crawl: int - 最大页面抓取数，防止无限抓取。
        :param output_file_name: str - 结果输出到的JSON文件名。
        :param cookie: dict - 可选，包含cookie信息的字典，格式如{'name': 'cookie_name', 'value': 'cookie_value', 'url': 'cookie_url'}。
        """
        self.url = url
        self.match = match
        self.selector = selector
        self.max_pages_to_crawl = max_pages_to_crawl
        self.output_file_name = output_file_name
        self.cookie = cookie
