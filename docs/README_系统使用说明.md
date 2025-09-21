# A股金融年报智能分析交互系统

## 系统简介

本系统是一个完整的A股金融数据智能分析平台，集成了数据获取、存储、分析和可视化功能。系统使用BaoStock API获取A股市场数据，通过MySQL数据库存储，并提供Web界面进行数据查询和分析。

## 功能特点

### 📊 数据获取
- 使用BaoStock API获取A股上市公司数据
- 支持股票基本信息、财务数据、日线数据、行业数据
- 自动处理API请求频率限制
- 数据保存为CSV和Excel格式

### 💾 数据存储
- MySQL数据库存储，支持大数据量
- 自动创建数据表和索引
- 支持数据批量导入
- 数据完整性校验

### 📈 数据分析
- 股票表现分析
- 行业对比分析
- 表现最佳股票筛选
- 财务指标统计分析

### 🌐 Web界面
- 现代化的Web界面设计
- 股票搜索和筛选
- 实时数据展示
- 交互式图表展示

### 📊 数据可视化
- 股票走势图
- 行业对比图表
- 财务指标图表
- 支持图表导出

## 系统架构

```
A股金融年报智能分析交互系统
├── 数据获取层 (BaoStock API)
├── 数据存储层 (MySQL)
├── 业务逻辑层 (Python)
├── 数据展示层 (Web界面)
└── 可视化层 (Matplotlib/Seaborn)
```

## 安装和配置

### 1. 环境要求

- Python 3.8+
- MySQL 5.7+
- 网络连接（用于API数据获取）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库配置

1. 启动MySQL服务
2. 创建数据库用户（可选）
3. 修改 `config.py` 中的数据库配置：

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'stock_analysis',
    'user': 'root',
    'password': 'your_password',  # 修改为实际密码
    'port': 3306,
    'charset': 'utf8mb4'
}
```

### 4. 快速启动

运行启动脚本：

```bash
python run_system.py
```

## 使用指南

### 1. 系统初始化

首次使用时，按以下步骤操作：

1. **检查系统环境**
   - 验证依赖包安装
   - 检查MySQL连接

2. **设置数据库**
   - 创建数据库
   - 创建数据表
   - 设置索引

3. **加载数据**
   - 从CSV文件导入数据
   - 验证数据完整性

### 2. 数据获取

如果需要获取最新数据：

```bash
python get_stock_data_baostock.py
```

### 3. Web界面使用

启动Web服务器后，访问 `http://localhost:5000`：

- **股票列表**: 浏览所有股票
- **搜索功能**: 按代码或名称搜索
- **表现最佳**: 查看表现最好的股票
- **行业分析**: 查看行业对比数据
- **股票详情**: 点击查看详细分析

### 4. 数据分析

运行数据分析程序：

```bash
python stock_analyzer.py
```

## 文件结构

```
金融年报智能分析交互系统/
├── 数据获取
│   ├── get_stock_data_baostock.py     # 主数据获取程序
│   ├── quick_get_data_baostock.py     # 快速测试版本
│   └── config_baostock.py             # BaoStock配置
├── 数据处理
│   ├── data_loader.py                 # 数据加载器
│   ├── merge_stock_data.py            # 数据合并
│   └── analyze_excel_and_generate_sql.py  # Excel分析
├── 数据分析
│   ├── stock_analyzer.py              # 数据分析器
│   └── check_data_relationship.py     # 数据关系检查
├── Web界面
│   ├── web_interface.py               # Web服务器
│   └── templates/                     # HTML模板
├── 配置和工具
│   ├── config.py                      # 系统配置
│   ├── run_system.py                  # 启动脚本
│   ├── requirements.txt               # 依赖包列表
│   └── stock_daily_data.sql           # 数据库建表语句
├── 数据文件
│   └── A股金融日线数据/
│       ├── 完整A股金融日线数据_修复编码.csv
│       └── 完整A股金融日线数据_20250920_221233.xlsx
└── 文档
    ├── README_系统使用说明.md          # 本文档
    ├── README_BaoStock.md             # BaoStock说明
    └── phpMyAdmin导入说明.txt          # 数据库导入说明
```

## API接口

### 数据接口

- `GET /api/stocks` - 获取股票列表
- `GET /api/stock/<code>` - 获取指定股票数据
- `GET /api/stock/<code>/analysis` - 获取股票分析
- `GET /api/top-performers` - 获取表现最佳股票
- `GET /api/industry-analysis` - 获取行业分析
- `GET /api/search` - 搜索股票
- `GET /api/statistics` - 获取数据统计

### 图表接口

- `GET /api/chart/<code>` - 获取股票走势图

## 配置说明

### 数据库配置

在 `config.py` 中修改数据库连接参数：

```python
DATABASE_CONFIG = {
    'host': 'localhost',        # 数据库主机
    'database': 'stock_analysis',  # 数据库名称
    'user': 'root',            # 用户名
    'password': '',            # 密码
    'port': 3306,              # 端口
    'charset': 'utf8mb4'       # 字符集
}
```

### Web服务器配置

```python
WEB_CONFIG = {
    'host': '0.0.0.0',         # 监听地址
    'port': 5000,              # 端口
    'debug': True              # 调试模式
}
```

### 数据获取配置

```python
BAOSTOCK_CONFIG = {
    'start_date': '2020-01-01',  # 开始日期
    'end_date': '2025-01-01',    # 结束日期
    'max_stocks': 1000,          # 最大股票数量
    'request_delay': 0.1         # 请求间隔
}
```

## 常见问题

### Q: 如何修改获取数据的日期范围？

A: 修改 `config.py` 中的 `BAOSTOCK_CONFIG` 配置，或者直接修改 `get_stock_data_baostock.py` 中的日期参数。

### Q: 数据库连接失败怎么办？

A: 检查MySQL服务是否启动，用户名密码是否正确，数据库是否存在。

### Q: 如何添加新的分析功能？

A: 在 `stock_analyzer.py` 中添加新的分析方法，然后在 `web_interface.py` 中添加对应的API接口。

### Q: 如何部署到生产环境？

A: 修改 `config.py` 中的配置，使用生产环境的数据库和服务器设置，关闭调试模式。

### Q: 数据更新频率如何设置？

A: 可以通过定时任务（如cron）定期运行数据获取程序，建议每日更新。

## 技术支持

如果遇到问题，请检查：

1. 依赖包是否正确安装
2. MySQL服务是否正常运行
3. 网络连接是否正常
4. 数据文件是否存在

## 更新日志

### v1.0.0 (2025-01-01)
- 初始版本发布
- 完成基础功能开发
- 支持数据获取、存储、分析和可视化

## 许可证

本项目仅用于学习和研究目的，不构成投资建议。

## 免责声明

本项目使用的数据来源于BaoStock API，使用者应当自行承担使用数据的风险。系统仅提供数据分析工具，不提供投资建议。
