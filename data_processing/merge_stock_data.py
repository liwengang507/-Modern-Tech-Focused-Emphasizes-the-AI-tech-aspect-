#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据汇总脚本
将多个Excel文件中的数据进行汇总，按IPO日期排序，保存到新的Excel文件中
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class StockDataMerger:
    """A股数据汇总器"""
    
    def __init__(self):
        """初始化数据汇总器"""
        self.all_basic_data = []
        self.all_daily_data = []
        self.all_financial_data = []
        self.all_industry_data = []
    
    def find_excel_files(self, directory="."):
        """
        查找目录中的所有Excel文件
        
        Args:
            directory (str): 目录路径
            
        Returns:
            list: Excel文件路径列表
        """
        excel_files = glob.glob(os.path.join(directory, "*.xlsx"))
        # 排除临时文件
        excel_files = [f for f in excel_files if not f.startswith("~$")]
        print(f"找到 {len(excel_files)} 个Excel文件:")
        for file in excel_files:
            print(f"  - {os.path.basename(file)}")
        return excel_files
    
    def read_excel_file(self, file_path):
        """
        读取Excel文件中的所有工作表
        
        Args:
            file_path (str): Excel文件路径
            
        Returns:
            dict: 工作表数据字典
        """
        print(f"正在读取文件: {os.path.basename(file_path)}")
        
        try:
            # 读取所有工作表
            excel_data = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
            print(f"  包含工作表: {list(excel_data.keys())}")
            
            return excel_data
        except Exception as e:
            print(f"  读取文件失败: {e}")
            return {}
    
    def merge_basic_data(self, data_dict):
        """
        合并股票基本信息数据
        
        Args:
            data_dict (dict): 数据字典
        """
        # 查找包含基本信息的工作表
        basic_sheets = []
        for sheet_name, df in data_dict.items():
            if any(keyword in sheet_name.lower() for keyword in ['基本信息', 'basic', '股票信息']):
                if not df.empty:
                    basic_sheets.append(df)
                    print(f"  找到基本信息工作表: {sheet_name}, 共 {len(df)} 行")
        
        if basic_sheets:
            # 合并所有基本信息数据
            merged_basic = pd.concat(basic_sheets, ignore_index=True)
            # 去重
            merged_basic = merged_basic.drop_duplicates(subset=['code'], keep='first')
            self.all_basic_data.append(merged_basic)
            print(f"  合并基本信息数据: {len(merged_basic)} 行")
    
    def merge_daily_data(self, data_dict):
        """
        合并日线数据
        
        Args:
            data_dict (dict): 数据字典
        """
        # 查找包含日线数据的工作表
        daily_sheets = []
        for sheet_name, df in data_dict.items():
            if any(keyword in sheet_name.lower() for keyword in ['日线', 'daily', '交易']):
                if not df.empty:
                    daily_sheets.append(df)
                    print(f"  找到日线数据工作表: {sheet_name}, 共 {len(df)} 行")
        
        if daily_sheets:
            # 合并所有日线数据
            merged_daily = pd.concat(daily_sheets, ignore_index=True)
            self.all_daily_data.append(merged_daily)
            print(f"  合并日线数据: {len(merged_daily)} 行")
    
    def merge_financial_data(self, data_dict):
        """
        合并财务数据
        
        Args:
            data_dict (dict): 数据字典
        """
        # 查找包含财务数据的工作表
        financial_sheets = []
        for sheet_name, df in data_dict.items():
            if any(keyword in sheet_name.lower() for keyword in ['财务', 'financial', '利润', 'balance', 'cashflow']):
                if not df.empty:
                    financial_sheets.append(df)
                    print(f"  找到财务数据工作表: {sheet_name}, 共 {len(df)} 行")
        
        if financial_sheets:
            # 合并所有财务数据
            merged_financial = pd.concat(financial_sheets, ignore_index=True)
            self.all_financial_data.append(merged_financial)
            print(f"  合并财务数据: {len(merged_financial)} 行")
    
    def merge_industry_data(self, data_dict):
        """
        合并行业数据
        
        Args:
            data_dict (dict): 数据字典
        """
        # 查找包含行业数据的工作表
        industry_sheets = []
        for sheet_name, df in data_dict.items():
            if any(keyword in sheet_name.lower() for keyword in ['行业', 'industry']):
                if not df.empty:
                    industry_sheets.append(df)
                    print(f"  找到行业数据工作表: {sheet_name}, 共 {len(df)} 行")
        
        if industry_sheets:
            # 合并所有行业数据
            merged_industry = pd.concat(industry_sheets, ignore_index=True)
            self.all_industry_data.append(merged_industry)
            print(f"  合并行业数据: {len(merged_industry)} 行")
    
    def process_file(self, file_path):
        """
        处理单个Excel文件
        
        Args:
            file_path (str): Excel文件路径
        """
        data_dict = self.read_excel_file(file_path)
        if not data_dict:
            return
        
        # 合并各类数据
        self.merge_basic_data(data_dict)
        self.merge_daily_data(data_dict)
        self.merge_financial_data(data_dict)
        self.merge_industry_data(data_dict)
    
    def sort_by_ipo_date(self, df, date_columns=['ipoDate', 'listDate', '上市日期']):
        """
        按照IPO日期排序
        
        Args:
            df (pd.DataFrame): 数据框
            date_columns (list): 可能的日期列名
            
        Returns:
            pd.DataFrame: 排序后的数据框
        """
        for col in date_columns:
            if col in df.columns:
                print(f"  按照 {col} 排序")
                # 转换日期格式
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df = df.sort_values(col, ascending=True)
                break
        return df
    
    def merge_all_data(self):
        """
        合并所有数据
        
        Returns:
            dict: 合并后的数据字典
        """
        print("\n开始合并所有数据...")
        
        merged_data = {}
        
        # 合并股票基本信息
        if self.all_basic_data:
            print("合并股票基本信息...")
            basic_merged = pd.concat(self.all_basic_data, ignore_index=True)
            # 去重
            basic_merged = basic_merged.drop_duplicates(subset=['code'], keep='first')
            # 按IPO日期排序
            basic_merged = self.sort_by_ipo_date(basic_merged)
            merged_data['股票基本信息'] = basic_merged
            print(f"股票基本信息: {len(basic_merged)} 行")
        
        # 合并日线数据
        if self.all_daily_data:
            print("合并日线数据...")
            daily_merged = pd.concat(self.all_daily_data, ignore_index=True)
            # 按日期排序
            if 'date' in daily_merged.columns:
                daily_merged['date'] = pd.to_datetime(daily_merged['date'], errors='coerce')
                daily_merged = daily_merged.sort_values(['code', 'date'], ascending=[True, True])
            merged_data['日线数据'] = daily_merged
            print(f"日线数据: {len(daily_merged)} 行")
        
        # 合并财务数据
        if self.all_financial_data:
            print("合并财务数据...")
            financial_merged = pd.concat(self.all_financial_data, ignore_index=True)
            # 按股票代码和统计日期排序
            if 'statDate' in financial_merged.columns:
                financial_merged['statDate'] = pd.to_datetime(financial_merged['statDate'], errors='coerce')
                financial_merged = financial_merged.sort_values(['code', 'statDate'], ascending=[True, True])
            merged_data['财务数据'] = financial_merged
            print(f"财务数据: {len(financial_merged)} 行")
        
        # 合并行业数据
        if self.all_industry_data:
            print("合并行业数据...")
            industry_merged = pd.concat(self.all_industry_data, ignore_index=True)
            # 去重
            industry_merged = industry_merged.drop_duplicates(subset=['code'], keep='first')
            merged_data['行业数据'] = industry_merged
            print(f"行业数据: {len(industry_merged)} 行")
        
        return merged_data
    
    def save_merged_data(self, merged_data, output_filename):
        """
        保存合并后的数据
        
        Args:
            merged_data (dict): 合并后的数据
            output_filename (str): 输出文件名
        """
        print(f"\n正在保存合并后的数据到 {output_filename}...")
        
        try:
            with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
                for sheet_name, df in merged_data.items():
                    if not df.empty:
                        # 如果数据量过大，分页保存
                        if len(df) > 100000:  # 如果超过10万行，分页保存
                            print(f"数据量过大，分页保存 {sheet_name}")
                            # 每页保存10万行
                            for i in range(0, len(df), 100000):
                                page_num = i // 100000 + 1
                                page_data = df.iloc[i:i+100000]
                                page_sheet_name = f"{sheet_name}_第{page_num}页"
                                page_data.to_excel(writer, sheet_name=page_sheet_name, index=False)
                                print(f"已保存 {page_sheet_name}，共 {len(page_data)} 行数据")
                        else:
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                            print(f"已保存 {sheet_name} 工作表，共 {len(df)} 行数据")
                    else:
                        print(f"警告：{sheet_name} 工作表为空")
            
            print(f"数据已成功保存到 {output_filename}")
            
        except Exception as e:
            print(f"保存Excel文件失败: {e}")
    
    def run(self):
        """运行数据汇总"""
        print("A股数据汇总程序")
        print("=" * 50)
        
        # 查找所有Excel文件
        excel_files = self.find_excel_files()
        
        if not excel_files:
            print("未找到任何Excel文件")
            return
        
        # 处理每个Excel文件
        for file_path in excel_files:
            print(f"\n处理文件: {os.path.basename(file_path)}")
            self.process_file(file_path)
        
        # 合并所有数据
        merged_data = self.merge_all_data()
        
        if not merged_data:
            print("未找到任何数据")
            return
        
        # 保存合并后的数据
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'A股数据汇总_按IPO排序_{timestamp}.xlsx'
        self.save_merged_data(merged_data, output_filename)
        
        # 显示数据统计
        print("\n最终数据统计：")
        print("-" * 50)
        for sheet_name, df in merged_data.items():
            print(f"{sheet_name}: {len(df)} 行数据")

def main():
    """主函数"""
    merger = StockDataMerger()
    merger.run()

if __name__ == "__main__":
    main()
