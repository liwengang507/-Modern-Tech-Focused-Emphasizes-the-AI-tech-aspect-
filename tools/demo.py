#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股金融数据系统演示脚本
展示系统的主要功能
"""

import os
import sys
from datetime import datetime

def print_banner():
    """打印系统横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        A股金融年报智能分析交互系统                            ║
    ║                                                              ║
    ║        功能演示脚本 v1.0.0                                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def demo_data_loading():
    """演示数据加载功能"""
    print("\n" + "="*60)
    print("📊 演示功能1: 数据加载")
    print("="*60)
    
    try:
        from data_loader import StockDataLoader
        
        print("1. 创建数据加载器...")
        loader = StockDataLoader(
            host='localhost',
            database='stock_analysis',
            user='root',
            password=''
        )
        
        print("2. 连接数据库...")
        if loader.connect():
            print("✅ 数据库连接成功")
            
            print("3. 获取数据统计...")
            stats = loader.get_data_summary()
            if stats:
                print("📈 数据统计信息:")
                for key, value in stats.items():
                    print(f"   - {key}: {value}")
            else:
                print("⚠️  数据库为空或无法获取统计信息")
            
            loader.disconnect()
        else:
            print("❌ 数据库连接失败")
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def demo_data_analysis():
    """演示数据分析功能"""
    print("\n" + "="*60)
    print("📈 演示功能2: 数据分析")
    print("="*60)
    
    try:
        from stock_analyzer import StockAnalyzer
        
        print("1. 创建数据分析器...")
        analyzer = StockAnalyzer(
            host='localhost',
            database='stock_analysis',
            user='root',
            password=''
        )
        
        print("2. 连接数据库...")
        if analyzer.connect():
            print("✅ 数据库连接成功")
            
            print("3. 获取股票列表...")
            stocks = analyzer.get_stock_list()
            if stocks is not None and not stocks.empty:
                print(f"📋 共找到 {len(stocks)} 只股票")
                print("前5只股票:")
                for _, row in stocks.head(5).iterrows():
                    print(f"   - {row['stock_code']}: {row['stock_name']}")
                
                # 分析第一只股票
                first_stock = stocks.iloc[0]['stock_code']
                print(f"\n4. 分析股票: {first_stock}")
                analysis = analyzer.analyze_stock_performance(first_stock)
                if analysis:
                    print("📊 股票分析结果:")
                    for key, value in analysis.items():
                        if key not in ['股票代码', '股票名称']:
                            print(f"   - {key}: {value}")
            else:
                print("⚠️  未找到股票数据")
            
            analyzer.disconnect()
        else:
            print("❌ 数据库连接失败")
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def demo_web_interface():
    """演示Web界面功能"""
    print("\n" + "="*60)
    print("🌐 演示功能3: Web界面")
    print("="*60)
    
    print("1. 检查Web界面组件...")
    
    # 检查Flask是否安装
    try:
        import flask
        print(f"✅ Flask版本: {flask.__version__}")
    except ImportError:
        print("❌ Flask未安装")
        return
    
    # 检查模板文件
    if os.path.exists('templates/index.html'):
        print("✅ HTML模板文件存在")
    else:
        print("⚠️  HTML模板文件不存在，Web界面可能无法正常工作")
    
    print("\n2. Web界面功能说明:")
    print("   - 股票列表浏览")
    print("   - 股票搜索功能")
    print("   - 表现最佳股票展示")
    print("   - 行业分析对比")
    print("   - 股票详情查看")
    print("   - 交互式图表展示")
    
    print("\n3. 启动Web服务器:")
    print("   python web_interface.py")
    print("   然后访问: http://localhost:5000")

def demo_data_visualization():
    """演示数据可视化功能"""
    print("\n" + "="*60)
    print("📊 演示功能4: 数据可视化")
    print("="*60)
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✅ 可视化库已安装")
        
        print("1. 支持的可视化功能:")
        print("   - 股票走势图")
        print("   - 行业对比图")
        print("   - 财务指标图表")
        print("   - 成交量分析图")
        print("   - 相关性热力图")
        
        print("\n2. 图表生成示例:")
        print("   - 运行 stock_analyzer.py 生成示例图表")
        print("   - 通过Web界面查看交互式图表")
        
    except ImportError as e:
        print(f"❌ 可视化库未安装: {e}")

def demo_system_overview():
    """演示系统概览"""
    print("\n" + "="*60)
    print("🔍 演示功能5: 系统概览")
    print("="*60)
    
    print("1. 系统架构:")
    print("   📥 数据获取层: BaoStock API")
    print("   💾 数据存储层: MySQL数据库")
    print("   🔧 业务逻辑层: Python分析模块")
    print("   🌐 数据展示层: Web界面")
    print("   📊 可视化层: Matplotlib/Seaborn")
    
    print("\n2. 主要文件:")
    files = [
        ("get_stock_data_baostock.py", "数据获取"),
        ("data_loader.py", "数据加载"),
        ("stock_analyzer.py", "数据分析"),
        ("web_interface.py", "Web界面"),
        ("config.py", "系统配置"),
        ("run_system.py", "启动脚本")
    ]
    
    for filename, description in files:
        if os.path.exists(filename):
            print(f"   ✅ {filename} - {description}")
        else:
            print(f"   ❌ {filename} - {description} (文件不存在)")
    
    print("\n3. 数据文件:")
    data_files = [
        "A股金融日线数据/完整A股金融日线数据_修复编码.csv",
        "A股金融日线数据/完整A股金融日线数据_20250920_221233.xlsx",
        "stock_daily_data.sql"
    ]
    
    for filename in data_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename) / (1024*1024)  # MB
            print(f"   ✅ {filename} ({size:.1f} MB)")
        else:
            print(f"   ❌ {filename} (文件不存在)")

def main():
    """主函数"""
    print_banner()
    
    print(f"🕒 演示开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行各个演示功能
    demo_system_overview()
    demo_data_loading()
    demo_data_analysis()
    demo_data_visualization()
    demo_web_interface()
    
    print("\n" + "="*60)
    print("🎉 演示完成!")
    print("="*60)
    print("\n📚 使用说明:")
    print("1. 首次使用请运行: python run_system.py")
    print("2. 获取新数据请运行: python get_stock_data_baostock.py")
    print("3. 启动Web界面请运行: python web_interface.py")
    print("4. 查看详细文档: README_系统使用说明.md")
    
    print(f"\n🕒 演示结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
