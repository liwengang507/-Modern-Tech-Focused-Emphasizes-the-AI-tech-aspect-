#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股金融数据分析器
提供股票数据的基本统计分析功能
"""

import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class StockAnalyzer:
    """A股金融数据分析器"""
    
    def __init__(self, host='localhost', database='stock_analysis', user='root', password=''):
        """
        初始化数据分析器
        
        Args:
            host (str): MySQL主机地址
            database (str): 数据库名称
            user (str): 用户名
            password (str): 密码
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                use_unicode=True
            )
            
            if self.connection.is_connected():
                print(f"✅ 成功连接到MySQL数据库: {self.database}")
                return True
                
        except Error as e:
            print(f"❌ 连接MySQL数据库失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ 已断开MySQL数据库连接")
    
    def get_stock_list(self):
        """获取股票列表"""
        if not self.connection:
            return None
            
        try:
            query = """
                SELECT DISTINCT stock_code, stock_name, industry_name
                FROM stock_daily_data 
                WHERE stock_name IS NOT NULL
                ORDER BY stock_code
            """
            
            df = pd.read_sql(query, self.connection)
            return df
            
        except Error as e:
            print(f"❌ 获取股票列表失败: {e}")
            return None
    
    def get_stock_data(self, stock_code, start_date=None, end_date=None):
        """
        获取指定股票的数据
        
        Args:
            stock_code (str): 股票代码
            start_date (str): 开始日期，格式：YYYY-MM-DD
            end_date (str): 结束日期，格式：YYYY-MM-DD
        """
        if not self.connection:
            return None
            
        try:
            query = """
                SELECT * FROM stock_daily_data 
                WHERE stock_code = %s
            """
            params = [stock_code]
            
            if start_date:
                query += " AND trade_date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND trade_date <= %s"
                params.append(end_date)
            
            query += " ORDER BY trade_date"
            
            df = pd.read_sql(query, self.connection, params=params)
            return df
            
        except Error as e:
            print(f"❌ 获取股票数据失败: {e}")
            return None
    
    def analyze_stock_performance(self, stock_code):
        """分析股票表现"""
        df = self.get_stock_data(stock_code)
        if df is None or df.empty:
            return None
        
        # 基本统计信息
        analysis = {
            '股票代码': stock_code,
            '股票名称': df['stock_name'].iloc[0] if not df.empty else '',
            '数据期间': f"{df['trade_date'].min()} 至 {df['trade_date'].max()}",
            '交易天数': len(df),
            '当前价格': df['close_price'].iloc[-1] if not df.empty else 0,
            '最高价': df['high_price'].max(),
            '最低价': df['low_price'].min(),
            '平均价格': df['close_price'].mean(),
            '价格标准差': df['close_price'].std(),
            '总成交量': df['volume'].sum(),
            '平均成交量': df['volume'].mean(),
            '最大单日涨幅': df['pct_change'].max(),
            '最大单日跌幅': df['pct_change'].min(),
            '平均涨跌幅': df['pct_change'].mean(),
            '上涨天数': len(df[df['pct_change'] > 0]),
            '下跌天数': len(df[df['pct_change'] < 0]),
            '平盘天数': len(df[df['pct_change'] == 0])
        }
        
        return analysis
    
    def get_top_performers(self, limit=10, order_by='pct_change'):
        """获取表现最好的股票"""
        if not self.connection:
            return None
            
        try:
            query = f"""
                SELECT stock_code, stock_name, 
                       AVG(pct_change) as avg_change,
                       MAX(pct_change) as max_change,
                       MIN(pct_change) as min_change,
                       COUNT(*) as trade_days,
                       AVG(close_price) as avg_price
                FROM stock_daily_data 
                WHERE pct_change IS NOT NULL
                GROUP BY stock_code, stock_name
                HAVING trade_days >= 30
                ORDER BY {order_by} DESC
                LIMIT %s
            """
            
            df = pd.read_sql(query, self.connection, params=[limit])
            return df
            
        except Error as e:
            print(f"❌ 获取表现最佳股票失败: {e}")
            return None
    
    def get_industry_analysis(self):
        """获取行业分析"""
        if not self.connection:
            return None
            
        try:
            query = """
                SELECT industry_name,
                       COUNT(DISTINCT stock_code) as stock_count,
                       AVG(pct_change) as avg_change,
                       AVG(pe_ttm) as avg_pe,
                       AVG(pb_ratio) as avg_pb,
                       SUM(volume) as total_volume
                FROM stock_daily_data 
                WHERE industry_name IS NOT NULL 
                  AND industry_name != 'nan'
                  AND pct_change IS NOT NULL
                GROUP BY industry_name
                HAVING stock_count >= 5
                ORDER BY stock_count DESC
            """
            
            df = pd.read_sql(query, self.connection)
            return df
            
        except Error as e:
            print(f"❌ 获取行业分析失败: {e}")
            return None
    
    def plot_stock_trend(self, stock_code, save_path=None):
        """绘制股票走势图"""
        df = self.get_stock_data(stock_code)
        if df is None or df.empty:
            return False
        
        plt.figure(figsize=(12, 8))
        
        # 绘制价格走势
        plt.subplot(2, 1, 1)
        plt.plot(df['trade_date'], df['close_price'], label='收盘价', linewidth=1)
        plt.title(f'{stock_code} 股票走势图', fontsize=14, fontweight='bold')
        plt.ylabel('价格 (元)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 绘制成交量
        plt.subplot(2, 1, 2)
        plt.bar(df['trade_date'], df['volume'], alpha=0.7, color='orange')
        plt.title('成交量', fontsize=12)
        plt.ylabel('成交量', fontsize=12)
        plt.xlabel('日期', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 图表已保存到: {save_path}")
        else:
            plt.show()
        
        return True
    
    def plot_industry_comparison(self, save_path=None):
        """绘制行业对比图"""
        df = self.get_industry_analysis()
        if df is None or df.empty:
            return False
        
        # 取前10个行业
        top_industries = df.head(10)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 股票数量对比
        axes[0, 0].barh(top_industries['industry_name'], top_industries['stock_count'])
        axes[0, 0].set_title('各行业股票数量', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('股票数量')
        
        # 平均涨跌幅对比
        axes[0, 1].barh(top_industries['industry_name'], top_industries['avg_change'])
        axes[0, 1].set_title('各行业平均涨跌幅', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('平均涨跌幅 (%)')
        
        # 平均市盈率对比
        valid_pe = top_industries.dropna(subset=['avg_pe'])
        if not valid_pe.empty:
            axes[1, 0].barh(valid_pe['industry_name'], valid_pe['avg_pe'])
            axes[1, 0].set_title('各行业平均市盈率', fontsize=12, fontweight='bold')
            axes[1, 0].set_xlabel('平均市盈率')
        
        # 总成交量对比
        axes[1, 1].barh(top_industries['industry_name'], top_industries['total_volume'])
        axes[1, 1].set_title('各行业总成交量', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('总成交量')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 行业对比图已保存到: {save_path}")
        else:
            plt.show()
        
        return True
    
    def generate_report(self, stock_code=None):
        """生成分析报告"""
        print("=" * 60)
        print("A股金融数据分析报告")
        print("=" * 60)
        
        if stock_code:
            # 单个股票分析
            analysis = self.analyze_stock_performance(stock_code)
            if analysis:
                print(f"\n📊 股票分析: {analysis['股票代码']} - {analysis['股票名称']}")
                print("-" * 40)
                for key, value in analysis.items():
                    if key not in ['股票代码', '股票名称']:
                        print(f"{key}: {value}")
        
        # 行业分析
        industry_df = self.get_industry_analysis()
        if industry_df is not None and not industry_df.empty:
            print(f"\n🏭 行业分析 (前5个行业)")
            print("-" * 40)
            top_5 = industry_df.head(5)
            for _, row in top_5.iterrows():
                print(f"{row['industry_name']}: {row['stock_count']}只股票, 平均涨跌幅: {row['avg_change']:.2f}%")
        
        # 表现最佳股票
        top_stocks = self.get_top_performers(5)
        if top_stocks is not None and not top_stocks.empty:
            print(f"\n📈 表现最佳股票 (前5名)")
            print("-" * 40)
            for _, row in top_stocks.iterrows():
                print(f"{row['stock_code']} - {row['stock_name']}: 平均涨跌幅 {row['avg_change']:.2f}%")

def main():
    """主函数"""
    print("A股金融数据分析器")
    print("=" * 50)
    
    # 创建分析器实例
    analyzer = StockAnalyzer(
        host='localhost',
        database='stock_analysis',
        user='root',
        password=''  # 请根据实际情况修改密码
    )
    
    try:
        # 连接到数据库
        if not analyzer.connect():
            print("❌ 无法连接到数据库，请检查配置")
            return
        
        # 生成分析报告
        analyzer.generate_report()
        
        # 获取股票列表
        stock_list = analyzer.get_stock_list()
        if stock_list is not None and not stock_list.empty:
            print(f"\n📋 股票列表 (前10只)")
            print("-" * 40)
            for _, row in stock_list.head(10).iterrows():
                print(f"{row['stock_code']} - {row['stock_name']} ({row['industry_name']})")
            
            # 分析第一只股票
            first_stock = stock_list.iloc[0]['stock_code']
            print(f"\n🔍 分析股票: {first_stock}")
            analysis = analyzer.analyze_stock_performance(first_stock)
            if analysis:
                for key, value in analysis.items():
                    print(f"{key}: {value}")
            
            # 生成图表
            print(f"\n📊 生成图表...")
            analyzer.plot_stock_trend(first_stock, f"stock_trend_{first_stock}.png")
            analyzer.plot_industry_comparison("industry_comparison.png")
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    finally:
        analyzer.disconnect()

if __name__ == "__main__":
    main()
