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

# 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 配置 DashScope API Key
# 请在这里填写您的API Key
API_KEY = "sk-db159bb711df4c46ae4db8100e304516"  # 在这里填写您的DashScope API Key

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
我将回答用户关于股票相关的问题

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
    }]

    def call(self, params: str, **kwargs) -> str:
        import json
        import matplotlib.pyplot as plt
        import io, os, time
        import numpy as np
        args = json.loads(params)
        sql_input = args['sql_input']
        database = args.get('database', 'lwg_database')
        engine = create_engine(
            f'mysql+mysqlconnector://root:@127.0.0.1:3306/{database}?charset=utf8mb4',
            connect_args={'connect_timeout': 10}, pool_size=10, max_overflow=20
        )
        try:
            df = pd.read_sql(sql_input, engine)
            md = df.head(10).to_markdown(index=False)
            # 自动创建目录
            save_dir = os.path.join(os.path.dirname(__file__), 'image_show')
            os.makedirs(save_dir, exist_ok=True)
            filename = f'bar_{int(time.time()*1000)}.png'
            save_path = os.path.join(save_dir, filename)
            # 生成图表
            generate_chart_png(df, save_path)
            img_path = os.path.join('image_show', filename)
            img_md = f'![柱状图]({img_path})'
            return f"{md}\n\n{img_md}"
        except Exception as e:
            return f"SQL执行或可视化出错: {str(e)}"

# ========== 通用可视化函数 ========== 
def generate_chart_png(df_sql, save_path):
    columns = df_sql.columns
    x = np.arange(len(df_sql))
    # 获取object类型
    object_columns = df_sql.select_dtypes(include='O').columns.tolist()
    if columns[0] in object_columns:
        object_columns.remove(columns[0])
    num_columns = df_sql.select_dtypes(exclude='O').columns.tolist()
    if len(object_columns) > 0:
        # 对数据进行透视，以便为每个日期和销售渠道创建堆积柱状图
        pivot_df = df_sql.pivot_table(index=columns[0], columns=object_columns, 
                                      values=num_columns, 
                                      fill_value=0)
        # 绘制堆积柱状图
        fig, ax = plt.subplots(figsize=(10, 6))
        # 为每个销售渠道和票类型创建柱状图
        bottoms = None
        for col in pivot_df.columns:
            ax.bar(pivot_df.index, pivot_df[col], bottom=bottoms, label=str(col))
            if bottoms is None:
                bottoms = pivot_df[col].copy()
            else:
                bottoms += pivot_df[col]
    else:
        print('进入到else...')
        bottom = np.zeros(len(df_sql))
        for column in columns[1:]:
            plt.bar(x, df_sql[column], bottom=bottom, label=column)
            bottom += df_sql[column]
        plt.xticks(x, df_sql[columns[0]])
    plt.legend()
    plt.title("股票数据统计")
    plt.xlabel(columns[0])
    plt.ylabel("数值")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_path)
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
            function_list=['exc_sql'],
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
        
        # 配置聊天界面，列举3个典型股票查询问题
        chatbot_config = {
            'prompt.suggestions': [
                '查询招商银行(600036)最近一年的股价走势',
                '显示银行业股票的平均市盈率排名',
                '找出2024年涨幅最大的10只股票'
            ]
        }
        
        print("Web 界面准备就绪，正在启动服务...")
        print("访问地址: http://localhost:7860")
        
        # 启动 Web 界面
        WebUI(
            bot,
            chatbot_config=chatbot_config
        ).run()
        
    except Exception as e:
        print(f"启动 Web 界面失败: {str(e)}")
        print("请检查网络连接和 API Key 配置")

if __name__ == '__main__':
    # 运行模式选择
    app_gui()          # 图形界面模式（默认）
