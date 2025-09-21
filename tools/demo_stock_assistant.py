#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票查询助手演示脚本
展示主要功能和使用方法
"""

import os
import sys

def print_banner():
    """打印系统横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              A股股票查询助手 v1.0.0                          ║
    ║                                                              ║
    ║              基于qwen-agent的智能股票查询系统                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_features():
    """展示功能特点"""
    print("\n🚀 功能特点:")
    print("=" * 60)
    
    features = [
        ("🔍 智能查询", "支持自然语言股票查询，自动生成SQL语句"),
        ("📊 数据可视化", "自动生成多种类型的股票数据图表"),
        ("💬 多种交互", "Web界面和终端命令行两种交互方式"),
        ("📈 实时分析", "支持股价走势、行业对比、财务指标分析"),
        ("🎯 精准筛选", "支持复杂的股票筛选和排序条件"),
        ("📋 数据统计", "提供全面的股票数据统计和分析")
    ]
    
    for feature, description in features:
        print(f"  {feature:<12} {description}")
    
    print("\n📊 支持的图表类型:")
    chart_types = [
        "📈 股价走势图 - 时间序列数据可视化",
        "📊 股票对比图 - 多股票数据对比",
        "🏭 行业分析图 - 行业数据统计对比",
        "📉 涨跌幅图 - 涨跌幅分析和排序",
        "📋 通用柱状图 - 其他统计数据展示"
    ]
    
    for chart_type in chart_types:
        print(f"    {chart_type}")

def show_examples():
    """展示查询示例"""
    print("\n💡 查询示例:")
    print("=" * 60)
    
    examples = [
        ("基本信息查询", [
            "查询招商银行(600036)的基本信息",
            "显示平安银行的股票数据",
            "查看万科A的财务指标"
        ]),
        ("价格走势分析", [
            "查看招商银行最近30天的股价走势",
            "分析平安银行在2024年的价格变化",
            "显示万科A的股价波动情况"
        ]),
        ("行业对比分析", [
            "银行业股票的平均市盈率对比",
            "各行业股票数量统计",
            "显示房地产行业的平均市值"
        ]),
        ("财务指标分析", [
            "查询净利润最高的10只股票",
            "显示ROE排名前20的股票",
            "找出总资产超过1000亿的股票"
        ]),
        ("交易数据统计", [
            "今日成交量最大的股票",
            "涨跌幅排行榜",
            "换手率最高的股票"
        ]),
        ("股票筛选排序", [
            "筛选市盈率在10-20之间的股票",
            "找出市值最大的50只股票",
            "查询ST股票列表"
        ])
    ]
    
    for category, queries in examples:
        print(f"\n  📋 {category}:")
        for i, query in enumerate(queries, 1):
            print(f"    {i}. {query}")

def show_usage():
    """展示使用方法"""
    print("\n🔧 使用方法:")
    print("=" * 60)
    
    print("1. 安装依赖包:")
    print("   pip install -r requirements_stock_assistant.txt")
    
    print("\n2. 配置API Key:")
    print("   export DASHSCOPE_API_KEY='your_api_key_here'")
    
    print("\n3. 测试系统:")
    print("   python test_stock_assistant.py")
    
    print("\n4. 启动助手:")
    print("   终端模式: python stock_query_assistant.py tui")
    print("   Web界面: python stock_query_assistant.py gui")
    
    print("\n5. 访问Web界面:")
    print("   http://localhost:7860")

def show_database_info():
    """展示数据库信息"""
    print("\n💾 数据库信息:")
    print("=" * 60)
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
        connection = mysql.connector.connect(
            host='127.0.0.1',
            database='lwg_database',
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 获取基本统计信息
            cursor.execute("SELECT COUNT(*) FROM stock_daily_data")
            total_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT stock_code) FROM stock_daily_data")
            total_stocks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT industry_name) FROM stock_daily_data WHERE industry_name IS NOT NULL")
            total_industries = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(trade_date), MAX(trade_date) FROM stock_daily_data")
            date_range = cursor.fetchone()
            
            print(f"  📊 数据统计:")
            print(f"    总记录数: {total_records:,}")
            print(f"    股票数量: {total_stocks}")
            print(f"    行业数量: {total_industries}")
            print(f"    数据期间: {date_range[0]} 至 {date_range[1]}")
            
            # 显示部分股票信息
            cursor.execute("""
                SELECT stock_code, stock_name, industry_name 
                FROM stock_daily_data 
                WHERE trade_date = (SELECT MAX(trade_date) FROM stock_daily_data)
                AND industry_name IS NOT NULL
                LIMIT 5
            """)
            stocks = cursor.fetchall()
            
            print(f"\n  📋 股票示例:")
            for stock in stocks:
                print(f"    {stock[0]} - {stock[1]} ({stock[2]})")
            
            cursor.close()
            connection.close()
            
        else:
            print("  ❌ 数据库连接失败")
            
    except Exception as e:
        print(f"  ❌ 数据库信息获取失败: {e}")

def main():
    """主函数"""
    print_banner()
    
    show_features()
    show_examples()
    show_usage()
    show_database_info()
    
    print("\n" + "=" * 60)
    print("🎉 股票查询助手准备就绪！")
    print("=" * 60)
    
    print("\n📞 技术支持:")
    print("  - 查看详细文档: README_股票查询助手.md")
    print("  - 运行测试脚本: python test_stock_assistant.py")
    print("  - 启动助手: python stock_query_assistant.py")
    
    print(f"\n🕒 演示完成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
