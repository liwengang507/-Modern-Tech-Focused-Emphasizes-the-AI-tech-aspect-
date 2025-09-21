#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据关系检查脚本
检查A股基本信息与日线数据之间的一一对应关系
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataRelationshipChecker:
    """数据关系检查器"""
    
    def __init__(self, excel_file):
        """
        初始化检查器
        
        Args:
            excel_file (str): Excel文件路径
        """
        self.excel_file = excel_file
        self.basic_data = None
        self.daily_data = None
        
    def load_data(self):
        """加载数据"""
        print(f"正在加载数据文件: {self.excel_file}")
        
        try:
            # 读取Excel文件
            excel_data = pd.read_excel(self.excel_file, sheet_name=None, engine='openpyxl')
            
            # 获取股票基本信息
            if '股票基本信息' in excel_data:
                self.basic_data = excel_data['股票基本信息']
                print(f"股票基本信息: {len(self.basic_data)} 行")
            else:
                print("未找到股票基本信息工作表")
            
            # 获取日线数据
            if '日线数据' in excel_data:
                self.daily_data = excel_data['日线数据']
                print(f"日线数据: {len(self.daily_data)} 行")
            else:
                print("未找到日线数据工作表")
                
        except Exception as e:
            print(f"加载数据失败: {e}")
    
    def check_basic_data_structure(self):
        """检查股票基本信息结构"""
        if self.basic_data is None:
            return
        
        print("\n=== 股票基本信息结构分析 ===")
        print(f"数据行数: {len(self.basic_data)}")
        print(f"数据列数: {len(self.basic_data.columns)}")
        print("列名:", list(self.basic_data.columns))
        
        # 检查股票代码
        if 'code' in self.basic_data.columns:
            unique_codes = self.basic_data['code'].nunique()
            total_codes = len(self.basic_data['code'])
            print(f"唯一股票代码数量: {unique_codes}")
            print(f"总股票代码数量: {total_codes}")
            print(f"是否有重复: {'是' if unique_codes < total_codes else '否'}")
            
            # 显示前几个股票代码
            print("前10个股票代码:")
            print(self.basic_data['code'].head(10).tolist())
        
        # 检查IPO日期
        date_columns = ['ipoDate', 'listDate', '上市日期', 'list_date']
        for col in date_columns:
            if col in self.basic_data.columns:
                print(f"IPO日期列: {col}")
                print(f"日期范围: {self.basic_data[col].min()} 到 {self.basic_data[col].max()}")
                break
    
    def check_daily_data_structure(self):
        """检查日线数据结构"""
        if self.daily_data is None:
            return
        
        print("\n=== 日线数据结构分析 ===")
        print(f"数据行数: {len(self.daily_data)}")
        print(f"数据列数: {len(self.daily_data.columns)}")
        print("列名:", list(self.daily_data.columns))
        
        # 检查股票代码
        if 'code' in self.daily_data.columns:
            unique_codes = self.daily_data['code'].nunique()
            total_records = len(self.daily_data)
            print(f"唯一股票代码数量: {unique_codes}")
            print(f"总交易记录数量: {total_records}")
            print(f"平均每只股票记录数: {total_records / unique_codes:.2f}")
            
            # 显示前几个股票代码
            print("前10个股票代码:")
            print(self.daily_data['code'].head(10).tolist())
        
        # 检查日期范围
        if 'date' in self.daily_data.columns:
            print(f"交易日期范围: {self.daily_data['date'].min()} 到 {self.daily_data['date'].max()}")
    
    def check_relationship(self):
        """检查基本信息与日线数据的关系"""
        if self.basic_data is None or self.daily_data is None:
            print("缺少必要的数据，无法进行关系分析")
            return
        
        print("\n=== 数据关系分析 ===")
        
        # 获取基本信息中的股票代码
        basic_codes = set(self.basic_data['code'].unique())
        print(f"基本信息中的股票代码数量: {len(basic_codes)}")
        
        # 获取日线数据中的股票代码
        daily_codes = set(self.daily_data['code'].unique())
        print(f"日线数据中的股票代码数量: {len(daily_codes)}")
        
        # 计算交集和差集
        common_codes = basic_codes.intersection(daily_codes)
        only_in_basic = basic_codes - daily_codes
        only_in_daily = daily_codes - basic_codes
        
        print(f"同时存在于两个数据集中的股票代码数量: {len(common_codes)}")
        print(f"仅在基本信息中的股票代码数量: {len(only_in_basic)}")
        print(f"仅在日线数据中的股票代码数量: {len(only_in_daily)}")
        
        # 计算覆盖率
        coverage_rate = len(common_codes) / len(basic_codes) * 100
        print(f"日线数据对基本信息的覆盖率: {coverage_rate:.2f}%")
        
        # 显示仅在基本信息中的股票代码（前10个）
        if only_in_basic:
            print(f"\n仅在基本信息中的股票代码（前10个）:")
            print(list(only_in_basic)[:10])
        
        # 显示仅在日线数据中的股票代码（前10个）
        if only_in_daily:
            print(f"\n仅在日线数据中的股票代码（前10个）:")
            print(list(only_in_daily)[:10])
        
        return {
            'basic_codes': basic_codes,
            'daily_codes': daily_codes,
            'common_codes': common_codes,
            'only_in_basic': only_in_basic,
            'only_in_daily': only_in_daily,
            'coverage_rate': coverage_rate
        }
    
    def analyze_daily_data_coverage(self):
        """分析日线数据的覆盖情况"""
        if self.basic_data is None or self.daily_data is None:
            return
        
        print("\n=== 日线数据覆盖情况分析 ===")
        
        # 获取共同股票代码
        basic_codes = set(self.basic_data['code'].unique())
        daily_codes = set(self.daily_data['code'].unique())
        common_codes = basic_codes.intersection(daily_codes)
        
        if not common_codes:
            print("没有共同的股票代码，无法进行覆盖分析")
            return
        
        # 分析每只股票的日线数据记录数
        daily_counts = self.daily_data['code'].value_counts()
        
        print(f"共同股票代码数量: {len(common_codes)}")
        print(f"日线数据记录数统计:")
        print(f"  最少记录数: {daily_counts.min()}")
        print(f"  最多记录数: {daily_counts.max()}")
        print(f"  平均记录数: {daily_counts.mean():.2f}")
        print(f"  中位数记录数: {daily_counts.median():.2f}")
        
        # 显示记录数最少的股票
        print(f"\n记录数最少的5只股票:")
        min_stocks = daily_counts.nsmallest(5)
        for code, count in min_stocks.items():
            print(f"  {code}: {count} 条记录")
        
        # 显示记录数最多的股票
        print(f"\n记录数最多的5只股票:")
        max_stocks = daily_counts.nlargest(5)
        for code, count in max_stocks.items():
            print(f"  {code}: {count} 条记录")
    
    def generate_summary_report(self):
        """生成汇总报告"""
        print("\n" + "="*60)
        print("数据关系检查汇总报告")
        print("="*60)
        
        # 检查数据结构
        self.check_basic_data_structure()
        self.check_daily_data_structure()
        
        # 检查关系
        relationship = self.check_relationship()
        
        # 分析覆盖情况
        self.analyze_daily_data_coverage()
        
        # 结论
        print("\n=== 结论 ===")
        if relationship:
            if relationship['coverage_rate'] > 90:
                print("✅ 数据关系良好：日线数据对基本信息的覆盖率超过90%")
            elif relationship['coverage_rate'] > 70:
                print("⚠️  数据关系一般：日线数据对基本信息的覆盖率在70%-90%之间")
            else:
                print("❌ 数据关系较差：日线数据对基本信息的覆盖率低于70%")
            
            print(f"📊 具体覆盖率: {relationship['coverage_rate']:.2f}%")
            print(f"📈 基本信息股票数量: {len(relationship['basic_codes'])}")
            print(f"📈 日线数据股票数量: {len(relationship['daily_codes'])}")
            print(f"📈 共同股票数量: {len(relationship['common_codes'])}")

def main():
    """主函数"""
    print("A股数据关系检查程序")
    print("=" * 50)
    
    # 使用最新的汇总文件
    excel_file = "A股数据汇总_按IPO排序_20250920_214629.xlsx"
    
    # 创建检查器
    checker = DataRelationshipChecker(excel_file)
    
    # 加载数据
    checker.load_data()
    
    # 生成汇总报告
    checker.generate_summary_report()

if __name__ == "__main__":
    main()

