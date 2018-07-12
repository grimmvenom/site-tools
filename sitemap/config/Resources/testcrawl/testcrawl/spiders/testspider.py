#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
import scrapy


class BSRSpider(scrapy.Spider):
    name = "BSR"
    start_urls = [
        'http://www.ford.com',
    ]

    def parse(self, response):
        page = response.url.split("/")[-1]
        filename = 'bsr-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)

"""

import scrapy


class BSRSpider(scrapy.Spider):
    name = "BSR"
    handle_httpstatus_list = [301, 302]
    allowed_domains = ["ford.com"]
    start_urls = [
        "http://www.ford.com/",
    ]

    def parse(self, response):
        hxs = scrapy.Selector(response)
        # extract all links from page
        all_links = hxs.xpath('*//a/@href').extract()
        # iterate over links
        for link in all_links:
            yield scrapy.http.Request(url=link, callback=print_this_link)

    def print_this_link(self, link):
        print("Link --> {this_link}".format(this_link=link))