# -*- coding:utf-8 -*-
import json
import requests
import pandas as pd
from MyTT import KDJ, MACD, RSI

def get_price_day_tx_fixed(code, end_date='', count=10, frequency='1d'):
    """修复版的腾讯日线获取函数"""
    unit = 'week' if frequency in '1w' else 'month' if frequency in '1M' else 'day'
    if end_date:
        end_date = end_date.strftime('%Y-%m-%d') if isinstance(end_date, pd.Timestamp) else end_date.split(' ')[0]
    end_date = '' if end_date == pd.Timestamp.now().strftime('%Y-%m-%d') else end_date
    
    URL = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date},{count},qfq'
    st = json.loads(requests.get(URL).content)
    ms = 'qfq' + unit
    stk = st['data'][code]
    buf = stk[ms] if ms in stk else stk[unit]
    
    # 修复：手动创建DataFrame，避免列数不匹配问题
    # 腾讯接口返回的数据顺序是：日期,开盘,收盘,最高,最低,成交量
    data = {
        'time': [item[0] for item in buf],
        'open': [item[1] for item in buf],
        'close': [item[2] for item in buf],
        'high': [item[3] for item in buf],
        'low': [item[4] for item in buf],
        'volume': [item[5] for item in buf]
    }
    
    df = pd.DataFrame(data)
    
    # 转换数据类型
    df['time'] = pd.to_datetime(df['time'])
    numeric_cols = ['open', 'close', 'high', 'low', 'volume']
    df[numeric_cols] = df[numeric_cols].astype(float)
    
    df.set_index(['time'], inplace=True)
    df.index.name = ''
    return df

# 1. 获取光大银行sh601818的前复权行情数据
count = 120 + 1  # 包含今天
frequency = '1d'  # 日线数据
code = 'sh601818'

# 使用修复版的腾讯接口获取前复权数据
df = get_price_day_tx_fixed(code, end_date='', count=count, frequency=frequency)
print(f"获取到 {code} 的 {count} 天前复权数据:")
print(df.head())
print("...")
print(df.tail())

# 2. 计算技术指标: KDJ, MACD, RSI
# 准备数据
CLOSE = df['close'].values
HIGH = df['high'].values
LOW = df['low'].values

# 计算KDJ (需要至少9天数据)
K, D, J = KDJ(CLOSE, HIGH, LOW, 9, 3, 3)

# 计算MACD (需要至少26天数据)
DIF, DEA, MACD_LINE = MACD(CLOSE, 12, 26, 9)

# 计算RSI (需要至少14天数据)
RSI_VALUE = RSI(CLOSE, 14)

# 将计算得到的技术指标添加到原始DataFrame中
# 注意：由于技术指标计算需要历史数据，前期会有NaN值，这是正常现象
df['K'] = K
df['D'] = D
df['J'] = J
df['DIF'] = DIF
df['DEA'] = DEA
df['MACD'] = MACD_LINE
df['RSI'] = RSI_VALUE

# 打印带有技术指标的DataFrame的最后几行
print("\n技术指标的最后几行数据:")
print(df.tail())

# 可选：保存数据到CSV文件
df.to_csv(f'{code}_qfq_data_with_indicators.csv')
print(f"\n前复权数据已保存到 {code}_qfq_data_with_indicators.csv")