import pandas as pd

class TOOLS:
    """实用工具类"""

    def __init__(self, csv_file):
        """加载数据"""
        self.df = pd.read_csv(csv_file)
        self.df['time'] = pd.to_datetime(self.df['time'])
        print(f"{csv_file} 数据加载成功")

    def get_latest_two_all(self):
        """
        返回：
                   time  open  close  high  ...    DIF    DEA   MACD     RSI
        198  2025-08-28  3.86   3.85  3.89  ... -0.059 -0.045 -0.027  33.001
        199  2025-08-29  3.85   3.78  3.94  ... -0.068 -0.050 -0.037  28.829
        """
        return self.df.tail(2)




if __name__ == '__main__':
    tools = TOOLS("sh601818_qfq_data_with_indicators.csv")
    latest_two = tools.get_latest_two_all()
    print(latest_two)