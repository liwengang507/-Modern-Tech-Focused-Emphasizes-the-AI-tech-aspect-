#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股上市公司年报数据获取脚本
使用BaoStock获取2020-01-01至今的A股上市公司数据并保存到Excel文件
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import warnings
warnings.filterwarnings('ignore')

class BaoStockDataCollector:
    """基于BaoStock的A股数据收集器"""
    
    def __init__(self):
        """初始化数据收集器"""
        self.lg = None
        
    def login(self):
        """
        登录BaoStock
        
        Returns:
            bool: 登录是否成功
        """
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
        """
        获取A股基本信息
        
        Returns:
            pd.DataFrame: A股基本信息数据
        """
        print("正在获取A股基本信息...")
        try:
            # 获取A股基本信息
            rs = bs.query_stock_basic(code_name="")
            if rs.error_code != '0':
                print(f"获取股票基本信息失败: {rs.error_msg}")
                return None
            
            stock_basic = rs.get_data()
            print(f"获取到 {len(stock_basic)} 只A股股票基本信息")
            
        # 筛选A股（排除科创板、创业板等，只保留主板和中小板）
        a_stocks = stock_basic[
            (stock_basic['type'] == '1') &  # 股票类型为1表示A股
            (stock_basic['status'] == '1')  # 状态为1表示上市
        ].copy()
        
        # 按照IPO日期（上市日期）从小到大排序
        if 'ipoDate' in a_stocks.columns:
            a_stocks = a_stocks.sort_values('ipoDate', ascending=True)
            print(f"已按照IPO日期排序")
        elif 'listDate' in a_stocks.columns:
            a_stocks = a_stocks.sort_values('listDate', ascending=True)
            print(f"已按照上市日期排序")
        
        print(f"筛选出 {len(a_stocks)} 只A股股票")
        return a_stocks
            
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return None
    
    def get_financial_data(self, stock_codes, start_date='2020-01-01', end_date=None):
        """
        获取财务数据
        
        Args:
            stock_codes (list): 股票代码列表
            start_date (str): 开始日期，格式：YYYY-MM-DD
            end_date (str): 结束日期，格式：YYYY-MM-DD，默认为今天
            
        Returns:
            pd.DataFrame: 财务数据
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        print(f"正在获取财务数据，时间范围：{start_date} 到 {end_date}")
        
        all_financial_data = []
        
        for i, code in enumerate(stock_codes):
            try:
                print(f"正在获取股票 {code} 的财务数据 ({i+1}/{len(stock_codes)})")
                
                # 获取利润表数据
                rs_profit = bs.query_profit_data(code=code, year=2020, quarter=4)
                if rs_profit.error_code == '0':
                    profit_data = rs_profit.get_data()
                    if not profit_data.empty:
                        profit_data['data_type'] = '利润表'
                        all_financial_data.append(profit_data)
                
                # 获取2021年数据
                rs_profit_2021 = bs.query_profit_data(code=code, year=2021, quarter=4)
                if rs_profit_2021.error_code == '0':
                    profit_data_2021 = rs_profit_2021.get_data()
                    if not profit_data_2021.empty:
                        profit_data_2021['data_type'] = '利润表'
                        all_financial_data.append(profit_data_2021)
                
                # 获取2022年数据
                rs_profit_2022 = bs.query_profit_data(code=code, year=2022, quarter=4)
                if rs_profit_2022.error_code == '0':
                    profit_data_2022 = rs_profit_2022.get_data()
                    if not profit_data_2022.empty:
                        profit_data_2022['data_type'] = '利润表'
                        all_financial_data.append(profit_data_2022)
                
                # 获取2023年数据
                rs_profit_2023 = bs.query_profit_data(code=code, year=2023, quarter=4)
                if rs_profit_2023.error_code == '0':
                    profit_data_2023 = rs_profit_2023.get_data()
                    if not profit_data_2023.empty:
                        profit_data_2023['data_type'] = '利润表'
                        all_financial_data.append(profit_data_2023)
                
                # 获取资产负债表数据
                rs_balance = bs.query_balance_data(code=code, year=2020, quarter=4)
                if rs_balance.error_code == '0':
                    balance_data = rs_balance.get_data()
                    if not balance_data.empty:
                        balance_data['data_type'] = '资产负债表'
                        all_financial_data.append(balance_data)
                
                # 获取现金流量表数据
                rs_cashflow = bs.query_cash_flow_data(code=code, year=2020, quarter=4)
                if rs_cashflow.error_code == '0':
                    cashflow_data = rs_cashflow.get_data()
                    if not cashflow_data.empty:
                        cashflow_data['data_type'] = '现金流量表'
                        all_financial_data.append(cashflow_data)
                
                # 避免请求过于频繁
                time.sleep(0.1)
                
            except Exception as e:
                print(f"获取股票 {code} 财务数据失败: {e}")
                continue
        
        if all_financial_data:
            # 合并所有财务数据
            combined_data = pd.concat(all_financial_data, ignore_index=True)
            print(f"总共获取到 {len(combined_data)} 条财务数据")
            return combined_data
        else:
            print("未获取到任何财务数据")
            return pd.DataFrame()
    
    def get_daily_data(self, stock_codes, start_date='2020-01-01', end_date=None):
        """
        获取日线数据
        
        Args:
            stock_codes (list): 股票代码列表
            start_date (str): 开始日期
            end_date (str): 结束日期
            
        Returns:
            pd.DataFrame: 日线数据
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        print(f"正在获取日线数据，时间范围：{start_date} 到 {end_date}")
        
        all_daily_data = []
        
        for i, code in enumerate(stock_codes):
            try:
                print(f"正在获取股票 {code} 的日线数据 ({i+1}/{len(stock_codes)})")
                
                # 获取日线数据
                rs = bs.query_history_k_data_plus(
                    code=code,
                    fields="date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                    start_date=start_date,
                    end_date=end_date,
                    frequency="d",
                    adjustflag="3"
                )
                
                if rs.error_code == '0':
                    daily_data = rs.get_data()
                    if not daily_data.empty:
                        all_daily_data.append(daily_data)
                        print(f"获取到 {len(daily_data)} 条日线数据")
                else:
                    print(f"获取股票 {code} 日线数据失败: {rs.error_msg}")
                
                # 避免请求过于频繁
                time.sleep(0.05)
                
            except Exception as e:
                print(f"获取股票 {code} 日线数据失败: {e}")
                continue
        
        if all_daily_data:
            combined_data = pd.concat(all_daily_data, ignore_index=True)
            print(f"总共获取到 {len(combined_data)} 条日线数据")
            return combined_data
        else:
            print("未获取到任何日线数据")
            return pd.DataFrame()
    
    def get_industry_data(self, stock_codes):
        """
        获取行业数据
        
        Args:
            stock_codes (list): 股票代码列表
            
        Returns:
            pd.DataFrame: 行业数据
        """
        print("正在获取行业数据...")
        
        all_industry_data = []
        
        for i, code in enumerate(stock_codes):
            try:
                print(f"正在获取股票 {code} 的行业数据 ({i+1}/{len(stock_codes)})")
                
                # 获取行业数据
                rs = bs.query_stock_industry(code=code)
                if rs.error_code == '0':
                    industry_data = rs.get_data()
                    if not industry_data.empty:
                        all_industry_data.append(industry_data)
                
                time.sleep(0.05)
                
            except Exception as e:
                print(f"获取股票 {code} 行业数据失败: {e}")
                continue
        
        if all_industry_data:
            combined_data = pd.concat(all_industry_data, ignore_index=True)
            print(f"总共获取到 {len(combined_data)} 条行业数据")
            return combined_data
        else:
            print("未获取到任何行业数据")
            return pd.DataFrame()
    
    def save_to_excel(self, data_dict, filename='A股上市公司数据.xlsx'):
        """
        保存数据到Excel文件
        
        Args:
            data_dict (dict): 数据字典，键为工作表名称，值为DataFrame
            filename (str): 文件名
        """
        print(f"正在保存数据到 {filename}...")
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for sheet_name, df in data_dict.items():
                    if not df.empty:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        print(f"已保存 {sheet_name} 工作表，共 {len(df)} 行数据")
                    else:
                        print(f"警告：{sheet_name} 工作表为空")
            
            print(f"数据已成功保存到 {filename}")
            
        except Exception as e:
            print(f"保存Excel文件失败: {e}")
    
    def collect_all_data(self, start_date='2020-01-01', end_date=None):
        """
        收集所有数据
        
        Args:
            start_date (str): 开始日期
            end_date (str): 结束日期
            
        Returns:
            dict: 包含所有数据的字典
        """
        print("开始收集A股上市公司数据...")
        
        # 获取股票基本信息
        stock_basic = self.get_stock_basic_info()
        if stock_basic is None or stock_basic.empty:
            print("无法获取股票基本信息，程序退出")
            return {}
        
        # 获取股票代码列表（限制数量以避免请求过多）
        stock_codes = stock_basic['code'].head(1000).tolist()  # 限制为1000只股票
        
        print(f"将获取 {len(stock_codes)} 只股票的数据")
        
        # 获取财务数据
        financial_data = self.get_financial_data(stock_codes, start_date, end_date)
        
        # 获取日线数据
        daily_data = self.get_daily_data(stock_codes, start_date, end_date)
        
        # 获取行业数据
        industry_data = self.get_industry_data(stock_codes)
        
        # 组织数据
        data_dict = {
            '股票基本信息': stock_basic,
            '财务数据': financial_data,
            '日线数据': daily_data,
            '行业数据': industry_data
        }
        
        return data_dict

def main():
    """主函数"""
    print("A股上市公司年报数据获取程序 (基于BaoStock)")
    print("=" * 60)
    
    try:
        # 创建数据收集器
        collector = BaoStockDataCollector()
        
        # 登录BaoStock
        if not collector.login():
            print("无法登录BaoStock，程序退出")
            return
        
        # 收集所有数据
        data_dict = collector.collect_all_data(
            start_date='2020-01-01',
            end_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        if data_dict:
            # 保存到Excel文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'A股上市公司数据_BaoStock_{timestamp}.xlsx'
            collector.save_to_excel(data_dict, filename)
            
            # 显示数据统计
            print("\n数据统计：")
            print("-" * 40)
            for sheet_name, df in data_dict.items():
                print(f"{sheet_name}: {len(df)} 行数据")
        else:
            print("未获取到任何数据")
            
    except Exception as e:
        print(f"程序执行失败: {e}")
    finally:
        # 登出BaoStock
        collector.logout()

if __name__ == "__main__":
    main()
