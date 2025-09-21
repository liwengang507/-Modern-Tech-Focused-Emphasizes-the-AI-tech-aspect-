#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股金融数据加载器
将CSV/Excel数据导入到MySQL数据库
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockDataLoader:
    """A股金融数据加载器"""
    
    def __init__(self, host='127.0.0.1', database='lwg_database', user='root', password=''):
        """
        初始化数据加载器
        
        Args:
            host (str): 127.0.0.1
            database (str): lwg_database
            user (str): lwg
            password (str): password123456
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                use_unicode=True
            )
            
            if self.connection.is_connected():
                logger.info(f"成功连接到MySQL数据库: {self.database}")
                return True
                
        except Error as e:
            logger.error(f"连接MySQL数据库失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("已断开MySQL数据库连接")
    
    def create_database(self):
        """创建数据库（如果不存在）"""
        try:
            # 先连接到MySQL服务器（不指定数据库）
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )
            
            cursor = temp_connection.cursor()
            
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"数据库 {self.database} 创建成功或已存在")
            
            cursor.close()
            temp_connection.close()
            
        except Error as e:
            logger.error(f"创建数据库失败: {e}")
    
    def check_table_exists(self):
        """检查数据表是否存在"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'stock_daily_data'")
            result = cursor.fetchone()
            
            if result:
                logger.info("数据表 stock_daily_data 已存在")
                return True
            else:
                logger.error("数据表 stock_daily_data 不存在")
                return False
                
        except Error as e:
            logger.error(f"检查数据表失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def load_csv_data(self, csv_file_path, batch_size=1000):
        """
        从CSV文件加载数据到数据库
        
        Args:
            csv_file_path (str): CSV文件路径
            batch_size (int): 批处理大小
        """
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        if not os.path.exists(csv_file_path):
            logger.error(f"CSV文件不存在: {csv_file_path}")
            return False
        
        try:
            logger.info(f"开始加载CSV数据: {csv_file_path}")
            
            # 读取CSV文件，尝试不同的编码
            try:
                df = pd.read_csv(csv_file_path, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(csv_file_path, encoding='gbk')
                except UnicodeDecodeError:
                    df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
            
            logger.info(f"CSV文件读取成功，共 {len(df)} 行数据")
            
            # 数据预处理
            df = self.preprocess_data(df)
            
            # 分批插入数据
            cursor = self.connection.cursor()
            
            # 构建插入语句（排除id字段）
            columns = [col for col in df.columns if col != 'id']
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"""
                INSERT INTO stock_daily_data ({', '.join(columns)}) 
                VALUES ({placeholders})
            """
            
            total_rows = len(df)
            inserted_rows = 0
            
            for i in range(0, total_rows, batch_size):
                batch_df = df.iloc[i:i+batch_size]
                
                # 准备批量插入数据
                batch_data = []
                for _, row in batch_df.iterrows():
                    values = []
                    for col in columns:  # 只使用指定的列
                        value = row[col]
                        if pd.isna(value):
                            values.append(None)
                        else:
                            values.append(value)
                    batch_data.append(tuple(values))
                
                # 执行批量插入
                cursor.executemany(insert_sql, batch_data)
                self.connection.commit()
                
                inserted_rows += len(batch_data)
                logger.info(f"已插入 {inserted_rows}/{total_rows} 行数据")
            
            logger.info(f"CSV数据加载完成，共插入 {inserted_rows} 行数据")
            return True
            
        except Error as e:
            logger.error(f"加载CSV数据失败: {e}")
            self.connection.rollback()
            return False
        except Exception as e:
            logger.error(f"处理CSV数据时发生错误: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def preprocess_data(self, df):
        """数据预处理"""
        logger.info("开始数据预处理...")
        
        # 显示CSV文件的列名
        logger.info(f"CSV文件列名: {list(df.columns)}")
        
        # 重命名字段以匹配数据库表结构
        column_mapping = {
            'pre_close_price': 'prev_close_price'  # 将pre_close_price重命名为prev_close_price
        }
        df = df.rename(columns=column_mapping)
        
        # 处理日期字段
        date_columns = ['ipo_date', 'trade_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 处理数值字段
        numeric_columns = [
            'open_price', 'high_price', 'low_price', 'close_price', 'prev_close_price',
            'volume', 'amount', 'pct_change', 'turnover_rate', 'pe_ttm', 'pb_ratio',
            'ps_ttm', 'pcf_ttm', 'net_profit', 'revenue', 'total_assets', 'net_assets',
            'eps', 'roe'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 处理字符串字段
        string_columns = [
            'stock_code', 'stock_name', 'listing_status', 'stock_type', 'trade_status',
            'is_st', 'industry_code', 'industry_name'
        ]
        
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).replace('nan', None)
        
        # 移除id列（如果存在），因为数据库会自动生成
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
        
        logger.info("数据预处理完成")
        return df
    
    def get_data_summary(self):
        """获取数据统计信息"""
        if not self.connection:
            logger.error("未连接到数据库")
            return None
            
        try:
            cursor = self.connection.cursor()
            
            # 获取基本统计信息
            summary_queries = {
                '总记录数': "SELECT COUNT(*) FROM stock_daily_data",
                '股票数量': "SELECT COUNT(DISTINCT stock_code) FROM stock_daily_data",
                '日期范围': "SELECT MIN(trade_date), MAX(trade_date) FROM stock_daily_data",
                '行业数量': "SELECT COUNT(DISTINCT industry_code) FROM stock_daily_data WHERE industry_code IS NOT NULL"
            }
            
            summary = {}
            for key, query in summary_queries.items():
                cursor.execute(query)
                result = cursor.fetchone()
                summary[key] = result[0] if len(result) == 1 else result
            
            return summary
            
        except Error as e:
            logger.error(f"获取数据统计信息失败: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

def main():
    """主函数"""
    print("A股金融数据加载器")
    print("=" * 50)
    
    # 创建数据加载器实例
    loader = StockDataLoader(
        host='127.0.0.1',
        database='lwg_database',
        user='root',
        password=''
    )
    
    try:
        # 连接到数据库
        if not loader.connect():
            print("❌ 无法连接到数据库，请检查配置")
            return
        
        # 检查数据表是否存在
        if not loader.check_table_exists():
            print("❌ 数据表不存在，请先创建表")
            return
        
        # 加载CSV数据
        csv_file = "A股金融日线数据/完整A股金融日线数据.csv"
        if os.path.exists(csv_file):
            if loader.load_csv_data(csv_file):
                print("✅ CSV数据加载成功")
                
                # 显示数据统计
                summary = loader.get_data_summary()
                if summary:
                    print("\n📊 数据统计:")
                    for key, value in summary.items():
                        print(f"   - {key}: {value}")
            else:
                print("❌ CSV数据加载失败")
        else:
            print(f"❌ CSV文件不存在: {csv_file}")
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    finally:
        loader.disconnect()

if __name__ == "__main__":
    main()
