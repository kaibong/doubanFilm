# -*- coding: utf-8 -*-
import scrapy


class FilmSpider(scrapy.Spider):
    name = 'film'
    allowed_domains = ['douban.com']
    start_urls = ['http://douban.com/']

    def parse(self, response):
        pass
