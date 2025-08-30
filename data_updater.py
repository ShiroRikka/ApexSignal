# -*- coding: utf-8 -*-
"""
data_updater.py
股票前复权数据 + 技术指标 自动更新模块
"""
import os
import time
import datetime
import yaml
import logging

# --- 新增导入 ---
from Ashare import get_price
from MyTT import KDJ, MACD, RSI

# --- 新增日志配置 ---
def setup_logger(config):
    level = getattr(logging, config.get("log_level", "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def load_config():
    """加载配置文件"""
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 未找到，请创建 config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def update_stock_data(code, config=None):
    """
    更新单只股票的技术指标数据
    :param code: 股票代码，如 'sh601328'
    :param config: 配置字典 (可选，如果未提供则加载)
    :return: DataFrame 或 None（失败时）
    """
    if config is None:
        config = load_config()
    
    logger = setup_logger(config.get("output", {}))
    data_updater_config = config.get("data_updater", {})
    indicators_config = config.get("indicators", {})
    
    count = data_updater_config.get("default_count", 200)
    frequency = data_updater_config.get("default_frequency", "1d")
    force_update = data_updater_config.get("force_update", False)
    cache_dir = data_updater_config.get("cache_dir", ".")
    
    # 确保缓存目录存在
    os.makedirs(cache_dir, exist_ok=True)
    filename = os.path.join(cache_dir, f"{code}_qfq_data_with_indicators.csv")
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # --- 1. 检查是否已存在且为今天更新 ---
    if not force_update and os.path.exists(filename):
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        if file_time.strftime("%Y-%m-%d") == today:
            logger.info(f"✅ {filename} 已是今日最新数据，跳过下载")
            try:
                return __load_and_return(filename, code)
            except Exception as e:
                logger.warning(f"⚠️ 读取缓存文件失败: {e}，重新获取数据")

    # --- 2. 获取行情数据 ---
    logger.info(f"📥 正在获取 {code} 的 {count} 天前复权数据...")
    try:
        df = get_price(code, end_date="", count=count, frequency=frequency)
        if df.empty:
            logger.error(f"❌ {code} 数据获取为空")
            return None
    except Exception as e:
        logger.error(f"❌ {code} 数据获取失败: {e}")
        return None

    logger.info(f"✅ 获取到 {len(df)} 天数据，最新日期: {df.index[-1].strftime('%Y-%m-%d')}")

    # --- 3. 计算技术指标 ---
    CLOSE = df["close"].values
    HIGH = df["high"].values
    LOW = df["low"].values

    # 从配置读取指标参数
    kdj_params = indicators_config.get("kdj", {})
    macd_params = indicators_config.get("macd", {})
    rsi_params = indicators_config.get("rsi", {})

    K, D, J = KDJ(CLOSE, HIGH, LOW, kdj_params.get("n", 9), kdj_params.get("m1", 3), kdj_params.get("m2", 3))
    DIF, DEA, MACD_BAR = MACD(CLOSE, macd_params.get("fast_period", 12), macd_params.get("slow_period", 26), macd_params.get("signal_period", 9))
    RSI_VALUE = RSI(CLOSE, rsi_params.get("period", 14))

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
        logger.info(f"✅ 数据与指标已保存至: {filename}")
    except Exception as e:
        logger.error(f"❌ 保存文件失败: {e}")
        return None

    return df

def __load_and_return(filename, code):
    """内部函数：加载已有 CSV 文件"""
    import pandas as pd # 确保 pd 在此函数内可用
    df = pd.read_csv(filename, index_col=0, parse_dates=True)
    logger = logging.getLogger(__name__) # 使用已配置的 logger
    logger.info(f"🔁 使用本地缓存: {filename}")
    return df

# --- 为了兼容旧的直接调用方式 ---
# 如果你希望保留 update_stock_data(code) 的旧用法，可以添加一个包装器
def update_stock_data_old_style(code, count=None, frequency=None, force_update=None):
    """兼容旧的调用方式"""
    config = load_config()
    # 允许旧参数覆盖配置
    if count is not None:
        config["data_updater"]["default_count"] = count
    if frequency is not None:
        config["data_updater"]["default_frequency"] = frequency
    if force_update is not None:
        config["data_updater"]["force_update"] = force_update
    return update_stock_data(code, config)

# 确保能导入 pd (在模块级别)
try:
    import pandas as pd
except ImportError:
    pass
