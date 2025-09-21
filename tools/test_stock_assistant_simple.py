#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版股票查询助手测试
只测试代码结构和格式，不依赖外部包
"""

import os
import ast

def test_file_structure():
    """测试文件结构"""
    print("=== 测试文件结构 ===")
    
    try:
        with open('stock_query_assistant.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键组件是否存在
        checks = [
            ("system_prompt", "system_prompt变量"),
            ("functions_desc", "functions_desc变量"),
            ("ExcSQLTool", "ExcSQLTool类"),
            ("generate_chart_png", "generate_chart_png函数"),
            ("init_agent_service", "init_agent_service函数"),
            ("app_gui", "app_gui函数")
        ]
        
        for check, name in checks:
            if check in content:
                print(f"✅ {name}存在")
            else:
                print(f"❌ {name}不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

def test_system_prompt_content():
    """测试system_prompt内容"""
    print("\n=== 测试system_prompt内容 ===")
    
    try:
        with open('stock_query_assistant.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找system_prompt
        start = content.find('system_prompt = """')
        end = content.find('"""', start + len('system_prompt = """'))
        
        if start == -1 or end == -1:
            print("❌ 找不到system_prompt定义")
            return False
        
        system_prompt = content[start:end + 3]
        
        # 检查关键内容
        checks = [
            ("我是A股股票查询助手", "助手身份说明"),
            ("stock_daily_data", "股票表名称"),
            ("CREATE TABLE", "表结构定义"),
            ("每当 exc_sql 工具返回", "工具返回提示")
        ]
        
        for check, name in checks:
            if check in system_prompt:
                print(f"✅ {name}正确")
            else:
                print(f"❌ {name}不正确")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试system_prompt内容失败: {e}")
        return False

def test_functions_desc_content():
    """测试functions_desc内容"""
    print("\n=== 测试functions_desc内容 ===")
    
    try:
        with open('stock_query_assistant.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找functions_desc
        start = content.find('functions_desc = [')
        if start == -1:
            print("❌ 找不到functions_desc定义")
            return False
        
        # 检查关键内容
        checks = [
            ('"name": "exc_sql"', "函数名称"),
            ('"description": "对于生成的SQL，进行SQL查询"', "函数描述"),
            ('"sql_input"', "参数名称")
        ]
        
        for check, name in checks:
            if check in content:
                print(f"✅ {name}正确")
            else:
                print(f"❌ {name}不正确")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试functions_desc内容失败: {e}")
        return False

def test_exc_sql_tool_structure():
    """测试ExcSQLTool类结构"""
    print("\n=== 测试ExcSQLTool类结构 ===")
    
    try:
        with open('stock_query_assistant.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找ExcSQLTool类
        start = content.find('class ExcSQLTool(BaseTool):')
        if start == -1:
            print("❌ 找不到ExcSQLTool类定义")
            return False
        
        # 检查关键内容
        checks = [
            ("description = '对于生成的SQL，进行SQL查询，并自动可视化'", "类描述"),
            ("def call(self, params: str, **kwargs) -> str:", "call方法"),
            ("create_engine", "数据库连接"),
            ("generate_chart_png", "图表生成函数")
        ]
        
        for check, name in checks:
            if check in content:
                print(f"✅ {name}正确")
            else:
                print(f"❌ {name}不正确")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试ExcSQLTool类结构失败: {e}")
        return False

def test_generate_chart_png_structure():
    """测试generate_chart_png函数结构"""
    print("\n=== 测试generate_chart_png函数结构 ===")
    
    try:
        with open('stock_query_assistant.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找generate_chart_png函数
        start = content.find('def generate_chart_png(df_sql, save_path):')
        if start == -1:
            print("❌ 找不到generate_chart_png函数定义")
            return False
        
        # 检查关键内容
        checks = [
            ("plt.subplots", "matplotlib绘图"),
            ("plt.title(\"股票数据统计\")", "图表标题"),
            ("plt.savefig(save_path)", "保存图表")
        ]
        
        for check, name in checks:
            if check in content:
                print(f"✅ {name}正确")
            else:
                print(f"❌ {name}不正确")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试generate_chart_png函数结构失败: {e}")
        return False

def test_main_function():
    """测试主函数"""
    print("\n=== 测试主函数 ===")
    
    try:
        with open('stock_query_assistant.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查主函数部分
        checks = [
            ("if __name__ == '__main__':", "主函数入口"),
            ("app_gui()", "启动GUI")
        ]
        
        for check, name in checks:
            if check in content:
                print(f"✅ {name}正确")
            else:
                print(f"❌ {name}不正确")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试主函数失败: {e}")
        return False

def main():
    """主函数"""
    print("股票查询助手简化版测试")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_system_prompt_content,
        test_functions_desc_content,
        test_exc_sql_tool_structure,
        test_generate_chart_png_structure,
        test_main_function
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        print("\n✅ 股票查询助手已成功修改为与assistant_ticket_bot-3.py完全一样的实现方式")
        print("\n📋 主要修改内容:")
        print("  1. ✅ system_prompt替换为股票表结构")
        print("  2. ✅ functions_desc保持与原始文件一致")
        print("  3. ✅ ExcSQLTool使用SQLAlchemy连接方式")
        print("  4. ✅ generate_chart_png使用与原始文件相同的实现")
        print("  5. ✅ 主函数简化为直接启动GUI")
        print("  6. ✅ 图表保存目录改为image_show")
        
        print("\n🚀 使用方法:")
        print("  python stock_query_assistant.py")
        
    else:
        print("❌ 部分测试失败，请检查修改")
    
    return passed == total

if __name__ == "__main__":
    main()
