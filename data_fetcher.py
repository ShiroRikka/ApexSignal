# -*- coding:utf-8 -*-
import time
import os
import datetime

from Ashare import get_price
from MyTT import KDJ, MACD, RSI

# === 配置参数 ===
count = 200  # 取200天数据
frequency = "1d"
code = "sh601328"
filename = f"{code}_qfq_data_with_indicators.csv"

# 获取今天的日期
today = datetime.datetime.now().strftime("%Y-%m-%d")

print(f"📅 开始获取 {code} 的前复权数据...")

# --- 1. 检查是否已更新 ---
if os.path.exists(filename):
    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
    if file_time.strftime("%Y-%m-%d") == today:
        print(f"✅ {filename} 已是今日最新数据，无需重复下载")
        print("💡 如需强制更新，请删除该文件后重新运行")
        exit()

# --- 2. 获取行情数据 ---
df = get_price(code, end_date="", count=count, frequency=frequency)
if df.empty:
    print("❌ 数据获取失败，请检查网络或股票代码")
    exit()

print(f"✅ 获取到 {code} 的 {len(df)} 天前复权数据:")
print(df.head())
print("...")
print(df.tail())

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
df.to_csv(filename, encoding='utf-8-sig')
print(f"\n✅ 技术指标已计算完毕，保存到: {filename}")
print(f"📊 共 {len(df)} 行数据，最新日期: {df.index[-1].strftime('%Y-%m-%d')}")
