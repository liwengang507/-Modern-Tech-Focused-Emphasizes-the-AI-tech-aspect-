#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股金融年报智能分析交互系统启动脚本
"""

import os
import sys
import subprocess
import time
from config import config

def check_dependencies():
    """检查依赖包是否已安装"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'baostock', 'pandas', 'numpy', 'openpyxl', 
        'mysql-connector-python', 'flask', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装依赖包:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_mysql():
    """检查MySQL是否可用"""
    print("\n🔍 检查MySQL连接...")
    
    try:
        import mysql.connector
        connection = mysql.connector.connect(**config.DATABASE_CONFIG)
        if connection.is_connected():
            print("✅ MySQL连接成功")
            connection.close()
            return True
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        print("请确保MySQL服务正在运行，并检查数据库配置")
        return False

def setup_database():
    """设置数据库"""
    print("\n🔧 设置数据库...")
    
    try:
        from data_loader import StockDataLoader
        
        loader = StockDataLoader(
            host=config.DATABASE_CONFIG['host'],
            database=config.DATABASE_CONFIG['database'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password']
        )
        
        # 创建数据库
        loader.create_database()
        
        # 连接数据库
        if not loader.connect():
            print("❌ 无法连接到数据库")
            return False
        
        # 创建数据表
        if not loader.create_table():
            print("❌ 创建数据表失败")
            return False
        
        # 检查是否有数据
        stats = loader.get_data_summary()
        if stats and stats.get('总记录数', 0) > 0:
            print(f"✅ 数据库已存在数据: {stats['总记录数']} 条记录")
        else:
            print("⚠️  数据库为空，建议运行数据加载程序")
        
        loader.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ 数据库设置失败: {e}")
        return False

def load_data():
    """加载数据"""
    print("\n📊 加载数据...")
    
    csv_file = config.DATA_PATHS['csv_file']
    if not os.path.exists(csv_file):
        print(f"❌ CSV文件不存在: {csv_file}")
        print("请先运行数据获取程序")
        return False
    
    try:
        from data_loader import StockDataLoader
        
        loader = StockDataLoader(
            host=config.DATABASE_CONFIG['host'],
            database=config.DATABASE_CONFIG['database'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password']
        )
        
        if not loader.connect():
            print("❌ 无法连接到数据库")
            return False
        
        if loader.load_csv_data(csv_file):
            print("✅ 数据加载成功")
            loader.disconnect()
            return True
        else:
            print("❌ 数据加载失败")
            loader.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return False

def start_web_server():
    """启动Web服务器"""
    print("\n🌐 启动Web服务器...")
    
    try:
        from web_interface import main as start_web
        print("✅ Web服务器启动成功")
        print(f"📱 访问地址: http://localhost:{config.WEB_CONFIG['port']}")
        start_web()
    except Exception as e:
        print(f"❌ Web服务器启动失败: {e}")
        return False

def show_menu():
    """显示主菜单"""
    print("\n" + "="*60)
    print("A股金融年报智能分析交互系统")
    print("="*60)
    print("1. 检查系统环境")
    print("2. 设置数据库")
    print("3. 加载数据")
    print("4. 启动Web界面")
    print("5. 运行数据分析")
    print("6. 获取新数据")
    print("0. 退出")
    print("="*60)

def run_data_analysis():
    """运行数据分析"""
    print("\n📈 运行数据分析...")
    
    try:
        from stock_analyzer import main as run_analysis
        run_analysis()
    except Exception as e:
        print(f"❌ 数据分析失败: {e}")

def get_new_data():
    """获取新数据"""
    print("\n📊 获取新数据...")
    
    try:
        from get_stock_data_baostock import main as get_data
        get_data()
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")

def main():
    """主函数"""
    print("🚀 启动A股金融年报智能分析交互系统")
    
    # 创建必要目录
    config.create_directories()
    
    while True:
        show_menu()
        
        try:
            choice = input("\n请选择操作 (0-6): ").strip()
            
            if choice == '0':
                print("👋 感谢使用，再见！")
                break
            elif choice == '1':
                if check_dependencies() and check_mysql():
                    print("✅ 系统环境检查完成")
                else:
                    print("❌ 系统环境检查失败")
            elif choice == '2':
                setup_database()
            elif choice == '3':
                load_data()
            elif choice == '4':
                start_web_server()
            elif choice == '5':
                run_data_analysis()
            elif choice == '6':
                get_new_data()
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()
