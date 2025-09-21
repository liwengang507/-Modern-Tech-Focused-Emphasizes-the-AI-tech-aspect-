#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BaoStock配置文件
包含数据获取参数和其他设置
"""

# 数据获取参数
START_DATE = "2020-01-01"  # 开始日期
END_DATE = None  # 结束日期，None表示到今天

# 数据筛选参数
MAX_STOCKS = 1000  # 最大股票数量（避免请求过多）
STOCK_TYPES = ['1']  # 股票类型：1表示A股
STOCK_STATUS = ['1']  # 股票状态：1表示上市

# 文件输出配置
OUTPUT_FILENAME_PREFIX = "A股上市公司数据_BaoStock"
OUTPUT_DIRECTORY = "./data"  # 输出目录

# API请求配置
REQUEST_DELAY = 0.1  # 请求间隔（秒）
BATCH_SIZE = 100  # 批处理大小

# 数据字段配置
DAILY_FIELDS = [
    "date", "code", "open", "high", "low", "close", "preclose", 
    "volume", "amount", "adjustflag", "turn", "tradestatus", 
    "pctChg", "peTTM", "pbMRQ", "psTTM", "pcfNcfTTM", "isST"
]

# 财务数据年份
FINANCIAL_YEARS = [2020, 2021, 2022, 2023]

# 财务数据季度
FINANCIAL_QUARTERS = [4]  # 只获取年报数据（第4季度）
