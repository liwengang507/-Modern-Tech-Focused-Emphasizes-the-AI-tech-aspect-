#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票查询助手测试脚本
"""

import os
import mysql.connector
from mysql.connector import Error
import pandas as pd

def test_database_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            database='lwg_database',
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        if connection.is_connected():
            print("✅ 数据库连接成功")
            
            # 测试查询
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM stock_daily_data")
            count = cursor.fetchone()[0]
            print(f"✅ 数据表记录数: {count}")
            
            # 测试基本查询
            cursor.execute("SELECT stock_code, stock_name FROM stock_daily_data LIMIT 5")
            results = cursor.fetchall()
            print("✅ 前5只股票:")
            for row in results:
                print(f"   {row[0]} - {row[1]}")
            
            cursor.close()
            connection.close()
            return True
        else:
            print("❌ 数据库连接失败")
            return False
            
    except Error as e:
        print(f"❌ 数据库连接错误: {e}")
        return False

def test_sample_queries():
    """测试示例查询"""
    print("\n=== 测试示例查询 ===")
    
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            database='lwg_database',
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        # 示例查询1: 股票基本信息
        print("1. 股票基本信息查询:")
        df1 = pd.read_sql("""
            SELECT stock_code, stock_name, industry_name, close_price, pct_change 
            FROM stock_daily_data 
            WHERE trade_date = (SELECT MAX(trade_date) FROM stock_daily_data)
            LIMIT 10
        """, connection)
        print(df1.to_string(index=False))
        
        # 示例查询2: 行业分析
        print("\n2. 行业分析:")
        df2 = pd.read_sql("""
            SELECT industry_name, COUNT(DISTINCT stock_code) as stock_count,
                   AVG(close_price) as avg_price, AVG(pct_change) as avg_change
            FROM stock_daily_data 
            WHERE trade_date = (SELECT MAX(trade_date) FROM stock_daily_data)
            AND industry_name IS NOT NULL
            GROUP BY industry_name
            ORDER BY stock_count DESC
            LIMIT 10
        """, connection)
        print(df2.to_string(index=False))
        
        # 示例查询3: 涨跌幅排行
        print("\n3. 涨跌幅排行:")
        df3 = pd.read_sql("""
            SELECT stock_code, stock_name, close_price, pct_change
            FROM stock_daily_data 
            WHERE trade_date = (SELECT MAX(trade_date) FROM stock_daily_data)
            ORDER BY pct_change DESC
            LIMIT 10
        """, connection)
        print(df3.to_string(index=False))
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 查询测试失败: {e}")
        return False

def main():
    """主函数"""
    print("A股股票查询助手测试")
    print("=" * 50)
    
    # 测试数据库连接
    if not test_database_connection():
        print("数据库连接失败，请检查配置")
        return
    
    # 测试示例查询
    if not test_sample_queries():
        print("查询测试失败")
        return
    
    print("\n✅ 所有测试通过！")
    print("\n使用方法:")
    print("1. 终端模式: python stock_query_assistant.py tui")
    print("2. Web界面: python stock_query_assistant.py gui")

if __name__ == "__main__":
    main()
