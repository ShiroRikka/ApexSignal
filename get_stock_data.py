# -*- coding:utf-8 -*-
import time

from Ashare import get_price
from MyTT import KDJ, MACD, RSI

# 1. 获取光大银行sh601818的前复权行情数据
count = 120 + 1  # 包含今天
frequency = "1d"  # 日线数据
code = "sh601818"

while True:
    # 使用修复版的腾讯接口获取前复权数据
    df = get_price(code, end_date="", count=count, frequency=frequency)
    print(f"获取到 {code} 的 {count} 天前复权数据:")
    print(df.head())
    print("...")
    print(df.tail())

    # 2. 计算技术指标: KDJ, MACD, RSI
    # 准备数据
    CLOSE = df["close"].values
    HIGH = df["high"].values
    LOW = df["low"].values

    # 计算KDJ (需要至少9天数据)
    K, D, J = KDJ(CLOSE, HIGH, LOW, 9, 3, 3)

    # 计算MACD (需要至少26天数据)
    DIF, DEA, MACD_BAR = MACD(CLOSE, 12, 26, 9)

    # 计算RSI (需要至少14天数据)
    RSI_VALUE = RSI(CLOSE, 14)

    # 将计算得到的技术指标添加到原始DataFrame中
    # 注意：由于技术指标计算需要历史数据，前期会有NaN值，这是正常现象
    df["K"] = K
    df["D"] = D
    df["J"] = J
    df["DIF"] = DIF
    df["DEA"] = DEA
    df["MACD"] = MACD_BAR
    df["RSI"] = RSI_VALUE

    # 打印带有技术指标的DataFrame的最后几行
    print("\n技术指标的最后几行数据:")
    print(df.tail())

    # 可选：保存数据到CSV文件
    df.to_csv(f"{code}_qfq_data_with_indicators.csv")
    print(f"\n前复权数据已保存到 {code}_qfq_data_with_indicators.csv")

    time.sleep(60)
