# ApexSignal 项目说明 (QWEN.md)

## 项目概述

ApexSignal 是一个 Python 项目，旨在获取、存储和分析中国 A 股市场的股票数据。它利用 `Ashare` 或 `Tushare` 等 API 来获取股票的行情数据（如开盘价、收盘价、最高价、最低价、成交量等），并基于这些数据计算常用的技术指标，如 MACD、KDJ、RSI 等。项目的核心功能是通过 MACD 指标进行多维度的信号分析，包括金叉死叉、趋势判断、动能分析和顶底背离检测，并提供综合的交易建议。

项目的主要技术栈包括：
- **Python 3.13+**
- **数据处理**: `pandas`, `numpy`
- **数据获取**: `akshare`, `baostock`, `tushare`, `requests` (自定义 `Ashare.py`)
- **配置管理**: `pyyaml`
- **可视化**: `matplotlib`
- **Web 框架 (可能用于后续扩展)**: `flask`
- **科学计算**: `scipy`

## 项目结构与核心文件

- `main.py`: 项目主入口。定义了关注的股票列表，并调用 `data_updater` 和 `macd_checker` 模块来执行数据更新和信号分析。
- `data_updater.py`: 负责获取股票数据并计算技术指标。
  - 使用 `Ashare.get_price` 获取指定股票代码的行情数据。
  - 使用 `MyTT.py` 中的函数计算 KDJ, MACD, RSI 指标。
  - 将带有指标的数据保存为 CSV 文件 (`{code}_qfq_data_with_indicators.csv`) 以便缓存和后续分析。
- `macd_checker.py`: 核心分析模块，执行 MACD 相关的各种信号检测。
  - `MACDChecker` 类：封装了对单个股票数据进行分析的所有逻辑。
  - 方法包括：`get_cross_signal` (金叉死叉), `get_trend_signal` (零轴趋势), `get_momentum_signal` (柱状图动能), `detect_macd_divergence` (顶底背离), 以及综合所有信号的 `run` 方法。
  - `run` 方法通过一个评分系统整合多个信号，给出最终的买卖建议（如 `strong_buy`, `buy`, `hold`, `sell`, `strong_sell`）。
- `Ashare.py`: 自定义的数据获取模块，封装了从腾讯和新浪接口获取股票行情数据的函数。
- `MyTT.py`: 自定义的技术指标计算模块，实现了 KDJ, MACD, RSI 等指标的计算公式。
- `tools.py`: 通用工具模块，目前包含 `TOOLS` 类，用于加载和处理 CSV 数据。
- `config.yaml`: 项目的配置文件，定义了数据更新和 MACD 检查的相关参数。
- `pyproject.toml`: 项目的依赖和元数据定义文件。

## 运行与开发

### 运行项目
1.  确保已安装 Python 3.13 及以上版本。
2.  安装依赖：`pip install -r requirements.txt` (如果存在) 或根据 `pyproject.toml` 使用 `pip install .` 或 `uv pip install .`。
3.  (可选) 配置 `config.yaml` 文件以调整数据获取和分析参数。
4.  运行主程序：`python main.py`。这将依次更新 `main.py` 中定义的股票列表的数据，并为每只股票生成 MACD 分析报告和图表。

### 开发约定
- **依赖管理**: 使用 `pyproject.toml` 管理项目依赖。
- **配置**: 通过 `config.yaml` 文件进行配置，代码中通过 `yaml.safe_load` 加载。
- **数据存储**: 将获取到的带技术指标的数据缓存为 CSV 文件，文件名格式为 `{stock_code}_qfq_data_with_indicators.csv`。
- **代码结构**: 功能模块化，将数据获取、数据处理、信号分析等功能分别放在不同的 `.py` 文件中。
- **指标计算**: 技术指标的计算逻辑集中在 `MyTT.py` 文件中。
- **信号分析**: `macd_checker.py` 是信号分析的核心，通过 `MACDChecker` 类提供面向对象的分析接口。