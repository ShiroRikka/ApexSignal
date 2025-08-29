# ApexSignal - A股数据获取与技术分析工具

## 项目简介

ApexSignal 是一个用 Python 编写的轻量级工具集，旨在方便地获取中国 A 股市场的股票行情数据，并进行基础的技术分析。本项目核心包含两个模块：

1.  **Ashare**: 一个修复版的、简化版的 A 股数据获取库。它封装了对新浪财经和腾讯财经 API 的调用，提供统一的 `get_price` 接口来获取日线、周线、月线以及分钟级别的历史数据（前复权）。
2.  **MyTT**: 一个麦语言（My Language）的 Python 实现，包含了常用的技术指标计算函数，如 MA, EMA, MACD, KDJ, RSI, BOLL 等。

本项目旨在为个人投资者和技术分析爱好者提供一个易于使用、易于理解的数据获取和分析平台。

## 功能特性

*   **简单易用**: 核心数据获取 (`Ashare`) 和技术分析 (`MyTT`) 功能分别封装在单个文件中，方便集成。
*   **双源数据**: `Ashare` 优先从腾讯财经获取数据，若失败则自动回退到新浪财经，提高数据获取的稳定性。
*   **数据格式友好**: 数据以 `pandas.DataFrame` 格式返回，便于后续处理和分析。
*   **丰富的技术指标**: `MyTT` 提供了数十种常用的技术分析指标计算函数。
*   **示例清晰**: 提供了 `get_stock_data.py` 示例脚本，展示如何获取数据并计算关键指标。

## 环境要求

*   Python >= 3.13
*   建议使用 `uv` 作为包管理器，以获得更快的依赖安装速度。

## 安装

1.  **克隆项目**:
    ```bash
    git clone https://github.com/your-username/ApexSignal.git
    cd ApexSignal
    ```

2.  **安装依赖**:
    *   使用 `uv` (推荐):
        ```bash
        uv sync
        ```

        # 或者基于 pyproject.toml
        pip install .
        ```

## 快速开始

运行项目根目录下的示例脚本 `get_stock_data.py` 来体验数据获取和指标计算功能：

```bash
python get_stock_data.py
```

该脚本会：
1.  获取光大银行 (sh601818) 最近 120 天的日线前复权数据。
2.  使用 `MyTT` 库计算 KDJ, MACD, RSI 指标。
3.  打印部分数据到控制台。
4.  将完整数据 (含指标) 保存到 CSV 文件 `sh601818_qfq_data_with_indicators.csv`。

## 使用方法

在你的 Python 脚本中，你可以这样使用：

```python
# 导入库
from Ashare import get_price
from MyTT import MA, MACD

# 获取平安银行 (sz000001) 最近 100 天的日线数据
df = get_price('sz000001', frequency='1d', count=100)
print(df.head())

# 计算 5 日和 20 日均线
df['MA5'] = MA(df['close'].values, 5)
df['MA20'] = MA(df['close'].values, 20)

# 计算 MACD 指标
df['DIF'], df['DEA'], df['MACD'] = MACD(df['close'].values)

print(df.tail())
```

## 项目结构

```
ApexSignal/
├── Ashare.py          # A股数据获取核心库 (修复版)
├── MyTT.py            # 技术分析指标库 (麦语言实现)
├── get_stock_data.py  # 示例脚本：获取数据并计算指标
├── requirements.txt   # pip 依赖文件
├── pyproject.toml     # 项目配置和 uv 依赖声明
└── README.md          # 项目说明文件
```

## 依赖说明

项目主要依赖如下库，详细信息请参见 `requirements.txt` 或 `pyproject.toml`：

*   `numpy`: 数值计算基础库。
*   `pandas`: 数据处理和分析库。
*   `requests`: 用于发起 HTTP 请求获取网络数据。
*   `tushare`, `akshare`, `baostock`: 其他可选的数据源库 (当前核心功能未使用)。

## 贡献

欢迎提交 Issue 或 Pull Request 来改进本项目。

## 许可证

本项目基于 MIT 许可证开源。