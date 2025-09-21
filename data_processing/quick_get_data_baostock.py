#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速获取A股数据脚本 (基于BaoStock)
简化版本，适合快速获取数据
"""

import baostock as bs
import pandas as pd
from datetime import datetime
import time

def quick_get_stock_data():
    """
    快速获取A股数据
    """
    print("正在登录BaoStock...")
    
    # 登录BaoStock
    lg = bs.login()
    if lg.error_code != '0':
        print(f"BaoStock登录失败: {lg.error_msg}")
        return
    
    print("BaoStock登录成功")
    
    try:
        print("正在获取A股股票基本信息...")
        
        # 获取A股基本信息
        rs = bs.query_stock_basic(code_name="")
        if rs.error_code != '0':
            print(f"获取股票基本信息失败: {rs.error_msg}")
            return
        
        stock_basic = rs.get_data()
        print(f"获取到 {len(stock_basic)} 只股票基本信息")
        
        # 筛选A股（限制数量）
        a_stocks = stock_basic[
            (stock_basic['type'] == '1') & 
            (stock_basic['status'] == '1')
        ].head(100).copy()  # 只取前100只股票
        
        print(f"筛选出 {len(a_stocks)} 只A股股票")
        
        # 获取前10只股票的日线数据作为示例
        sample_codes = a_stocks['code'].head(10).tolist()
        
        print("正在获取日线数据...")
        daily_data_list = []
        
        for i, code in enumerate(sample_codes):
            try:
                print(f"正在获取股票 {code} 的日线数据 ({i+1}/{len(sample_codes)})")
                
                # 获取最近一年的日线数据
                rs_daily = bs.query_history_k_data_plus(
                    code=code,
                    fields="date,code,open,high,low,close,preclose,volume,amount,pctChg",
                    start_date="2024-01-01",
                    end_date="2024-12-31",
                    frequency="d",
                    adjustflag="3"
                )
                
                if rs_daily.error_code == '0':
                    daily_data = rs_daily.get_data()
                    if not daily_data.empty:
                        daily_data_list.append(daily_data)
                        print(f"获取到 {len(daily_data)} 条日线数据")
                
                time.sleep(0.1)  # 避免请求过快
                
            except Exception as e:
                print(f"获取股票 {code} 日线数据失败: {e}")
                continue
        
        # 合并日线数据
        if daily_data_list:
            all_daily_data = pd.concat(daily_data_list, ignore_index=True)
            print(f"总共获取到 {len(all_daily_data)} 条日线数据")
        else:
            all_daily_data = pd.DataFrame()
        
        # 获取财务数据示例
        print("正在获取财务数据...")
        financial_data_list = []
        
        for i, code in enumerate(sample_codes[:5]):  # 只获取前5只股票的财务数据
            try:
                print(f"正在获取股票 {code} 的财务数据 ({i+1}/5)")
                
                # 获取2023年利润表数据
                rs_profit = bs.query_profit_data(code=code, year=2023, quarter=4)
                if rs_profit.error_code == '0':
                    profit_data = rs_profit.get_data()
                    if not profit_data.empty:
                        profit_data['data_type'] = '利润表'
                        financial_data_list.append(profit_data)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"获取股票 {code} 财务数据失败: {e}")
                continue
        
        # 合并财务数据
        if financial_data_list:
            all_financial_data = pd.concat(financial_data_list, ignore_index=True)
            print(f"总共获取到 {len(all_financial_data)} 条财务数据")
        else:
            all_financial_data = pd.DataFrame()
        
        # 保存到Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'A股数据示例_BaoStock_{timestamp}.xlsx'
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            a_stocks.to_excel(writer, sheet_name='A股基本信息', index=False)
            if not all_daily_data.empty:
                all_daily_data.to_excel(writer, sheet_name='日线数据', index=False)
            if not all_financial_data.empty:
                all_financial_data.to_excel(writer, sheet_name='财务数据', index=False)
        
        print(f"数据已保存到 {filename}")
        print(f"A股基本信息: {len(a_stocks)} 行")
        print(f"日线数据: {len(all_daily_data)} 行")
        print(f"财务数据: {len(all_financial_data)} 行")
        
    except Exception as e:
        print(f"获取数据失败: {e}")
    finally:
        # 登出BaoStock
        bs.logout()
        print("已登出BaoStock")

def main():
    """主函数"""
    print("A股数据快速获取程序 (基于BaoStock)")
    print("=" * 50)
    print("注意：BaoStock是免费的数据接口，无需注册")
    print("=" * 50)
    
    quick_get_stock_data()

if __name__ == "__main__":
    main()
