#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析Excel文件并生成MySQL建表语句
"""

import pandas as pd
import os
from datetime import datetime

def analyze_excel_data():
    """分析Excel文件数据"""
    excel_file = "A股金融日线数据/完整A股金融日线数据_20250920_221233.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"文件不存在: {excel_file}")
        return None
    
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_file, sheet_name='A股金融日线数据', engine='openpyxl')
        
        print("=== Excel文件数据分析 ===")
        print(f"总行数: {len(df)}")
        print(f"总列数: {len(df.columns)}")
        print(f"列名: {list(df.columns)}")
        
        # 显示前5个股票的数据
        print("\n=== 前5个股票数据 ===")
        first_5_stocks = df['股票代码'].unique()[:5]
        
        for i, stock_code in enumerate(first_5_stocks, 1):
            print(f"\n第{i}个股票: {stock_code}")
            stock_data = df[df['股票代码'] == stock_code]
            print(f"记录数: {len(stock_data)}")
            print("前3条记录:")
            print(stock_data.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return None

def generate_mysql_table_sql(df):
    """生成MySQL建表语句"""
    if df is None:
        return
    
    print("\n=== 生成MySQL建表语句 ===")
    
    # 分析字段类型
    field_types = {}
    
    for column in df.columns:
        # 获取非空值
        non_null_values = df[column].dropna()
        
        if len(non_null_values) == 0:
            field_types[column] = "VARCHAR(255)"
            continue
        
        # 判断字段类型
        if column in ['股票代码', '股票名称', '上市状态', '股票类型', '交易状态', '是否ST', '行业分类', '行业名称']:
            max_length = non_null_values.astype(str).str.len().max()
            field_types[column] = f"VARCHAR({max(50, min(max_length * 2, 255))})"
        
        elif column in ['IPO日期', '交易日期']:
            field_types[column] = "DATE"
        
        elif column in ['开盘价', '最高价', '最低价', '收盘价', '前收盘价', '涨跌幅', '换手率', '市盈率TTM', '市净率', '市销率TTM', '市现率TTM', '每股收益', '净资产收益率']:
            field_types[column] = "DECIMAL(15,4)"
        
        elif column in ['成交量', '成交额', '净利润', '营业收入', '总资产', '净资产']:
            field_types[column] = "BIGINT"
        
        else:
            field_types[column] = "VARCHAR(255)"
    
    # 生成建表语句
    sql_content = """-- A股金融日线数据表
-- 创建时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
-- 数据来源: BaoStock API

CREATE TABLE IF NOT EXISTS `stock_daily_data` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
"""
    
    # 添加字段定义
    for column, field_type in field_types.items():
        # 转换列名为数据库字段名
        db_column = column.replace('股票代码', 'stock_code')
        db_column = db_column.replace('股票名称', 'stock_name')
        db_column = db_column.replace('IPO日期', 'ipo_date')
        db_column = db_column.replace('上市状态', 'listing_status')
        db_column = db_column.replace('股票类型', 'stock_type')
        db_column = db_column.replace('交易日期', 'trade_date')
        db_column = db_column.replace('开盘价', 'open_price')
        db_column = db_column.replace('最高价', 'high_price')
        db_column = db_column.replace('最低价', 'low_price')
        db_column = db_column.replace('收盘价', 'close_price')
        db_column = db_column.replace('前收盘价', 'pre_close_price')
        db_column = db_column.replace('成交量', 'volume')
        db_column = db_column.replace('成交额', 'amount')
        db_column = db_column.replace('涨跌幅', 'pct_change')
        db_column = db_column.replace('换手率', 'turnover_rate')
        db_column = db_column.replace('交易状态', 'trade_status')
        db_column = db_column.replace('市盈率TTM', 'pe_ttm')
        db_column = db_column.replace('市净率', 'pb_ratio')
        db_column = db_column.replace('市销率TTM', 'ps_ttm')
        db_column = db_column.replace('市现率TTM', 'pcf_ttm')
        db_column = db_column.replace('是否ST', 'is_st')
        db_column = db_column.replace('净利润', 'net_profit')
        db_column = db_column.replace('营业收入', 'revenue')
        db_column = db_column.replace('总资产', 'total_assets')
        db_column = db_column.replace('净资产', 'net_assets')
        db_column = db_column.replace('每股收益', 'eps')
        db_column = db_column.replace('净资产收益率', 'roe')
        db_column = db_column.replace('行业分类', 'industry_code')
        db_column = db_column.replace('行业名称', 'industry_name')
        
        # 添加字段定义
        sql_content += f"    `{db_column}` {field_type} COMMENT '{column}',\n"
    
    # 添加索引和表选项
    sql_content += """    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='A股金融日线数据表';

-- 创建索引
CREATE INDEX `idx_stock_code` ON `stock_daily_data` (`stock_code`);
CREATE INDEX `idx_trade_date` ON `stock_daily_data` (`trade_date`);
CREATE INDEX `idx_stock_trade_date` ON `stock_daily_data` (`stock_code`, `trade_date`);
CREATE INDEX `idx_ipo_date` ON `stock_daily_data` (`ipo_date`);

-- 插入数据示例（前5条记录）
"""
    
    # 添加插入数据示例
    if len(df) > 0:
        sample_data = df.head(5)
        sql_content += "\n-- 示例数据插入语句\n"
        
        for _, row in sample_data.iterrows():
            values = []
            for column in df.columns:
                value = row[column]
                if pd.isna(value) or value == '':
                    values.append('NULL')
                elif isinstance(value, str):
                    escaped_value = value.replace("'", "''")
                    values.append(f"'{escaped_value}'")
                else:
                    values.append(str(value))
            
            sql_content += f"INSERT INTO `stock_daily_data` VALUES (NULL, {', '.join(values)}, NOW(), NOW());\n"
    
    return sql_content

def main():
    """主函数"""
    print("分析Excel文件并生成MySQL建表语句")
    print("=" * 50)
    
    # 分析Excel文件
    df = analyze_excel_data()
    
    if df is not None:
        # 生成MySQL建表语句
        sql_content = generate_mysql_table_sql(df)
        
        # 保存到SQL文件
        sql_filename = "stock_daily_data.sql"
        with open(sql_filename, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        print(f"\n✅ MySQL建表语句已生成并保存到: {sql_filename}")
        print(f"📊 数据统计:")
        print(f"   - 总记录数: {len(df)}")
        print(f"   - 股票数量: {df['股票代码'].nunique()}")
        print(f"   - 字段数量: {len(df.columns)}")
        print(f"   - 日期范围: {df['交易日期'].min()} 到 {df['交易日期'].max()}")
    else:
        print("❌ 无法分析Excel文件")

if __name__ == "__main__":
    main()
