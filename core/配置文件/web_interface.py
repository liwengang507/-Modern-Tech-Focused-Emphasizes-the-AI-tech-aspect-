#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股金融数据Web交互界面
提供用户友好的数据查询和分析功能
"""

from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import mysql.connector
from mysql.connector import Error
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
from stock_analyzer import StockAnalyzer

app = Flask(__name__)

# 全局分析器实例
analyzer = None

def init_analyzer():
    """初始化分析器"""
    global analyzer
    analyzer = StockAnalyzer(
        host='localhost',
        database='stock_analysis',
        user='root',
        password=''  # 请根据实际情况修改密码
    )
    return analyzer.connect()

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks():
    """获取股票列表API"""
    try:
        if not analyzer or not analyzer.connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        stocks = analyzer.get_stock_list()
        if stocks is not None:
            # 转换为JSON格式
            result = stocks.to_dict('records')
            return jsonify({'data': result})
        else:
            return jsonify({'error': '获取股票列表失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<stock_code>')
def get_stock_data(stock_code):
    """获取股票数据API"""
    try:
        if not analyzer or not analyzer.connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 获取股票数据
        df = analyzer.get_stock_data(stock_code, start_date, end_date)
        
        if df is not None and not df.empty:
            # 转换为JSON格式
            result = df.to_dict('records')
            return jsonify({'data': result})
        else:
            return jsonify({'error': '未找到股票数据'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<stock_code>/analysis')
def get_stock_analysis(stock_code):
    """获取股票分析API"""
    try:
        if not analyzer or not analyzer.connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        analysis = analyzer.analyze_stock_performance(stock_code)
        if analysis:
            return jsonify({'data': analysis})
        else:
            return jsonify({'error': '股票分析失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-performers')
def get_top_performers():
    """获取表现最佳股票API"""
    try:
        if not analyzer or not analyzer.connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        limit = request.args.get('limit', 10, type=int)
        order_by = request.args.get('order_by', 'avg_change')
        
        top_stocks = analyzer.get_top_performers(limit, order_by)
        if top_stocks is not None:
            result = top_stocks.to_dict('records')
            return jsonify({'data': result})
        else:
            return jsonify({'error': '获取表现最佳股票失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/industry-analysis')
def get_industry_analysis():
    """获取行业分析API"""
    try:
        if not analyzer or not analyzer.connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        industry_df = analyzer.get_industry_analysis()
        if industry_df is not None:
            result = industry_df.to_dict('records')
            return jsonify({'data': result})
        else:
            return jsonify({'error': '获取行业分析失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart/<stock_code>')
def get_stock_chart(stock_code):
    """获取股票图表API"""
    try:
        if not analyzer or not analyzer.connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        # 生成图表
        df = analyzer.get_stock_data(stock_code)
        if df is None or df.empty:
            return jsonify({'error': '未找到股票数据'}), 404
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        plt.plot(df['trade_date'], df['close_price'], linewidth=1)
        plt.title(f'{stock_code} 股票走势图')
        plt.ylabel('收盘价 (元)')
        plt.xlabel('日期')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # 转换为base64图片
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({'image': f'data:image/png;base64,{img_base64}'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_stocks():
    """搜索股票API"""
    try:
        if not analyzer or not analyzer.connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        keyword = request.args.get('q', '').strip()
        if not keyword:
            return jsonify({'data': []})
        
        # 搜索股票
        query = """
            SELECT DISTINCT stock_code, stock_name, industry_name
            FROM stock_daily_data 
            WHERE (stock_code LIKE %s OR stock_name LIKE %s)
              AND stock_name IS NOT NULL
            ORDER BY stock_code
            LIMIT 20
        """
        
        search_pattern = f'%{keyword}%'
        df = pd.read_sql(query, analyzer.connection, params=[search_pattern, search_pattern])
        
        result = df.to_dict('records')
        return jsonify({'data': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    """获取数据统计API"""
    try:
        if not analyzer or not analyzer.connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        stats = analyzer.get_data_summary()
        if stats:
            return jsonify({'data': stats})
        else:
            return jsonify({'error': '获取统计数据失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_templates():
    """创建HTML模板"""
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # 主页面模板
    index_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A股金融数据智能分析系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .stat-card h3 {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .stock-card {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        .stock-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .loading {
            text-align: center;
            padding: 20px;
        }
        .error {
            color: #dc3545;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="bi bi-graph-up"></i>
                A股金融数据智能分析系统
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- 统计信息 -->
        <div class="row" id="statistics">
            <div class="col-md-3">
                <div class="stat-card">
                    <h3 id="total-records">-</h3>
                    <p>总记录数</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <h3 id="total-stocks">-</h3>
                    <p>股票数量</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <h3 id="total-industries">-</h3>
                    <p>行业数量</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <h3 id="date-range">-</h3>
                    <p>数据期间</p>
                </div>
            </div>
        </div>

        <!-- 搜索和筛选 -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-search"></i></span>
                    <input type="text" class="form-control" id="searchInput" placeholder="搜索股票代码或名称...">
                </div>
            </div>
            <div class="col-md-6">
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-outline-primary active" onclick="showTab('stocks')">股票列表</button>
                    <button type="button" class="btn btn-outline-primary" onclick="showTab('top-performers')">表现最佳</button>
                    <button type="button" class="btn btn-outline-primary" onclick="showTab('industry')">行业分析</button>
                </div>
            </div>
        </div>

        <!-- 内容区域 -->
        <div id="content">
            <!-- 股票列表 -->
            <div id="stocks-tab" class="tab-content">
                <div class="row" id="stocksList">
                    <div class="loading">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p>正在加载股票数据...</p>
                    </div>
                </div>
            </div>

            <!-- 表现最佳股票 -->
            <div id="top-performers-tab" class="tab-content" style="display: none;">
                <div class="row" id="topPerformersList">
                    <div class="loading">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p>正在加载数据...</p>
                    </div>
                </div>
            </div>

            <!-- 行业分析 -->
            <div id="industry-tab" class="tab-content" style="display: none;">
                <div class="row" id="industryList">
                    <div class="loading">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p>正在加载行业数据...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 股票详情模态框 -->
    <div class="modal fade" id="stockModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="stockModalTitle">股票详情</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="stockDetails">
                        <div class="loading">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">加载中...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentTab = 'stocks';
        let allStocks = [];

        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadStatistics();
            loadStocks();
            loadTopPerformers();
            loadIndustryAnalysis();
            
            // 搜索功能
            document.getElementById('searchInput').addEventListener('input', function(e) {
                const keyword = e.target.value.trim();
                if (keyword.length >= 2) {
                    searchStocks(keyword);
                } else if (currentTab === 'stocks') {
                    displayStocks(allStocks);
                }
            });
        });

        // 加载统计数据
        async function loadStatistics() {
            try {
                const response = await fetch('/api/statistics');
                const data = await response.json();
                
                if (data.data) {
                    document.getElementById('total-records').textContent = data.data['总记录数'] || '-';
                    document.getElementById('total-stocks').textContent = data.data['股票数量'] || '-';
                    document.getElementById('total-industries').textContent = data.data['行业数量'] || '-';
                    
                    const dateRange = data.data['日期范围'];
                    if (dateRange && Array.isArray(dateRange) && dateRange.length === 2) {
                        document.getElementById('date-range').textContent = 
                            `${dateRange[0]} ~ ${dateRange[1]}`.substring(0, 10);
                    }
                }
            } catch (error) {
                console.error('加载统计数据失败:', error);
            }
        }

        // 加载股票列表
        async function loadStocks() {
            try {
                const response = await fetch('/api/stocks');
                const data = await response.json();
                
                if (data.data) {
                    allStocks = data.data;
                    displayStocks(allStocks);
                } else {
                    showError('stocksList', data.error || '加载股票列表失败');
                }
            } catch (error) {
                showError('stocksList', '网络错误: ' + error.message);
            }
        }

        // 显示股票列表
        function displayStocks(stocks) {
            const container = document.getElementById('stocksList');
            if (stocks.length === 0) {
                container.innerHTML = '<div class="col-12"><div class="alert alert-info">未找到股票数据</div></div>';
                return;
            }

            const html = stocks.map(stock => `
                <div class="col-md-6 col-lg-4">
                    <div class="stock-card">
                        <h6>${stock.stock_name || '未知'}</h6>
                        <p class="mb-1"><strong>代码:</strong> ${stock.stock_code}</p>
                        <p class="mb-2"><strong>行业:</strong> ${stock.industry_name || '未知'}</p>
                        <button class="btn btn-sm btn-primary" onclick="showStockDetails('${stock.stock_code}')">
                            <i class="bi bi-eye"></i> 查看详情
                        </button>
                    </div>
                </div>
            `).join('');

            container.innerHTML = html;
        }

        // 搜索股票
        async function searchStocks(keyword) {
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(keyword)}`);
                const data = await response.json();
                
                if (data.data) {
                    displayStocks(data.data);
                }
            } catch (error) {
                console.error('搜索失败:', error);
            }
        }

        // 显示股票详情
        async function showStockDetails(stockCode) {
            const modal = new bootstrap.Modal(document.getElementById('stockModal'));
            document.getElementById('stockModalTitle').textContent = `股票详情 - ${stockCode}`;
            
            const detailsContainer = document.getElementById('stockDetails');
            detailsContainer.innerHTML = '<div class="loading"><div class="spinner-border text-primary" role="status"></div></div>';
            
            modal.show();

            try {
                // 获取股票分析
                const analysisResponse = await fetch(`/api/stock/${stockCode}/analysis`);
                const analysisData = await analysisResponse.json();
                
                // 获取股票图表
                const chartResponse = await fetch(`/api/chart/${stockCode}`);
                const chartData = await chartResponse.json();

                let html = '';
                
                if (analysisData.data) {
                    html += '<div class="row mb-3">';
                    html += '<div class="col-md-6"><h6>基本信息</h6>';
                    html += '<ul class="list-unstyled">';
                    for (const [key, value] of Object.entries(analysisData.data)) {
                        html += `<li><strong>${key}:</strong> ${value}</li>`;
                    }
                    html += '</ul></div>';
                    
                    if (chartData.image) {
                        html += '<div class="col-md-6"><h6>走势图</h6>';
                        html += `<img src="${chartData.image}" class="img-fluid" alt="股票走势图">`;
                        html += '</div>';
                    }
                    html += '</div>';
                }

                detailsContainer.innerHTML = html;
                
            } catch (error) {
                detailsContainer.innerHTML = `<div class="error">加载股票详情失败: ${error.message}</div>`;
            }
        }

        // 加载表现最佳股票
        async function loadTopPerformers() {
            try {
                const response = await fetch('/api/top-performers?limit=20');
                const data = await response.json();
                
                if (data.data) {
                    displayTopPerformers(data.data);
                } else {
                    showError('topPerformersList', data.error || '加载表现最佳股票失败');
                }
            } catch (error) {
                showError('topPerformersList', '网络错误: ' + error.message);
            }
        }

        // 显示表现最佳股票
        function displayTopPerformers(stocks) {
            const container = document.getElementById('topPerformersList');
            if (stocks.length === 0) {
                container.innerHTML = '<div class="col-12"><div class="alert alert-info">未找到数据</div></div>';
                return;
            }

            const html = stocks.map((stock, index) => `
                <div class="col-md-6 col-lg-4">
                    <div class="stock-card">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="badge bg-primary">#${index + 1}</span>
                            <span class="text-success"><strong>${stock.avg_change.toFixed(2)}%</strong></span>
                        </div>
                        <h6>${stock.stock_name || '未知'}</h6>
                        <p class="mb-1"><strong>代码:</strong> ${stock.stock_code}</p>
                        <p class="mb-1"><strong>平均价格:</strong> ¥${stock.avg_price.toFixed(2)}</p>
                        <p class="mb-2"><strong>交易天数:</strong> ${stock.trade_days}天</p>
                        <button class="btn btn-sm btn-primary" onclick="showStockDetails('${stock.stock_code}')">
                            <i class="bi bi-eye"></i> 查看详情
                        </button>
                    </div>
                </div>
            `).join('');

            container.innerHTML = html;
        }

        // 加载行业分析
        async function loadIndustryAnalysis() {
            try {
                const response = await fetch('/api/industry-analysis');
                const data = await response.json();
                
                if (data.data) {
                    displayIndustryAnalysis(data.data);
                } else {
                    showError('industryList', data.error || '加载行业分析失败');
                }
            } catch (error) {
                showError('industryList', '网络错误: ' + error.message);
            }
        }

        // 显示行业分析
        function displayIndustryAnalysis(industries) {
            const container = document.getElementById('industryList');
            if (industries.length === 0) {
                container.innerHTML = '<div class="col-12"><div class="alert alert-info">未找到行业数据</div></div>';
                return;
            }

            const html = industries.map(industry => `
                <div class="col-md-6 col-lg-4">
                    <div class="stock-card">
                        <h6>${industry.industry_name || '未知行业'}</h6>
                        <p class="mb-1"><strong>股票数量:</strong> ${industry.stock_count}只</p>
                        <p class="mb-1"><strong>平均涨跌幅:</strong> ${industry.avg_change.toFixed(2)}%</p>
                        <p class="mb-1"><strong>平均市盈率:</strong> ${industry.avg_pe ? industry.avg_pe.toFixed(2) : 'N/A'}</p>
                        <p class="mb-2"><strong>平均市净率:</strong> ${industry.avg_pb ? industry.avg_pb.toFixed(2) : 'N/A'}</p>
                    </div>
                </div>
            `).join('');

            container.innerHTML = html;
        }

        // 显示错误信息
        function showError(containerId, message) {
            const container = document.getElementById(containerId);
            container.innerHTML = `<div class="col-12"><div class="error">${message}</div></div>`;
        }

        // 切换标签页
        function showTab(tabName) {
            currentTab = tabName;
            
            // 更新按钮状态
            document.querySelectorAll('.btn-group .btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // 显示对应内容
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
            });
            document.getElementById(tabName + '-tab').style.display = 'block';
        }
    </script>
</body>
</html>"""
    
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)

def main():
    """主函数"""
    print("A股金融数据Web交互界面")
    print("=" * 50)
    
    # 创建HTML模板
    create_templates()
    print("✅ HTML模板创建完成")
    
    # 初始化分析器
    if not init_analyzer():
        print("❌ 无法连接到数据库，请检查配置")
        return
    
    print("✅ 数据库连接成功")
    print("🌐 启动Web服务器...")
    print("📱 访问地址: http://localhost:5000")
    
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
