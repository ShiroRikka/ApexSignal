# main.py
import os
import subprocess

# 先更新数据
print("🔄 正在更新数据...")
subprocess.run(["python", "data_fetcher.py"])

# 再分析信号
print("🔍 正在分析信号...")
subprocess.run(["python", "macd_checker.py"])
