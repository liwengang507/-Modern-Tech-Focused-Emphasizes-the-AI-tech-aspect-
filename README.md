# 🚀 A股金融年报ChatBI系统

一个基于qwen-agent框架的智能股票查询分析助手系统，提供全面的A股数据分析和可视化功能。

## ✨ 主要功能

### 🔍 数据查询分析
- **SQL查询**: 智能生成SQL查询语句，支持复杂数据分析
- **数据可视化**: 自动生成图表，支持折线图、柱状图等多种类型
- **股票对比**: 多只股票的对比分析和涨跌幅统计

### 📰 热点资讯
- **新闻搜索**: 基于Tavily API的实时财经新闻搜索
- **热点追踪**: 获取最新的A股市场热点信息

### 📈 技术分析
- **ARIMA预测**: 基于ARIMA模型的股票价格预测
- **布林带检测**: 20日周期+2σ的超买超卖点检测
- **Prophet分析**: 股票的趋势和周期性规律分析

## 🏗️ 项目结构

```
A股金融年报ChatBI系统/
├── main.py                     # 主入口文件
├── requirements.txt            # 依赖包列表
├── README.md                   # 项目说明
├── core/                       # 核心模块
│   └── stock_query_assistant.py
├── data_processing/            # 数据处理模块
│   ├── config_baostock.py
│   ├── get_*.py
│   └── merge_stock_data.py
├── analysis/                   # 分析工具
│   ├── analyze_excel_and_generate_sql.py
│   └── check_data_relationship.py
├── visualization/              # 可视化模块
│   └── image_show/            # 图表输出目录
├── tools/                      # 工具和测试
│   ├── demo*.py
│   └── test_*.py
├── docs/                       # 文档
│   ├── README_*.md
│   ├── requirements_stock_assistant.txt
│   └── *.txt
├── assets/                     # 资源文件
│   ├── stock_daily_data.sql   # 数据库结构
│   └── A股金融日线数据/       # 数据文件
└── 配置文件/                   # 配置模块
    ├── config.py
    ├── data_loader.py
    └── web_interface.py
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd A股金融年报ChatBI系统

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

#### API密钥配置
在代码中配置以下API密钥：

```python
# DashScope API Key (阿里云通义千问)
DASHSCOPE_API_KEY = "your_dashscope_api_key"

# Tavily API Key (新闻搜索)
TAVILY_API_KEY = "your_tavily_api_key"
```

#### 数据库配置
配置MySQL数据库连接：

```python
# 数据库配置
DB_CONFIG = {
    'host': 'your_host',
    'port': 3306,
    'user': 'your_username',
    'password': 'your_password',
    'database': 'lwg_database'
}
```

### 3. 数据库初始化

```bash
# 导入股票数据表结构
mysql -u username -p database_name < assets/stock_daily_data.sql
```

### 4. 启动系统

```bash
# 启动系统
python main.py
```

系统启动后，访问 `http://localhost:7860` 使用Web界面。

## 💡 使用示例

### 基础查询
- "查询平安银行(sz.000001)最近一周的股价数据"
- "显示万科A(sz.000002)的涨跌幅信息"

### 对比分析
- "对比青岛啤酒(sh.600600)和方正科技(sh.600601)的涨跌幅"

### 技术分析
- "预测平安银行(sz.000001)未来5天的股价"
- "检测青岛啤酒(sh.600600)的布林带异常点"
- "分析青岛啤酒(sh.600600)的周期性规律"

### 新闻搜索
- "搜索最新的A股热点新闻"
- "查找今日股市新闻"

## 🔧 系统特色

### 智能图表生成
- 自动选择图表类型（数据量大用折线图，数据量小用柱状图）
- 智能优化X轴标签显示
- 支持中文字体显示

### 多维度分析
- **ARIMA预测**: 支持1-N天的价格预测
- **布林带检测**: 识别超买超卖信号
- **Prophet分析**: 趋势和季节性分析

### 用户友好界面
- 提供8+条推荐对话示例
- 实时图表生成和显示
- 响应式Web界面设计

## 📊 技术栈

- **AI框架**: qwen-agent (通义千问)
- **数据库**: MySQL + SQLAlchemy
- **数据处理**: pandas, numpy
- **可视化**: matplotlib, seaborn
- **时间序列**: statsmodels (ARIMA), Prophet
- **Web界面**: Gradio
- **数据源**: BaoStock API

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue: [GitHub Issues](项目Issues链接)
- 邮箱: your-email@example.com

---

⭐ 如果这个项目对您有帮助，请给它一个星标！
