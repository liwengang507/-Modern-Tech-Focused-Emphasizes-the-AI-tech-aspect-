#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股金融年报ChatBI系统 - 主入口文件
====================================

这是一个基于qwen-agent框架的A股股票查询分析助手系统，提供：
- SQL查询和数据可视化
- 热点新闻搜索 (Tavily)
- ARIMA价格预测
- 布林带异常点检测
- Prophet周期性分析

作者: liwengang
版本: 1.0.0
"""

import sys
import os

# 添加核心模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

def main():
    """主函数 - 启动股票查询助手"""
    try:
        # 导入核心股票查询助手
        from stock_query_assistant import app_gui as run_assistant
        
        print("=" * 60)
        print("🚀 A股金融年报ChatBI系统")
        print("=" * 60)
        print("📊 功能包括:")
        print("  1. SQL查询和数据可视化")
        print("  2. 热点新闻搜索 (Tavily)")
        print("  3. ARIMA价格预测")
        print("  4. 布林带异常点检测")
        print("  5. Prophet周期性分析")
        print("=" * 60)
        print("🌐 正在启动Web界面...")
        print()
        
        # 启动股票查询助手
        run_assistant()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖包已正确安装")
        print("运行: pip install -r docs/requirements_stock_assistant.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
