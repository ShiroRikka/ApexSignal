# -*- coding: utf-8 -*-
"""
data_updater.py
股票前复权数据 + 技术指标 自动更新模块
"""
import os
import time
import datetime
import yaml

from Ashare import get_price
from MyTT import KDJ, MACD, RSI


def load_config():
    """加载配置文件"""
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 未找到，请创建 config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def update_stock_data(code, count=None, frequency=None, force_update=None):
    """
    更新单只股票的技术指标数据
    :param code: 股票代码，如 'sh601328'
    :param count: 获取多少天数据（默认从配置读取）
    :param frequency: 周期，'1d' 表示日线（默认从配置读取）
    :param force_update: 是否强制更新（默认从配置读取）
    :return: DataFrame 或 None（失败时）
    """
    # 加载配置
    config = load_config().get("data_updater", {})
    if count is None:
        count = config.get("count", 200)
    if frequency is None:
        frequency = config.get("frequency", "1d")
    if force_update is None:
        force_update = config.get("force_update", False)
    """
    更新单只股票的技术指标数据
    :param code: 股票代码，如 'sh601328'
    :param count: 获取多少天数据（默认200）
    :param frequency: 周期，'1d' 表示日线
    :param force_update: 是否强制更新（忽略今日已更新）
    :return: DataFrame 或 None（失败时）
    """
    filename = f"{code}_qfq_data_with_indicators.csv"
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # --- 1. 检查是否已存在且为今天更新 ---
    if not force_update and os.path.exists(filename):
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        if file_time.strftime("%Y-%m-%d") == today:
            print(f"✅ {filename} 已是今日最新数据，跳过下载")
            try:
                return __load_and_return(filename, code)
            except Exception as e:
                print(f"⚠️ 读取缓存文件失败: {e}，重新获取数据")

    # --- 2. 获取行情数据 ---
    print(f"📥 正在获取 {code} 的 {count} 天前复权数据...")
    try:
        df = get_price(code, end_date="", count=count, frequency=frequency)
        if df.empty:
            print(f"❌ {code} 数据获取为空")
            return None
    except Exception as e:
        print(f"❌ {code} 数据获取失败: {e}")
        return None

    print(f"✅ 获取到 {len(df)} 天数据，最新日期: {df.index[-1].strftime('%Y-%m-%d')}")

    # --- 3. 计算技术指标 ---
    CLOSE = df["close"].values
    HIGH = df["high"].values
    LOW = df["low"].values

    K, D, J = KDJ(CLOSE, HIGH, LOW, 9, 3, 3)
    DIF, DEA, MACD_BAR = MACD(CLOSE, 12, 26, 9)
    RSI_VALUE = RSI(CLOSE, 14)

    # --- 4. 添加到 DataFrame ---
    df["K"] = K
    df["D"] = D
    df["J"] = J
    df["DIF"] = DIF
    df["DEA"] = DEA
    df["MACD"] = MACD_BAR
    df["RSI"] = RSI_VALUE

    # --- 5. 保存到 CSV ---
    try:
        df.to_csv(filename, encoding='utf-8-sig')
        print(f"✅ 数据与指标已保存至: {filename}")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return None

    return df


def __load_and_return(filename, code):
    """内部函数：加载已有 CSV 文件"""
    df = pd.read_csv(filename, index_col=0, parse_dates=True)
    print(f"🔁 使用本地缓存: {filename}")
    return df


# 确保能导入 pd
try:
    import pandas as pd
except ImportError:
    pass
