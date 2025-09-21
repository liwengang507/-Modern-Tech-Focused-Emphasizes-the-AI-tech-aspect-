#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终A股数据获取脚本
获取完整的A股数据，确保每只股票都有日线记录，保存到指定文件夹
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import glob
import warnings
warnings.filterwarnings('ignore')

class FinalStockDataCollector:
    """最终A股数据收集器"""
    
    def __init__(self):
        """初始化数据收集器"""
        self.lg = None
        self.complete_data = []
        self.output_dir = "A股金融日线数据"
        
    def create_output_directory(self):
        """创建输出目录"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建输出目录: {self.output_dir}")
        else:
            print(f"输出目录已存在: {self.output_dir}")
    
    def login(self):
        """登录BaoStock"""
        print("正在登录BaoStock...")
        try:
            self.lg = bs.login()
            if self.lg.error_code == '0':
                print("BaoStock登录成功")
                return True
            else:
                print(f"BaoStock登录失败: {self.lg.error_msg}")
                return False
        except Exception as e:
            print(f"BaoStock登录异常: {e}")
            return False
    
    def logout(self):
        """登出BaoStock"""
        if self.lg:
            bs.logout()
            print("已登出BaoStock")
    
    def get_stock_basic_info(self):
        """获取A股基本信息"""
        print("正在获取A股基本信息...")
        try:
            rs = bs.query_stock_basic(code_name="")
            if rs.error_code != '0':
                print(f"获取股票基本信息失败: {rs.error_msg}")
                return None
            
            stock_basic = rs.get_data()
            print(f"获取到 {len(stock_basic)} 只A股股票基本信息")
            
            # 筛选A股
            a_stocks = stock_basic[
                (stock_basic['type'] == '1') & 
                (stock_basic['status'] == '1')
            ].copy()
            
            # 按IPO日期排序
            if 'ipoDate' in a_stocks.columns:
                a_stocks['ipoDate'] = pd.to_datetime(a_stocks['ipoDate'], errors='coerce')
                a_stocks = a_stocks.sort_values('ipoDate', ascending=True)
            
            print(f"筛选出 {len(a_stocks)} 只A股股票")
            return a_stocks
            
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return None
    
    def get_daily_data_for_stock(self, stock_code, start_date='2020-01-01', end_date=None):
        """获取单只股票的日线数据"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            rs = bs.query_history_k_data_plus(
                code=stock_code,
                fields="date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3"
            )
            
            if rs.error_code == '0':
                daily_data = rs.get_data()
                if not daily_data.empty:
                    return daily_data
            return pd.DataFrame()
            
        except Exception as e:
            print(f"获取股票 {stock_code} 日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_financial_data_for_stock(self, stock_code):
        """获取单只股票的财务数据"""
        financial_data = []
        
        try:
            # 获取2023年的利润表数据
            rs_profit = bs.query_profit_data(code=stock_code, year=2023, quarter=4)
            if rs_profit.error_code == '0':
                profit_data = rs_profit.get_data()
                if not profit_data.empty:
                    financial_data.append(profit_data)
            
            time.sleep(0.05)  # 避免请求过快
            
        except Exception as e:
            print(f"获取股票 {stock_code} 财务数据失败: {e}")
        
        if financial_data:
            return pd.concat(financial_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def get_industry_data_for_stock(self, stock_code):
        """获取单只股票的行业数据"""
        try:
            rs = bs.query_stock_industry(code=stock_code)
            if rs.error_code == '0':
                industry_data = rs.get_data()
                if not industry_data.empty:
                    return industry_data
            return pd.DataFrame()
            
        except Exception as e:
            print(f"获取股票 {stock_code} 行业数据失败: {e}")
            return pd.DataFrame()
    
    def process_stock_data(self, stock_info):
        """处理单只股票的完整数据"""
        stock_code = stock_info['code']
        stock_name = stock_info['code_name']
        ipo_date = stock_info['ipoDate']
        
        print(f"正在处理股票: {stock_code} ({stock_name})")
        
        # 获取日线数据
        daily_data = self.get_daily_data_for_stock(stock_code)
        
        # 检查是否有日线数据
        if daily_data.empty:
            print(f"  警告: 股票 {stock_code} 没有日线数据，跳过")
            return False
        
        # 获取财务数据
        financial_data = self.get_financial_data_for_stock(stock_code)
        
        # 获取行业数据
        industry_data = self.get_industry_data_for_stock(stock_code)
        
        # 整合数据
        for _, daily_row in daily_data.iterrows():
            record = {
                # 基本信息
                '股票代码': stock_code,
                '股票名称': stock_name,
                'IPO日期': ipo_date,
                '上市状态': stock_info['status'],
                '股票类型': stock_info['type'],
                
                # 日线数据
                '交易日期': daily_row['date'],
                '开盘价': daily_row['open'],
                '最高价': daily_row['high'],
                '最低价': daily_row['low'],
                '收盘价': daily_row['close'],
                '前收盘价': daily_row['preclose'],
                '成交量': daily_row['volume'],
                '成交额': daily_row['amount'],
                '涨跌幅': daily_row['pctChg'],
                '换手率': daily_row.get('turn', ''),
                '交易状态': daily_row.get('tradestatus', ''),
                '市盈率TTM': daily_row.get('peTTM', ''),
                '市净率': daily_row.get('pbMRQ', ''),
                '市销率TTM': daily_row.get('psTTM', ''),
                '市现率TTM': daily_row.get('pcfNcfTTM', ''),
                '是否ST': daily_row.get('isST', ''),
                
                # 财务数据
                '净利润': '',
                '营业收入': '',
                '总资产': '',
                '净资产': '',
                '每股收益': '',
                '净资产收益率': '',
                
                # 行业数据
                '行业分类': '',
                '行业名称': '',
            }
            
            # 添加财务数据
            if not financial_data.empty:
                latest = financial_data.iloc[0]
                record['净利润'] = latest.get('netProfit', '')
                record['营业收入'] = latest.get('MBRevenue', '')
                record['总资产'] = latest.get('totalAssets', '')
                record['净资产'] = latest.get('netAssets', '')
                record['每股收益'] = latest.get('epsTTM', '')
                record['净资产收益率'] = latest.get('roeAvg', '')
            
            # 添加行业数据
            if not industry_data.empty:
                industry = industry_data.iloc[0]
                record['行业分类'] = industry.get('industry', '')
                record['行业名称'] = industry.get('industryName', '')
            
            self.complete_data.append(record)
        
        print(f"  处理完成，共 {len(daily_data)} 条日线记录")
        return True
    
    def collect_complete_data(self, max_stocks=200):
        """收集完整数据"""
        print("开始收集完整A股数据...")
        print("确保每只股票都有日线记录...")
        
        # 获取股票基本信息
        stock_basic = self.get_stock_basic_info()
        if stock_basic is None or stock_basic.empty:
            print("无法获取股票基本信息，程序退出")
            return
        
        # 限制股票数量
        limited_stocks = stock_basic.head(max_stocks)
        print(f"将处理前 {len(limited_stocks)} 只股票")
        
        successful_stocks = 0
        failed_stocks = 0
        
        # 处理每只股票
        for i, (_, stock_info) in enumerate(limited_stocks.iterrows()):
            print(f"\n进度: {i+1}/{len(limited_stocks)}")
            
            if self.process_stock_data(stock_info):
                successful_stocks += 1
            else:
                failed_stocks += 1
            
            # 每处理10只股票显示一次进度
            if (i + 1) % 10 == 0:
                print(f"已处理 {i+1} 只股票，成功: {successful_stocks}, 失败: {failed_stocks}, 当前总记录数: {len(self.complete_data)}")
        
        print(f"\n数据收集完成:")
        print(f"成功处理股票: {successful_stocks} 只")
        print(f"失败股票: {failed_stocks} 只")
        print(f"总记录数: {len(self.complete_data)} 条")
        
        return successful_stocks > 0
    
    def save_to_excel(self, filename='完整A股金融日线数据.xlsx'):
        """保存数据到Excel文件"""
        if not self.complete_data:
            print("没有数据可保存")
            return False
        
        filepath = os.path.join(self.output_dir, filename)
        print(f"正在保存数据到 {filepath}...")
        
        try:
            # 转换为DataFrame
            df = pd.DataFrame(self.complete_data)
            
            # 保存到Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='A股金融日线数据', index=False)
            
            print(f"数据已成功保存到 {filepath}")
            print(f"共保存 {len(df)} 条记录，{len(df.columns)} 个字段")
            
            # 显示数据统计
            print("\n数据统计：")
            print(f"股票数量: {df['股票代码'].nunique()}")
            print(f"交易日期范围: {df['交易日期'].min()} 到 {df['交易日期'].max()}")
            print(f"平均每只股票记录数: {len(df) / df['股票代码'].nunique():.2f}")
            
            return True
            
        except Exception as e:
            print(f"保存Excel文件失败: {e}")
            return False
    
    def cleanup_old_files(self):
        """清理旧的Excel文件"""
        print("\n正在清理旧的Excel文件...")
        
        # 查找所有Excel文件
        excel_files = glob.glob("*.xlsx")
        # 排除临时文件
        excel_files = [f for f in excel_files if not f.startswith("~$")]
        
        deleted_count = 0
        for file in excel_files:
            try:
                os.remove(file)
                print(f"已删除: {file}")
                deleted_count += 1
            except Exception as e:
                print(f"删除文件 {file} 失败: {e}")
        
        print(f"共删除 {deleted_count} 个旧文件")

def main():
    """主函数"""
    print("最终A股数据获取程序")
    print("=" * 60)
    print("特点：确保每只股票都有日线记录，保存到指定文件夹，清理旧文件")
    print("=" * 60)
    
    try:
        # 创建数据收集器
        collector = FinalStockDataCollector()
        
        # 创建输出目录
        collector.create_output_directory()
        
        # 登录BaoStock
        if not collector.login():
            print("无法登录BaoStock，程序退出")
            return
        
        # 收集完整数据
        if collector.collect_complete_data(max_stocks=200):
            # 保存数据
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'完整A股金融日线数据_{timestamp}.xlsx'
            
            if collector.save_to_excel(filename):
                print(f"\n✅ 数据获取成功！文件保存在: {collector.output_dir}/{filename}")
                
                # 清理旧文件
                collector.cleanup_old_files()
            else:
                print("❌ 数据保存失败")
        else:
            print("❌ 数据获取失败")
        
    except Exception as e:
        print(f"程序执行失败: {e}")
    finally:
        # 登出BaoStock
        collector.logout()

if __name__ == "__main__":
    main()

