# -*- coding:utf-8 -*-
import pandas as pd
from Ashare.Ashare import get_price
from MyTT.MyTT import KDJ, MACD, RSI

# 1. 获取光大银行sh601818的行情数据
# 获取前120天的数据以及开盘当天的最新数据
count = 120 + 1  # 包含今天
frequency = '1d'  # 日线数据
code = 'sh601818'

# 获取数据
df = get_price(code, count=count, frequency=frequency)
print(f"获取到 {code} 的 {count} 天数据:")
print(df.head())
print("...")
print(df.tail())

# 2. 计算技术指标: KDJ, MACD, RSI
# 准备数据
CLOSE = df['close'].values
HIGH = df['high'].values
LOW = df['low'].values

# 计算KDJ
K, D, J = KDJ(CLOSE, HIGH, LOW, 9, 3, 3)

# 计算MACD
DIF, DEA, MACD_LINE = MACD(CLOSE,12,26,9)

# 计算RSI
RSI_VALUE = RSI(CLOSE,14)

# 将计算得到的技术指标添加到原始DataFrame中
df['K'] = K
df['D'] = D
df['J'] = J
df['DIF'] = DIF
df['DEA'] = DEA
df['MACD'] = MACD_LINE
df['RSI'] = RSI_VALUE

# 打印带有技术指标的DataFrame的最后几行
print("\n带有技术指标的最后几行数据:")
print(df.tail())

# 可选：保存数据到CSV文件
df.to_csv(f'{code}_data_with_indicators.csv')
print(f"\n数据已保存到 {code}_data_with_indicators.csv")