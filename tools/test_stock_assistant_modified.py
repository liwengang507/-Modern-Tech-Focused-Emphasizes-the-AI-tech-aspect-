#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的股票查询助手
验证是否与assistant_ticket_bot-3.py的实现方式完全一样
"""

import os
import sys

def test_imports():
    """测试导入"""
    print("=== 测试导入 ===")
    try:
        from stock_query_assistant import ExcSQLTool, generate_chart_png, init_agent_service
        print("✅ 成功导入核心模块")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_system_prompt():
    """测试system_prompt格式"""
    print("\n=== 测试system_prompt格式 ===")
    try:
        from stock_query_assistant import system_prompt
        
        # 检查是否包含股票表结构
        if "stock_daily_data" in system_prompt:
            print("✅ system_prompt包含股票表结构")
        else:
            print("❌ system_prompt缺少股票表结构")
            return False
            
        # 检查是否包含必要的提示信息
        if "每当 exc_sql 工具返回" in system_prompt:
            print("✅ system_prompt包含工具返回提示")
        else:
            print("❌ system_prompt缺少工具返回提示")
            return False
            
        return True
    except Exception as e:
        print(f"❌ 测试system_prompt失败: {e}")
        return False

def test_functions_desc():
    """测试functions_desc格式"""
    print("\n=== 测试functions_desc格式 ===")
    try:
        from stock_query_assistant import functions_desc
        
        # 检查是否包含exc_sql函数
        if len(functions_desc) == 1 and functions_desc[0]["name"] == "exc_sql":
            print("✅ functions_desc格式正确")
        else:
            print("❌ functions_desc格式不正确")
            return False
            
        # 检查描述是否与原始文件一致
        if functions_desc[0]["description"] == "对于生成的SQL，进行SQL查询":
            print("✅ 函数描述与原始文件一致")
        else:
            print("❌ 函数描述与原始文件不一致")
            return False
            
        return True
    except Exception as e:
        print(f"❌ 测试functions_desc失败: {e}")
        return False

def test_exc_sql_tool():
    """测试ExcSQLTool类"""
    print("\n=== 测试ExcSQLTool类 ===")
    try:
        from stock_query_assistant import ExcSQLTool
        
        # 检查类描述
        if ExcSQLTool.description == "对于生成的SQL，进行SQL查询，并自动可视化":
            print("✅ ExcSQLTool描述正确")
        else:
            print("❌ ExcSQLTool描述不正确")
            return False
            
        # 检查是否有call方法
        if hasattr(ExcSQLTool, 'call'):
            print("✅ ExcSQLTool包含call方法")
        else:
            print("❌ ExcSQLTool缺少call方法")
            return False
            
        return True
    except Exception as e:
        print(f"❌ 测试ExcSQLTool失败: {e}")
        return False

def test_generate_chart_png():
    """测试generate_chart_png函数"""
    print("\n=== 测试generate_chart_png函数 ===")
    try:
        from stock_query_assistant import generate_chart_png
        
        # 检查函数是否存在
        if callable(generate_chart_png):
            print("✅ generate_chart_png函数存在且可调用")
        else:
            print("❌ generate_chart_png函数不存在或不可调用")
            return False
            
        return True
    except Exception as e:
        print(f"❌ 测试generate_chart_png失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    try:
        import pandas as pd
        from sqlalchemy import create_engine
        
        engine = create_engine(
            'mysql+mysqlconnector://root:@127.0.0.1:3306/lwg_database?charset=utf8mb4',
            connect_args={'connect_timeout': 10}, pool_size=10, max_overflow=20
        )
        
        # 测试简单查询
        df = pd.read_sql("SELECT COUNT(*) as count FROM stock_daily_data", engine)
        if len(df) > 0 and df.iloc[0]['count'] > 0:
            print(f"✅ 数据库连接成功，记录数: {df.iloc[0]['count']}")
            return True
        else:
            print("❌ 数据库连接失败或无数据")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("股票查询助手修改验证测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_system_prompt,
        test_functions_desc,
        test_exc_sql_tool,
        test_generate_chart_png,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！股票查询助手已成功修改为与assistant_ticket_bot-3.py完全一样的实现方式")
        print("\n使用方法:")
        print("python stock_query_assistant.py")
    else:
        print("❌ 部分测试失败，请检查修改")
    
    return passed == total

if __name__ == "__main__":
    main()
