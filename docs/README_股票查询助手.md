# A股股票查询助手

基于qwen-agent和MySQL数据库的智能A股股票查询助手，支持自然语言查询和自动数据可视化。

## 功能特点

### 🔍 智能查询
- 自然语言股票查询
- SQL自动生成
- 多维度数据分析

### 📊 数据可视化
- 自动生成图表
- 多种图表类型
- 实时数据展示

### 💬 交互方式
- Web图形界面
- 终端命令行
- 连续对话支持

## 支持的查询类型

### 1. 股票基本信息查询
- "查询股票600036的基本信息"
- "显示招商银行的股票数据"

### 2. 股票价格走势分析
- "查看平安银行最近30天的股价走势"
- "分析万科A在2024年的价格变化"

### 3. 行业对比分析
- "银行业股票的平均市盈率对比"
- "各行业股票数量统计"

### 4. 财务指标分析
- "查询净利润最高的10只股票"
- "显示ROE排名前20的股票"

### 5. 交易数据统计
- "今日成交量最大的股票"
- "涨跌幅排行榜"

### 6. 股票筛选和排序
- "筛选市盈率在10-20之间的股票"
- "找出总资产超过1000亿的股票"

## 安装和配置

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+
- DashScope API Key

### 2. 安装依赖
```bash
pip install -r requirements_stock_assistant.txt
```

### 3. 数据库配置
确保MySQL数据库`stock`中存在`stock_daily_data`表，包含A股股票数据。

### 4. API Key配置
设置DashScope API Key环境变量：
```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

或在代码中直接设置：
```python
dashscope.api_key = "your_api_key_here"
```

## 使用方法

### 1. 测试系统
```bash
python test_stock_assistant.py
```

### 2. 终端模式
```bash
python stock_query_assistant.py tui
```

### 3. Web界面模式
```bash
python stock_query_assistant.py gui
```
然后访问 http://localhost:7860

## 示例查询

### 基本查询示例
```
用户: 查询招商银行最近一年的股价走势
助手: [自动生成SQL并返回图表]

用户: 显示银行业股票的平均市盈率排名
助手: [返回行业对比图表]

用户: 找出2024年涨幅最大的10只股票
助手: [返回涨跌幅排行榜]
```

### 复杂查询示例
```
用户: 筛选出市盈率在10-20之间，总资产超过1000亿的股票
助手: [返回筛选结果和对比图表]

用户: 分析各行业股票的数量分布和平均市值
助手: [返回行业分析图表]
```

## 数据库表结构

### stock_daily_data表字段说明
- `stock_code`: 股票代码
- `stock_name`: 股票名称
- `trade_date`: 交易日期
- `open_price`: 开盘价
- `high_price`: 最高价
- `low_price`: 最低价
- `close_price`: 收盘价
- `volume`: 成交量
- `amount`: 成交额
- `pct_change`: 涨跌幅
- `pe_ttm`: 市盈率TTM
- `pb_ratio`: 市净率
- `net_profit`: 净利润
- `revenue`: 营业收入
- `industry_name`: 行业名称
- 更多字段请参考stock_daily_data.sql

## 图表类型

系统会根据查询结果自动生成相应类型的图表：

1. **股价走势图**: 时间序列数据
2. **股票对比图**: 多股票对比
3. **行业分析图**: 行业数据对比
4. **涨跌幅图**: 涨跌幅分析
5. **通用柱状图**: 其他统计数据

## 文件结构

```
股票查询助手/
├── stock_query_assistant.py      # 主程序
├── test_stock_assistant.py       # 测试脚本
├── requirements_stock_assistant.txt  # 依赖包
├── README_股票查询助手.md        # 说明文档
└── stock_charts/                 # 图表输出目录
```

## 常见问题

### Q: 如何修改数据库连接配置？
A: 在`stock_query_assistant.py`中修改ExcSQLTool类的数据库连接参数。

### Q: 如何添加新的图表类型？
A: 在`generate_stock_chart`函数中添加新的图表生成逻辑。

### Q: 如何自定义查询建议？
A: 在`app_gui`函数中修改`chatbot_config`的`prompt.suggestions`。

### Q: 如何扩展支持的查询类型？
A: 修改`system_prompt`中的说明，添加新的查询类型描述。

## 技术架构

```
用户输入 → qwen-agent → SQL生成 → 数据库查询 → 结果处理 → 图表生成 → 结果展示
```

- **自然语言处理**: qwen-agent + DashScope API
- **数据库**: MySQL + pandas
- **可视化**: matplotlib + seaborn
- **Web界面**: gradio + streamlit

## 更新日志

### v1.0.0 (2025-01-01)
- 初始版本发布
- 支持基本股票查询功能
- 集成自动图表生成
- 提供Web和终端两种交互方式

## 许可证

本项目仅用于学习和研究目的。

## 免责声明

本系统提供的数据和分析结果仅供参考，不构成投资建议。使用者应当自行承担使用数据的风险。
