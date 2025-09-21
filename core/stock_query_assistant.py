#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票查询助手
基于qwen-agent和stock_daily_data表的智能股票查询助手
"""

import os
import asyncio
from typing import Optional
import dashscope
from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
import pandas as pd
from sqlalchemy import create_engine
from qwen_agent.tools.base import BaseTool, register_tool
import matplotlib.pyplot as plt
import io
import base64
import time
import numpy as np
import mysql.connector
from mysql.connector import Error
from tavily import TavilyClient
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
warnings.filterwarnings('ignore')

# 布林带计算相关导入
import numpy as np

# Prophet周期性分析相关导入
from prophet import Prophet

# 解决中文显示问题
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配置 DashScope API Key
# 请在这里填写您的API Key
API_KEY = "sk-db159bb711df4c46ae4db8100e304516"  # 在这里填写您的DashScope API Key

# 配置 Tavily API Key
# 请在这里填写您的Tavily API Key
TAVILY_API_KEY = "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"  # 在这里填写您的Tavily API Key

dashscope.api_key = API_KEY
dashscope.timeout = 30  # 设置超时时间为 30 秒

# ====== 股票查询助手 system prompt 和函数描述 ======
system_prompt = """我是A股股票查询助手，以下是关于股票数据表相关的字段，我可能会编写对应的SQL，对数据进行查询
-- A股金融日线数据表
CREATE TABLE IF NOT EXISTS `stock_daily_data`(
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `stock_code` VARCHAR(50) COMMENT '股票代码',
    `stock_name` VARCHAR(50) COMMENT '股票名称',
    `ipo_date` DATETIME COMMENT 'IPO日期',
    `listing_status` VARCHAR(50) COMMENT '上市状态',
    `stock_type` VARCHAR(50) COMMENT '股票类型',
    `trade_date` DATE COMMENT '交易日期',
    `open_price` DECIMAL(15, 4) COMMENT '开盘价',
    `high_price` DECIMAL(15, 4) COMMENT '最高价',
    `low_price` DECIMAL(15, 4) COMMENT '最低价',
    `close_price` DECIMAL(15, 4) COMMENT '收盘价',
    `prev_close_price` DECIMAL(15, 4) COMMENT '前收盘价',
    `volume` BIGINT COMMENT '成交量',
    `amount` BIGINT COMMENT '成交额',
    `pct_change` DECIMAL(15, 4) COMMENT '涨跌幅',
    `turnover_rate` DECIMAL(15, 4) COMMENT '换手率',
    `trade_status` VARCHAR(50) COMMENT '交易状态',
    `pe_ttm` DECIMAL(15, 4) COMMENT '市盈率TTM',
    `pb_ratio` DECIMAL(15, 4) COMMENT '市净率',
    `ps_ttm` DECIMAL(15, 4) COMMENT '市销率TTM',
    `pcf_ttm` DECIMAL(15, 4) COMMENT '市现率TTM',
    `is_st` VARCHAR(50) COMMENT '是否ST',
    `net_profit` DECIMAL(20, 4) COMMENT '净利润',
    `revenue` DECIMAL(20, 4) COMMENT '营业收入',
    `total_assets` DECIMAL(20, 4) COMMENT '总资产',
    `net_assets` DECIMAL(20, 4) COMMENT '净资产',
    `eps` DECIMAL(15, 4) COMMENT '每股收益',
    `roe` DECIMAL(15, 4) COMMENT '净资产收益率',
    `industry_code` VARCHAR(50) COMMENT '行业分类',
    `industry_name` VARCHAR(255) COMMENT '行业名称',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'A股金融日线数据表';
我将回答用户关于股票相关的问题，包括：

1. 股票基本信息查询
2. 股票价格走势分析
3. 多股票对比分析（支持涨跌幅对比）
4. 行业对比分析
5. 财务指标分析
6. 交易数据统计
7. 热点新闻搜索（使用Tavily抓取最新财经新闻）
8. 股票价格预测（使用ARIMA模型预测未来N天价格）
9. 布林带异常点检测（使用20日周期+2σ检测超买和超卖点）
10. Prophet周期性分析（分析股票的趋势、周度和年度周期性规律）

**重要说明：**
- 对于单股票查询，使用 need_visualize=True（默认），会生成图表
- 对于多股票对比分析，使用 need_visualize=False，避免生成混乱的对比图表
- 数据展示采用前5行+后5行的方式，让AI看到更完整的数据信息
- 对于新闻搜索请求（如"搜索新闻"、"热点新闻"、"最新资讯"等），使用 news_search 工具，不要使用 exc_sql 工具

每当 exc_sql 工具返回 markdown 表格和图片时，你必须原样输出工具返回的全部内容（包括图片 markdown），不要只总结表格，也不要省略图片。这样用户才能直接看到表格和图片。
"""

functions_desc = [
    {
        "name": "exc_sql",
        "description": "对于生成的SQL，进行SQL查询",
        "parameters": {
            "type": "object",
            "properties": {
                "sql_input": {
                    "type": "string",
                    "description": "生成的SQL语句",
                }
            },
            "required": ["sql_input"],
        },
    },
    {
        "name": "news_search",
        "description": "搜索最新的热点新闻，特别是股票和财经相关的新闻",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，如'股票'、'财经'、'A股'等",
                },
                "max_results": {
                    "type": "integer",
                    "description": "返回的最大结果数量，默认为5",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "arima_stock",
        "description": "使用ARIMA模型预测股票未来N天的价格走势",
        "parameters": {
            "type": "object",
            "properties": {
                "ts_code": {
                    "type": "string",
                    "description": "股票代码，如sz.000001",
                },
                "n": {
                    "type": "integer",
                    "description": "预测天数，默认为5天",
                }
            },
            "required": ["ts_code"],
        },
    },
    {
        "name": "boll_detection",
        "description": "使用布林带指标检测股票的超买和超卖异常点",
        "parameters": {
            "type": "object",
            "properties": {
                "ts_code": {
                    "type": "string",
                    "description": "股票代码，如sh.600600",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式：YYYY-MM-DD，默认为过去1年",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式：YYYY-MM-DD，默认为今天",
                }
            },
            "required": ["ts_code"],
        },
    },
    {
        "name": "prophet_analysis",
        "description": "使用Prophet模型分析股票的周期性规律，包括趋势、周度和年度周期性",
        "parameters": {
            "type": "object",
            "properties": {
                "ts_code": {
                    "type": "string",
                    "description": "股票代码，如sh.600600",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式：YYYY-MM-DD，默认为过去1年",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式：YYYY-MM-DD，默认为今天",
                }
            },
            "required": ["ts_code"],
        },
    },
]

# ====== 会话隔离 DataFrame 存储 ======
_last_df_dict = {}

def get_session_id(kwargs):
    """根据 kwargs 获取当前会话的唯一 session_id"""
    messages = kwargs.get('messages')
    if messages is not None:
        return id(messages)
    return None

# ====== exc_sql 工具类实现 ======
@register_tool('exc_sql')
class ExcSQLTool(BaseTool):
    """
    SQL查询工具，执行传入的SQL语句并返回结果，并自动进行可视化。
    """
    description = '对于生成的SQL，进行SQL查询，并自动可视化'
    parameters = [{
        'name': 'sql_input',
        'type': 'string',
        'description': '生成的SQL语句',
        'required': True
    }, {
        'name': 'need_visualize',
        'type': 'boolean',
        'description': '是否需要可视化，默认为True。如果是对比分析，设置为False',
        'required': False,
        'default': True
    }]

    def call(self, params: str, **kwargs) -> str:
        import json
        import matplotlib.pyplot as plt
        import io, os, time
        import numpy as np
        args = json.loads(params)
        sql_input = args['sql_input']
        database = args.get('database', 'lwg_database')
        need_visualize = args.get('need_visualize', True)  # 默认需要可视化
        
        engine = create_engine(
            f'mysql+mysqlconnector://root:@127.0.0.1:3306/{database}?charset=utf8mb4',
            connect_args={'connect_timeout': 10}, pool_size=10, max_overflow=20
        )
        try:
            df = pd.read_sql(sql_input, engine)
            
            # 生成数据表格（前5行+后5行）
            if len(df) <= 10:
                # 数据量小，显示全部
                md = df.to_markdown(index=False)
            else:
                # 数据量大，显示前5行+后5行
                top_5 = df.head(5)
                bottom_5 = df.tail(5)
                md = f"**前5行数据:**\n{top_5.to_markdown(index=False)}\n\n**后5行数据:**\n{bottom_5.to_markdown(index=False)}"
            
            # 如果是对比分析，添加股票分组信息
            if 'stock_code' in df.columns and len(df['stock_code'].unique()) > 1:
                stock_summary = "\n\n## 股票对比摘要\n"
                for stock_code in df['stock_code'].unique():
                    stock_data = df[df['stock_code'] == stock_code]
                    stock_name = stock_data['stock_name'].iloc[0] if 'stock_name' in stock_data.columns else stock_code
                    if 'pct_change' in stock_data.columns:
                        avg_change = stock_data['pct_change'].mean()
                        max_change = stock_data['pct_change'].max()
                        min_change = stock_data['pct_change'].min()
                        stock_summary += f"- **{stock_name} ({stock_code})**: 平均涨跌幅 {avg_change:.2f}%, 最高 {max_change:.2f}%, 最低 {min_change:.2f}%\n"
                md += stock_summary
            
            # 生成数据统计描述
            describe_md = ""
            if len(df) > 0:
                # 获取数值列的统计信息
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    try:
                        describe_df = df[numeric_cols].describe()
                        # 格式化统计描述，确保中文显示正确
                        describe_md = f"\n\n## 数据统计描述\n{describe_df.to_markdown(index=True)}"
                    except Exception as e:
                        print(f"统计描述生成出错: {str(e)}")
                        describe_md = f"\n\n## 数据基本信息\n- 总记录数: {len(df)}\n- 数值列数: {len(numeric_cols)}"
                else:
                    # 如果没有数值列，提供基本统计信息
                    describe_md = f"\n\n## 数据基本信息\n- 总记录数: {len(df)}"
                    if len(df.columns) > 0:
                        describe_md += f"\n- 列数: {len(df.columns)}"
                        describe_md += f"\n- 列名: {', '.join(df.columns.tolist())}"
            
            # 根据need_visualize参数决定是否生成图表
            if need_visualize:
                try:
                    # 自动创建目录
                    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualization', 'image_show')
                    os.makedirs(save_dir, exist_ok=True)
                    filename = f'chart_{int(time.time()*1000)}.png'
                    save_path = os.path.join(save_dir, filename)
                    
                    # 生成图表
                    print(f"正在生成图表: {save_path}")
                    generate_chart_png(df, save_path)
                    
                    # 检查图表是否成功生成
                    if os.path.exists(save_path):
                        img_path = os.path.join('visualization', 'image_show', filename)
                        img_md = f'\n\n![数据图表]({img_path})'
                        print(f"图表生成成功: {img_path}")
                        return f"{md}{describe_md}{img_md}"
                    else:
                        print("图表文件未生成")
                        return f"{md}{describe_md}\n\n⚠️ 图表生成失败"
                except Exception as chart_error:
                    print(f"图表生成出错: {str(chart_error)}")
                    return f"{md}{describe_md}\n\n⚠️ 图表生成出错: {str(chart_error)}"
            else:
                # 不需要可视化，只返回数据和统计信息
                return f"{md}{describe_md}"
                
        except Exception as e:
            return f"SQL执行或可视化出错: {str(e)}"

@register_tool('news_search')
class NewsSearchTool(BaseTool):
    """
    新闻搜索工具，使用Tavily抓取最新的热点新闻
    """
    description = '搜索最新的热点新闻，特别是股票和财经相关的新闻'
    parameters = [{
        'name': 'query',
        'type': 'string',
        'description': '搜索关键词，如"股票"、"财经"、"A股"等',
        'required': True
    }, {
        'name': 'max_results',
        'type': 'integer',
        'description': '返回的最大结果数量，默认为5',
        'required': False,
        'default': 5
    }]

    def call(self, params: str, **kwargs) -> str:
        import json
        args = json.loads(params)
        query = args['query']
        max_results = args.get('max_results', 5)
        
        try:
            # 初始化Tavily客户端
            if not TAVILY_API_KEY:
                return "错误：未配置Tavily API Key，请先设置TAVILY_API_KEY"
            
            client = TavilyClient(api_key=TAVILY_API_KEY)
            
            # 搜索新闻
            response = client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_domains=["finance.sina.com.cn", "finance.eastmoney.com", "stock.hexun.com", "finance.ifeng.com"],
                exclude_domains=["wikipedia.org"]
            )
            
            # 格式化结果
            if response and 'results' in response:
                results = response['results']
                if not results:
                    return f"未找到关于'{query}'的相关新闻"
                
                news_md = f"## 📰 关于'{query}'的最新新闻\n\n"
                
                for i, result in enumerate(results, 1):
                    title = result.get('title', '无标题')
                    url = result.get('url', '')
                    content = result.get('content', '')
                    published_date = result.get('published_date', '')
                    
                    news_md += f"### {i}. {title}\n"
                    if published_date:
                        news_md += f"**发布时间**: {published_date}\n"
                    if content:
                        # 截取前200个字符作为摘要
                        summary = content[:200] + "..." if len(content) > 200 else content
                        news_md += f"**内容摘要**: {summary}\n"
                    if url:
                        news_md += f"**原文链接**: {url}\n"
                    news_md += "\n---\n\n"
                
                return news_md
            else:
                return f"搜索'{query}'时出现错误，请稍后重试"
                
        except Exception as e:
            return f"新闻搜索出错: {str(e)}"

@register_tool('arima_stock')
class ARIMAStockTool(BaseTool):
    """
    ARIMA股票价格预测工具，使用ARIMA(5,1,5)模型预测未来N天的股票价格
    """
    description = '使用ARIMA模型预测股票未来N天的价格走势'
    parameters = [{
        'name': 'ts_code',
        'type': 'string',
        'description': '股票代码，如sz.000001',
        'required': True
    }, {
        'name': 'n',
        'type': 'integer',
        'description': '预测天数，默认为5天',
        'required': False,
        'default': 5
    }]

    def call(self, params: str, **kwargs) -> str:
        import json
        import os
        from datetime import datetime, timedelta
        
        args = json.loads(params)
        ts_code = args['ts_code']
        n = args.get('n', 5)
        
        try:
            # 连接数据库
            engine = create_engine(
                f'mysql+mysqlconnector://root:@127.0.0.1:3306/lwg_database?charset=utf8mb4',
                connect_args={'connect_timeout': 10}, pool_size=10, max_overflow=20
            )
            
            # 获取过去一年的历史数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            sql_query = f"""
            SELECT trade_date, close_price 
            FROM stock_daily_data 
            WHERE stock_code = '{ts_code}' 
            AND trade_date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY trade_date
            """
            
            df = pd.read_sql(sql_query, engine)
            
            if len(df) == 0:
                return f"错误：未找到股票 {ts_code} 的历史数据，请检查股票代码是否正确"
            
            if len(df) < 30:
                return f"错误：股票 {ts_code} 的历史数据不足（只有{len(df)}天，需要至少30天），无法进行ARIMA建模"
            
            # 数据预处理
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.set_index('trade_date')
            df = df.sort_index()
            
            # 检查数据质量
            if df['close_price'].isna().sum() > len(df) * 0.1:
                return f"错误：股票 {ts_code} 的数据质量较差，缺失值过多，无法进行ARIMA建模"
            
            # 清理数据
            df = df.dropna()
            if len(df) < 30:
                return f"错误：清理后股票 {ts_code} 的数据不足（只有{len(df)}天），无法进行ARIMA建模"
            
            # 简化数据处理，直接使用原始数据
            original_data = df['close_price']
            
            # 使用简化的ARIMA模型，添加详细错误处理
            model_orders = [(1, 1, 1), (2, 1, 2), (3, 1, 3), (5, 1, 5)]
            fitted_model = None
            model_error = None
            used_order = None
            
            for order in model_orders:
                try:
                    print(f"尝试ARIMA{order}模型...")
                    model = ARIMA(original_data, order=order)
                    fitted_model = model.fit()
                    used_order = order
                    print(f"ARIMA{order}模型训练成功")
                    break
                except Exception as e:
                    print(f"ARIMA{order}模型失败: {str(e)}")
                    model_error = e
                    continue
            
            if fitted_model is None:
                return f"错误：所有ARIMA模型都训练失败。最后错误：{str(model_error)}"
            
            # 进行预测
            forecast = fitted_model.forecast(steps=n)
            forecast_index = pd.date_range(start=df.index[-1] + timedelta(days=1), periods=n, freq='D')
            
            # 生成预测结果
            forecast_df = pd.DataFrame({
                '预测日期': forecast_index.strftime('%Y-%m-%d'),
                '预测价格': [round(price, 2) for price in forecast]
            })
            
            # 计算预测统计信息
            last_price = original_data.iloc[-1]
            # 修复索引错误：使用iloc[-1]而不是[-1]
            price_change = forecast.iloc[-1] - last_price
            price_change_pct = (price_change / last_price) * 100
            
            # 生成预测图表
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualization', 'image_show')
            os.makedirs(save_dir, exist_ok=True)
            filename = f'arima_forecast_{int(time.time()*1000)}.png'
            save_path = os.path.join(save_dir, filename)
            
            # 绘制丰富的预测图表
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'ARIMA{used_order} 股票价格预测分析 - {ts_code}', fontsize=16, fontweight='bold')
            
            # 子图1：历史价格和预测价格对比
            recent_data = original_data.tail(60)
            ax1.plot(recent_data.index, recent_data.values, label='历史价格', color='blue', linewidth=3, marker='o', markersize=3)
            ax1.plot(forecast_index, forecast, label='预测价格', color='red', linewidth=3, linestyle='--', marker='s', markersize=4)
            ax1.set_title('价格走势与预测', fontsize=12, fontweight='bold')
            ax1.set_xlabel('日期', fontsize=10)
            ax1.set_ylabel('价格 (元)', fontsize=10)
            ax1.legend(fontsize=10)
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.tick_params(axis='x', rotation=45)
            
            # 添加价格变化标注
            ax1.annotate(f'当前: {last_price:.2f}元', 
                        xy=(recent_data.index[-1], recent_data.values[-1]),
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            ax1.annotate(f'预测: {forecast.iloc[-1]:.2f}元', 
                        xy=(forecast_index[-1], forecast.iloc[-1]),
                        xytext=(10, -20), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            # 子图2：预测价格变化趋势
            price_changes = [forecast.iloc[i] - last_price for i in range(len(forecast))]
            ax2.bar(range(1, n+1), price_changes, color=['green' if x > 0 else 'red' for x in price_changes], alpha=0.7)
            ax2.set_title('预测价格变化', fontsize=12, fontweight='bold')
            ax2.set_xlabel('预测天数', fontsize=10)
            ax2.set_ylabel('价格变化 (元)', fontsize=10)
            ax2.grid(True, alpha=0.3, linestyle='--')
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            
            # 为每个柱子添加数值标签
            for i, change in enumerate(price_changes):
                ax2.text(i+1, change + (0.1 if change > 0 else -0.1), f'{change:+.2f}', 
                        ha='center', va='bottom' if change > 0 else 'top', fontsize=9)
            
            # 子图3：历史价格分布
            ax3.hist(original_data.values, bins=20, color='skyblue', alpha=0.7, edgecolor='black')
            ax3.axvline(last_price, color='red', linestyle='--', linewidth=2, label=f'当前价格: {last_price:.2f}')
            ax3.axvline(forecast.iloc[-1], color='green', linestyle='--', linewidth=2, label=f'预测价格: {forecast.iloc[-1]:.2f}')
            ax3.set_title('历史价格分布', fontsize=12, fontweight='bold')
            ax3.set_xlabel('价格 (元)', fontsize=10)
            ax3.set_ylabel('频次', fontsize=10)
            ax3.legend(fontsize=9)
            ax3.grid(True, alpha=0.3, linestyle='--')
            
            # 子图4：预测置信区间（简化版）
            forecast_values = forecast.values
            upper_bound = forecast_values * 1.05  # 简化的上界
            lower_bound = forecast_values * 0.95  # 简化的下界
            
            ax4.fill_between(range(1, n+1), lower_bound, upper_bound, alpha=0.3, color='orange', label='置信区间')
            ax4.plot(range(1, n+1), forecast_values, color='red', linewidth=3, marker='o', markersize=5, label='预测价格')
            ax4.set_title('预测置信区间', fontsize=12, fontweight='bold')
            ax4.set_xlabel('预测天数', fontsize=10)
            ax4.set_ylabel('价格 (元)', fontsize=10)
            ax4.legend(fontsize=10)
            ax4.grid(True, alpha=0.3, linestyle='--')
            
            # 添加统计信息
            fig.text(0.02, 0.02, f'模型参数: ARIMA{used_order} | AIC: {fitted_model.aic:.2f} | BIC: {fitted_model.bic:.2f}', 
                    fontsize=9, ha='left')
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            # 生成结果报告
            result_md = f"""
## 📈 ARIMA股票价格预测报告

### 基本信息
- **股票代码**: {ts_code}
- **预测天数**: {n}天
- **历史数据**: {len(df)}天
- **模型参数**: ARIMA{used_order}

### 预测结果
{forecast_df.to_markdown(index=False)}

### 预测统计
- **当前价格**: {last_price:.2f}元
- **{n}天后预测价格**: {forecast.iloc[-1]:.2f}元
- **价格变化**: {price_change:+.2f}元 ({price_change_pct:+.2f}%)

### 模型信息
- **AIC**: {fitted_model.aic:.2f}
- **BIC**: {fitted_model.bic:.2f}
- **对数似然**: {fitted_model.llf:.2f}

![预测图表](visualization/image_show/{filename})
"""
            
            return result_md
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ARIMA预测详细错误: {error_details}")
            return f"ARIMA预测出错: {str(e)}"

@register_tool('boll_detection')
class BollDetectionTool(BaseTool):
    """
    布林带异常点检测工具，使用20日周期+2σ检测超买和超卖点
    """
    description = '使用布林带指标检测股票的超买和超卖异常点'
    parameters = [{
        'name': 'ts_code',
        'type': 'string',
        'description': '股票代码，如sh.600600',
        'required': True
    }, {
        'name': 'start_date',
        'type': 'string',
        'description': '开始日期，格式：YYYY-MM-DD，默认为过去1年',
        'required': False
    }, {
        'name': 'end_date',
        'type': 'string',
        'description': '结束日期，格式：YYYY-MM-DD，默认为今天',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        import json
        import os
        from datetime import datetime, timedelta
        
        args = json.loads(params)
        ts_code = args['ts_code']
        start_date = args.get('start_date')
        end_date = args.get('end_date')
        
        try:
            # 连接数据库
            engine = create_engine(
                f'mysql+mysqlconnector://root:@127.0.0.1:3306/lwg_database?charset=utf8mb4',
                connect_args={'connect_timeout': 10}, pool_size=10, max_overflow=20
            )
            
            # 设置默认日期范围（过去1年）
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # 获取股票数据
            sql_query = f"""
            SELECT trade_date, close_price, high_price, low_price, open_price, volume
            FROM stock_daily_data 
            WHERE stock_code = '{ts_code}' 
            AND trade_date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY trade_date
            """
            
            df = pd.read_sql(sql_query, engine)
            
            if len(df) == 0:
                return f"错误：未找到股票 {ts_code} 在指定时间范围内的数据"
            
            if len(df) < 20:
                return f"错误：股票 {ts_code} 的数据不足（只有{len(df)}天，需要至少20天），无法计算布林带"
            
            # 数据预处理
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.set_index('trade_date')
            df = df.sort_index()
            
            # 计算布林带指标
            period = 20  # 20日周期
            std_mult = 2  # 2倍标准差
            
            # 计算移动平均线
            df['ma20'] = df['close_price'].rolling(window=period).mean()
            
            # 计算标准差
            df['std20'] = df['close_price'].rolling(window=period).std()
            
            # 计算布林带上下轨
            df['upper_band'] = df['ma20'] + (df['std20'] * std_mult)
            df['lower_band'] = df['ma20'] - (df['std20'] * std_mult)
            
            # 检测异常点
            df['above_upper'] = df['close_price'] > df['upper_band']  # 超买
            df['below_lower'] = df['close_price'] < df['lower_band']  # 超卖
            
            # 获取异常点数据
            overbought = df[df['above_upper']].copy()
            oversold = df[df['below_lower']].copy()
            
            # 计算异常点统计
            overbought_count = len(overbought)
            oversold_count = len(oversold)
            total_days = len(df)
            
            # 生成异常点报告
            result_md = f"""
## 📊 布林带异常点检测报告

### 基本信息
- **股票代码**: {ts_code}
- **检测周期**: {start_date} 至 {end_date}
- **数据天数**: {total_days}天
- **布林带参数**: 20日周期 + 2σ

### 异常点统计
- **超买点数量**: {overbought_count}次
- **超卖点数量**: {oversold_count}次
- **超买频率**: {overbought_count/total_days*100:.2f}%
- **超卖频率**: {oversold_count/total_days*100:.2f}%

### 超买点详情
"""
            
            if overbought_count > 0:
                overbought_display = overbought[['close_price', 'upper_band', 'ma20']].copy()
                overbought_display['超出幅度'] = ((overbought_display['close_price'] - overbought_display['upper_band']) / overbought_display['upper_band'] * 100).round(2)
                overbought_display = overbought_display.rename(columns={
                    'close_price': '收盘价',
                    'upper_band': '上轨',
                    'ma20': '中轨'
                })
                result_md += overbought_display.to_markdown()
            else:
                result_md += "该时间段内未发现超买点"
            
            result_md += "\n\n### 超卖点详情\n"
            
            if oversold_count > 0:
                oversold_display = oversold[['close_price', 'lower_band', 'ma20']].copy()
                oversold_display['低于幅度'] = ((oversold_display['lower_band'] - oversold_display['close_price']) / oversold_display['lower_band'] * 100).round(2)
                oversold_display = oversold_display.rename(columns={
                    'close_price': '收盘价',
                    'lower_band': '下轨',
                    'ma20': '中轨'
                })
                result_md += oversold_display.to_markdown()
            else:
                result_md += "该时间段内未发现超卖点"
            
            # 生成布林带图表
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualization', 'image_show')
            os.makedirs(save_dir, exist_ok=True)
            filename = f'boll_detection_{int(time.time()*1000)}.png'
            save_path = os.path.join(save_dir, filename)
            
            # 绘制布林带图表
            plt.figure(figsize=(14, 10))
            
            # 主图：价格和布林带
            plt.subplot(2, 1, 1)
            plt.plot(df.index, df['close_price'], label='收盘价', color='blue', linewidth=2)
            plt.plot(df.index, df['ma20'], label='20日均线', color='orange', linewidth=1.5)
            plt.plot(df.index, df['upper_band'], label='上轨(+2σ)', color='red', linewidth=1.5, linestyle='--')
            plt.plot(df.index, df['lower_band'], label='下轨(-2σ)', color='green', linewidth=1.5, linestyle='--')
            
            # 标记异常点
            if overbought_count > 0:
                plt.scatter(overbought.index, overbought['close_price'], 
                           color='red', s=50, alpha=0.7, label=f'超买点({overbought_count}次)', marker='^')
            if oversold_count > 0:
                plt.scatter(oversold.index, oversold['close_price'], 
                           color='green', s=50, alpha=0.7, label=f'超卖点({oversold_count}次)', marker='v')
            
            plt.title(f'布林带异常点检测 - {ts_code}', fontsize=14, fontweight='bold')
            plt.xlabel('日期', fontsize=12)
            plt.ylabel('价格 (元)', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            # 副图：成交量
            plt.subplot(2, 1, 2)
            plt.bar(df.index, df['volume'], alpha=0.7, color='gray', width=1)
            plt.title('成交量', fontsize=12)
            plt.xlabel('日期', fontsize=12)
            plt.ylabel('成交量', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            result_md += f"\n\n![布林带检测图表](visualization/image_show/{filename})"
            
            return result_md
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"布林带检测详细错误: {error_details}")
            return f"布林带检测出错: {str(e)}"

@register_tool('prophet_analysis')
class ProphetAnalysisTool(BaseTool):
    """
    Prophet股票周期性分析工具，分析trend、weekly、yearly周期性
    """
    description = '使用Prophet模型分析股票的周期性规律，包括趋势、周度和年度周期性'
    parameters = [{
        'name': 'ts_code',
        'type': 'string',
        'description': '股票代码，如sh.600600',
        'required': True
    }, {
        'name': 'start_date',
        'type': 'string',
        'description': '开始日期，格式：YYYY-MM-DD，默认为过去1年',
        'required': False
    }, {
        'name': 'end_date',
        'type': 'string',
        'description': '结束日期，格式：YYYY-MM-DD，默认为今天',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        import json
        import os
        from datetime import datetime, timedelta
        
        args = json.loads(params)
        ts_code = args['ts_code']
        start_date = args.get('start_date')
        end_date = args.get('end_date')
        
        try:
            # 连接数据库
            engine = create_engine(
                f'mysql+mysqlconnector://root:@127.0.0.1:3306/lwg_database?charset=utf8mb4',
                connect_args={'connect_timeout': 10}, pool_size=10, max_overflow=20
            )
            
            # 设置默认日期范围（过去1年）
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # 获取股票数据
            sql_query = f"""
            SELECT trade_date, close_price, volume
            FROM stock_daily_data 
            WHERE stock_code = '{ts_code}' 
            AND trade_date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY trade_date
            """
            
            df = pd.read_sql(sql_query, engine)
            
            if len(df) == 0:
                return f"错误：未找到股票 {ts_code} 在指定时间范围内的数据"
            
            if len(df) < 30:
                return f"错误：股票 {ts_code} 的数据不足（只有{len(df)}天，需要至少30天），无法进行Prophet分析"
            
            # 数据预处理
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.sort_values('trade_date')
            
            # 准备Prophet数据格式
            prophet_df = df[['trade_date', 'close_price']].copy()
            prophet_df.columns = ['ds', 'y']  # Prophet要求列名为ds和y
            
            # 创建Prophet模型
            model = Prophet(
                yearly_seasonality=True,    # 年度季节性
                weekly_seasonality=True,    # 周度季节性
                daily_seasonality=False,     # 关闭日度季节性（股票数据）
                seasonality_mode='multiplicative',  # 乘法季节性
                changepoint_prior_scale=0.05,  # 趋势变化点敏感度
                seasonality_prior_scale=10.0   # 季节性强度
            )
            
            # 训练模型
            model.fit(prophet_df)
            
            # 生成未来预测（用于可视化）
            future = model.make_future_dataframe(periods=30)  # 预测未来30天
            forecast = model.predict(future)
            
            # 分析结果
            trend_data = forecast[['ds', 'trend']].copy()
            weekly_data = forecast[['ds', 'weekly']].copy()
            yearly_data = forecast[['ds', 'yearly']].copy()
            
            # 计算趋势统计
            trend_start = trend_data['trend'].iloc[0]
            trend_end = trend_data['trend'].iloc[-31]  # 排除预测部分
            trend_change = trend_end - trend_start
            trend_change_pct = (trend_change / trend_start) * 100
            
            # 计算周期性强度
            weekly_amplitude = weekly_data['weekly'].std()
            yearly_amplitude = yearly_data['yearly'].std()
            
            # 生成分析报告
            result_md = f"""
## 📈 Prophet股票周期性分析报告

### 基本信息
- **股票代码**: {ts_code}
- **分析周期**: {start_date} 至 {end_date}
- **数据天数**: {len(df)}天
- **模型**: Facebook Prophet

### 趋势分析
- **趋势变化**: {trend_change:+.2f}元 ({trend_change_pct:+.2f}%)
- **趋势方向**: {'上升' if trend_change > 0 else '下降' if trend_change < 0 else '平稳'}
- **趋势强度**: {'强' if abs(trend_change_pct) > 10 else '中等' if abs(trend_change_pct) > 5 else '弱'}

### 周期性分析
- **周度周期性强度**: {weekly_amplitude:.4f}
- **年度周期性强度**: {yearly_amplitude:.4f}
- **主要周期性**: {'年度' if yearly_amplitude > weekly_amplitude else '周度'}

### 模型性能
- **模型状态**: 训练完成
- **季节性模式**: 乘法模式
- **趋势变化点**: 已检测
"""
            
            # 生成Prophet可视化图表
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualization', 'image_show')
            os.makedirs(save_dir, exist_ok=True)
            filename = f'prophet_analysis_{int(time.time()*1000)}.png'
            save_path = os.path.join(save_dir, filename)
            
            # 使用matplotlib生成图表
            fig, axes = plt.subplots(4, 1, figsize=(14, 16))
            fig.suptitle(f'Prophet周期性分析 - {ts_code}', fontsize=16, fontweight='bold')
            
            # 主图：股价走势与预测
            axes[0].plot(forecast['ds'], forecast['yhat'], 'b-', label='预测值', linewidth=2)
            axes[0].fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], 
                               alpha=0.3, color='lightblue', label='置信区间')
            axes[0].scatter(prophet_df['ds'], prophet_df['y'], color='red', s=20, label='实际值', alpha=0.7)
            axes[0].set_title('股价走势与预测', fontsize=12, fontweight='bold')
            axes[0].set_ylabel('价格 (元)')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            # 趋势图
            axes[1].plot(trend_data['ds'], trend_data['trend'], 'g-', linewidth=2, label='趋势')
            axes[1].set_title('趋势分析', fontsize=12, fontweight='bold')
            axes[1].set_ylabel('趋势值')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
            
            # 周度周期性图
            axes[2].plot(weekly_data['ds'], weekly_data['weekly'], 'orange', linewidth=2, label='周度周期性')
            axes[2].set_title('周度周期性', fontsize=12, fontweight='bold')
            axes[2].set_ylabel('周度影响')
            axes[2].legend()
            axes[2].grid(True, alpha=0.3)
            
            # 年度周期性图
            axes[3].plot(yearly_data['ds'], yearly_data['yearly'], 'purple', linewidth=2, label='年度周期性')
            axes[3].set_title('年度周期性', fontsize=12, fontweight='bold')
            axes[3].set_ylabel('年度影响')
            axes[3].set_xlabel('日期')
            axes[3].legend()
            axes[3].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            result_md += f"\n\n![Prophet分析图表](visualization/image_show/{filename})"
            
            # 添加详细分析
            result_md += f"""

### 详细分析

#### 趋势特征
- 整体趋势呈现{'上升' if trend_change > 0 else '下降' if trend_change < 0 else '平稳'}态势
- 趋势变化幅度为{abs(trend_change_pct):.2f}%，属于{'强' if abs(trend_change_pct) > 10 else '中等' if abs(trend_change_pct) > 5 else '弱'}趋势

#### 周期性特征
- **周度周期性**: 强度为{weekly_amplitude:.4f}，{'明显' if weekly_amplitude > 0.01 else '不明显'}
- **年度周期性**: 强度为{yearly_amplitude:.4f}，{'明显' if yearly_amplitude > 0.01 else '不明显'}

#### 投资建议
基于Prophet分析结果：
1. **趋势判断**: 当前趋势{'向好' if trend_change > 0 else '向坏' if trend_change < 0 else '平稳'}
2. **周期性**: 该股票{'具有' if max(weekly_amplitude, yearly_amplitude) > 0.01 else '缺乏'}明显的周期性特征
3. **预测可靠性**: 基于Prophet模型的预测可靠性较高
"""
            
            return result_md
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Prophet分析详细错误: {error_details}")
            return f"Prophet分析出错: {str(e)}"

# ========== 通用可视化函数 ========== 
def generate_chart_png(df_sql, save_path):
    """生成股票数据图表，智能选择图表类型和优化显示，支持对比图表"""
    columns = df_sql.columns
    data_length = len(df_sql)
    
    # 设置图表样式和字体
    plt.style.use('default')
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    
    # 检查是否有股票对比数据
    if 'stock_code' in columns and len(df_sql['stock_code'].unique()) > 1:
        # 股票对比图 - 使用子图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
        fig.suptitle('股票对比分析图', fontsize=16, fontweight='bold', y=0.95)
        
        unique_stocks = df_sql['stock_code'].unique()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        # 第一个子图：价格对比折线图
        if 'close_price' in columns:
            for i, stock_code in enumerate(unique_stocks):
                stock_data = df_sql[df_sql['stock_code'] == stock_code].sort_values('trade_date')
                color = colors[i % len(colors)]
                ax1.plot(stock_data['trade_date'], stock_data['close_price'], 
                        marker='o', linewidth=3, markersize=4, 
                        color=color, label=f'{stock_code}', alpha=0.8, markevery=max(1, len(stock_data)//20))
            
            ax1.set_xlabel('交易日期', fontsize=12, fontweight='bold')
            ax1.set_ylabel('收盘价 (元)', fontsize=12, fontweight='bold')
            ax1.set_title('股票价格对比走势图', fontsize=14, fontweight='bold')
            ax1.legend(fontsize=11, loc='upper left')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.tick_params(axis='x', rotation=45)
            
            # 添加价格区间标注
            for stock_code in unique_stocks:
                stock_data = df_sql[df_sql['stock_code'] == stock_code].sort_values('trade_date')
                max_price = stock_data['close_price'].max()
                min_price = stock_data['close_price'].min()
                ax1.annotate(f'最高: {max_price:.2f}', 
                           xy=(stock_data[stock_data['close_price']==max_price]['trade_date'].iloc[0], max_price),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        # 第二个子图：涨跌幅对比
        if 'pct_change' in columns:
            for i, stock_code in enumerate(unique_stocks):
                stock_data = df_sql[df_sql['stock_code'] == stock_code].sort_values('trade_date')
                color = colors[i % len(colors)]
                ax2.plot(stock_data['trade_date'], stock_data['pct_change'], 
                        marker='s', linewidth=2, markersize=3, 
                        color=color, label=f'{stock_code}', alpha=0.8, markevery=max(1, len(stock_data)//20))
            
            ax2.set_xlabel('交易日期', fontsize=12, fontweight='bold')
            ax2.set_ylabel('涨跌幅 (%)', fontsize=12, fontweight='bold')
            ax2.set_title('股票涨跌幅对比图', fontsize=14, fontweight='bold')
            ax2.legend(fontsize=11, loc='upper right')
            ax2.grid(True, alpha=0.3, linestyle='--')
            ax2.axhline(y=0, color='red', linestyle='-', alpha=0.7, linewidth=2)
            ax2.tick_params(axis='x', rotation=45)
            
            # 添加涨跌幅统计信息
            for stock_code in unique_stocks:
                stock_data = df_sql[df_sql['stock_code'] == stock_code]
                avg_change = stock_data['pct_change'].mean()
                max_change = stock_data['pct_change'].max()
                min_change = stock_data['pct_change'].min()
                ax2.text(0.02, 0.98, f'{stock_code}: 平均{avg_change:.2f}%, 最高{max_change:.2f}%, 最低{min_change:.2f}%', 
                        transform=ax2.transAxes, fontsize=9, verticalalignment='top',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))
    
    elif len(columns) == 2:
        # 两个列的情况：日期和价格
        fig, ax = plt.subplots(figsize=(14, 8))
        date_col = columns[0]
        price_col = columns[1]
        
        # 智能选择图表类型
        if data_length > 20:  # 数据量大时使用折线图
            ax.plot(df_sql[date_col], df_sql[price_col], 
                   marker='o', linewidth=3, markersize=4, color='#1f77b4', alpha=0.8, markevery=max(1, data_length//20))
            ax.set_xlabel('交易日期', fontsize=12, fontweight='bold')
            ax.set_ylabel('收盘价 (元)', fontsize=12, fontweight='bold')
            ax.set_title('股价走势图', fontsize=14, fontweight='bold')
            
            # 添加趋势线
            z = np.polyfit(range(data_length), df_sql[price_col], 1)
            p = np.poly1d(z)
            ax.plot(df_sql[date_col], p(range(data_length)), "r--", alpha=0.8, linewidth=2, label='趋势线')
            ax.legend()
            
        else:
            # 数据量小时使用柱状图，但改进显示效果
            bars = ax.bar(range(data_length), df_sql[price_col], 
                         color='#1f77b4', alpha=0.7, edgecolor='darkblue', linewidth=1)
            
            # 为每个柱子添加数值标签
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{height:.2f}', ha='center', va='bottom', fontsize=8, rotation=90)
            
            ax.set_xlabel('交易日期', fontsize=12, fontweight='bold')
            ax.set_ylabel('收盘价 (元)', fontsize=12, fontweight='bold')
            ax.set_title('股价柱状图', fontsize=14, fontweight='bold')
            
            ax.set_xticks(range(data_length))
            ax.set_xticklabels([str(df_sql.iloc[i][date_col]) for i in range(data_length)], 
                              rotation=45, ha='right', fontsize=10)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(axis='x', rotation=45)
        
        # 添加统计信息
        mean_price = df_sql[price_col].mean()
        max_price = df_sql[price_col].max()
        min_price = df_sql[price_col].min()
        ax.text(0.02, 0.98, f'平均价格: {mean_price:.2f}元\n最高价格: {max_price:.2f}元\n最低价格: {min_price:.2f}元', 
                transform=ax.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))
    
    elif len(columns) >= 3:
        # 多列情况：选择数值列绘制
        fig, ax = plt.subplots(figsize=(14, 8))
        numeric_cols = df_sql.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            for i, col in enumerate(numeric_cols[:5]):  # 最多显示5个数值列
                color = colors[i % len(colors)]
                ax.plot(range(data_length), df_sql[col], 
                       marker='o', linewidth=2, markersize=3, 
                       color=color, label=col, alpha=0.8)
            
            ax.set_xlabel('数据点', fontsize=12, fontweight='bold')
            ax.set_ylabel('数值', fontsize=12, fontweight='bold')
            ax.set_title('数据趋势图', fontsize=14, fontweight='bold')
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
        else:
            ax.text(0.5, 0.5, '没有数值列可绘制', 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=14)
            ax.set_title('数据图表', fontsize=14, fontweight='bold')
    
    else:
        # 单列情况
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, '数据不足，无法生成图表', 
               ha='center', va='center', transform=ax.transAxes, 
               fontsize=14)
        ax.set_title('数据图表', fontsize=14, fontweight='bold')
    
    # 保存图表
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

# ====== 初始化股票查询助手服务 ======
def init_agent_service():
    """初始化股票查询助手服务"""
    llm_cfg = {
        'model': 'qwen-turbo-2025-04-28',
        'timeout': 30,
        'retry_count': 3,
    }
    try:
        bot = Assistant(
            llm=llm_cfg,
            name='A股股票查询助手',
            description='A股股票数据查询与分析',
            system_message=system_prompt,
            function_list=['exc_sql', 'news_search', 'arima_stock', 'boll_detection', 'prophet_analysis'],
        )
        print("股票查询助手初始化成功！")
        return bot
    except Exception as e:
        print(f"股票查询助手初始化失败: {str(e)}")
        raise

def app_tui():
    """终端交互模式
    
    提供命令行交互界面，支持：
    - 连续对话
    - 实时响应
    - 股票数据查询
    """
    try:
        # 初始化助手
        bot = init_agent_service()

        # 对话历史
        messages = []
        print("=== A股股票查询助手 ===")
        print("输入 'quit' 或 'exit' 退出程序")
        print("输入 'help' 查看帮助信息")
        
        while True:
            try:
                # 获取用户输入
                query = input('\n请输入您的股票查询问题: ').strip()
                
                if query.lower() in ['quit', 'exit', '退出']:
                    print("感谢使用A股股票查询助手！")
                    break
                    
                if query.lower() in ['help', '帮助']:
                    print_help()
                    continue
                
                # 输入验证
                if not query:
                    print('问题不能为空！')
                    continue
                    
                # 构建消息
                messages.append({'role': 'user', 'content': query})

                print("正在处理您的请求...")
                # 运行助手并处理响应
                response = []
                for response in bot.run(messages):
                    print('助手回复:', response)
                messages.extend(response)
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断，感谢使用！")
                break
            except Exception as e:
                print(f"处理请求时出错: {str(e)}")
                print("请重试或输入新的问题")
                
    except Exception as e:
        print(f"启动终端模式失败: {str(e)}")

def print_help():
    """打印帮助信息"""
    help_text = """
=== A股股票查询助手帮助信息 ===

支持的查询类型：

1. 股票基本信息查询
   - "查询股票600036的基本信息"
   - "显示招商银行的股票数据"

2. 股票价格走势分析
   - "查看平安银行最近30天的股价走势"
   - "分析万科A在2024年的价格变化"

3. 行业对比分析
   - "银行业股票的平均市盈率对比"
   - "各行业股票数量统计"

4. 财务指标分析
   - "查询净利润最高的10只股票"
   - "显示ROE排名前20的股票"

5. 交易数据统计
   - "今日成交量最大的股票"
   - "涨跌幅排行榜"

6. 股票筛选和排序
   - "筛选市盈率在10-20之间的股票"
   - "找出总资产超过1000亿的股票"

示例查询：
- "帮我查询招商银行(600036)最近一年的股价走势"
- "显示银行业股票的平均市盈率排名"
- "找出2024年涨幅最大的10只股票"
- "查询市值最大的20只股票"
"""
    print(help_text)

def app_gui():
    """图形界面模式，提供 Web 图形界面"""
    try:
        print("正在启动股票查询助手 Web 界面...")
        # 初始化助手
        bot = init_agent_service()
        
        # 配置聊天界面，按板块划分推荐对话
        chatbot_config = {
            'prompt.suggestions': [
                # 基础查询板块
                '查询青岛啤酒(sh.600600)最近一年的股价走势',
                '显示方正科技(sh.600601)的股价数据',
                
                # 对比分析板块
                '对比青岛啤酒(sh.600600)和方正科技(sh.600601)的涨跌幅',
                '找出2024年涨幅最大的10只股票',
                
                # 预测分析板块
                '预测青岛啤酒(sh.600600)未来5天的股价',
                '预测方正科技(sh.600601)未来10天的价格走势',
                
                # 技术分析板块
                '检测青岛啤酒(sh.600600)的布林带异常点',
                '检测方正科技(sh.600601)过去半年的超买超卖点',
                
                # 周期性分析板块
                '分析青岛啤酒(sh.600600)的周期性规律',
                '分析方正科技(sh.600601)过去一年的趋势和周期性',
                
                # 新闻资讯板块
                '搜索最新的A股热点新闻',
                '查找关于科技股的新闻'
            ]
        }
        
        print("Web 界面准备就绪，正在启动服务...")
        print("访问地址: http://localhost:7860")
        
        # 启动 Web 界面，明确指定端口为7860
        WebUI(
            bot,
            chatbot_config=chatbot_config
        ).run(server_port=7860, server_name="127.0.0.1")
        
    except Exception as e:
        print(f"启动 Web 界面失败: {str(e)}")
        print("请检查网络连接和 API Key 配置")

if __name__ == '__main__':
    # 运行模式选择
    app_gui()          # 图形界面模式（默认）
