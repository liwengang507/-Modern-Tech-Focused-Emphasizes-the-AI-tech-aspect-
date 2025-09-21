#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
管理数据库连接和其他系统设置
"""

import os
from datetime import datetime

class Config:
    """系统配置类"""
    
    # 数据库配置
    DATABASE_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'stock_analysis'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': int(os.getenv('DB_PORT', 3306)),
        'charset': 'utf8mb4'
    }
    
    # Web服务器配置
    WEB_CONFIG = {
        'host': os.getenv('WEB_HOST', '0.0.0.0'),
        'port': int(os.getenv('WEB_PORT', 5000)),
        'debug': os.getenv('WEB_DEBUG', 'True').lower() == 'true'
    }
    
    # 数据文件路径配置
    DATA_PATHS = {
        'csv_file': 'A股金融日线数据/完整A股金融日线数据_修复编码.csv',
        'excel_file': 'A股金融日线数据/完整A股金融日线数据_20250920_221233.xlsx',
        'sql_file': 'stock_daily_data.sql',
        'output_dir': 'output',
        'charts_dir': 'charts'
    }
    
    # BaoStock配置
    BAOSTOCK_CONFIG = {
        'start_date': '2020-01-01',
        'end_date': datetime.now().strftime('%Y-%m-%d'),
        'max_stocks': 1000,
        'request_delay': 0.1  # 请求间隔（秒）
    }
    
    # 分析配置
    ANALYSIS_CONFIG = {
        'top_performers_limit': 20,
        'industry_min_stocks': 5,
        'chart_dpi': 300,
        'chart_figsize': (12, 8)
    }
    
    # 日志配置
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'logs/system.log'
    }
    
    @classmethod
    def get_database_url(cls):
        """获取数据库连接URL"""
        config = cls.DATABASE_CONFIG
        return f"mysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    
    @classmethod
    def create_directories(cls):
        """创建必要的目录"""
        directories = [
            cls.DATA_PATHS['output_dir'],
            cls.DATA_PATHS['charts_dir'],
            'logs',
            'templates',
            'static'
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✅ 创建目录: {directory}")

# 开发环境配置
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    DATABASE_CONFIG = {
        **Config.DATABASE_CONFIG,
        'database': 'stock_analysis_dev'
    }

# 生产环境配置
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    DATABASE_CONFIG = {
        **Config.DATABASE_CONFIG,
        'database': 'stock_analysis_prod'
    }

# 测试环境配置
class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    DATABASE_CONFIG = {
        **Config.DATABASE_CONFIG,
        'database': 'stock_analysis_test'
    }

# 根据环境变量选择配置
def get_config():
    """根据环境变量获取配置"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()

# 默认配置
config = get_config()
