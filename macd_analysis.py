import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

class MACDAnalyzer:
    def __init__(self, csv_file):
        """初始化MACD分析器"""
        self.df = pd.read_csv(csv_file)
        self.df['time'] = pd.to_datetime(self.df['time'])
        self.df.set_index('time', inplace=True)

        print(f"数据加载完成，共 {len(self.df)} 条记录")
        print(f"数据时间范围: {self.df.index[0]} 到 {self.df.index[-1]}")
    
    def detect_cross_signals(self):
        """1. 检测金叉和死叉信号"""
        print("\n=== 1. 金叉与死叉检测 ===")
        
        # 检测金叉：MACD线从下向上穿过信号线
        self.df['golden_cross'] = (
            (self.df['DIF'] > self.df['DEA']) & 
            (self.df['DIF'].shift(1) <= self.df['DEA'].shift(1))
        )
        
        # 检测死叉：MACD线从上向下穿过信号线
        self.df['death_cross'] = (
            (self.df['DIF'] < self.df['DEA']) & 
            (self.df['DIF'].shift(1) >= self.df['DEA'].shift(1))
        )
        
        # 获取金叉和死叉的日期
        golden_dates = self.df[self.df['golden_cross']].index
        death_dates = self.df[self.df['death_cross']].index
        
        print(f"发现 {len(golden_dates)} 个金叉信号:")
        for date in golden_dates:
            print(f"  📈 金叉: {date.date()} - MACD: {self.df.loc[date, 'DIF']:.4f}")
        
        print(f"发现 {len(death_dates)} 个死叉信号:")
        for date in death_dates:
            print(f"  📉 死叉: {date.date()} - MACD: {self.df.loc[date, 'DIF']:.4f}")
        
        return golden_dates, death_dates
    
    def detect_zero_cross(self):
        """2. 检测零轴穿越信号"""
        print("\n=== 2. 零轴穿越检测 ===")
        
        # 检测MACD线上穿零轴（由负转正）
        self.df['zero_cross_up'] = (
            (self.df['DIF'] > 0) & 
            (self.df['DIF'].shift(1) <= 0)
        )
        
        # 检测MACD线下穿零轴（由正转负）
        self.df['zero_cross_down'] = (
            (self.df['DIF'] < 0) & 
            (self.df['DIF'].shift(1) >= 0)
        )
        
        zero_up_dates = self.df[self.df['zero_cross_up']].index
        zero_down_dates = self.df[self.df['zero_cross_down']].index
        
        print(f"MACD线上穿零轴（多头信号）:")
        for date in zero_up_dates:
            print(f"  ⬆️ 零轴上穿: {date.date()} - MACD: {self.df.loc[date, 'DIF']:.4f}")
        
        print(f"MACD线下穿零轴（空头信号）:")
        for date in zero_down_dates:
            print(f"  ⬇️ 零轴下穿: {date.date()} - MACD: {self.df.loc[date, 'DIF']:.4f}")
        
        return zero_up_dates, zero_down_dates
    
    def detect_divergence(self, window=10):
        """3. 检测背离信号"""
        print(f"\n=== 3. 背离检测（窗口期: {window}天） ===")
        
        # 找到价格的局部极值点
        price_highs_idx = argrelextrema(self.df['close'].values, np.greater, order=window)[0]
        price_lows_idx = argrelextrema(self.df['close'].values, np.less, order=window)[0]
        
        # 找到MACD的局部极值点
        macd_highs_idx = argrelextrema(self.df['DIF'].values, np.greater, order=window)[0]
        macd_lows_idx = argrelextrema(self.df['DIF'].values, np.less, order=window)[0]
        
        # 检测顶背离（价格创新高但MACD不创新高）
        print("顶背离检测:")
        for i in range(1, len(price_highs_idx)):
            current_price_idx = price_highs_idx[i]
            prev_price_idx = price_highs_idx[i-1]
            
            if (self.df['close'].iloc[current_price_idx] > self.df['close'].iloc[prev_price_idx] and
                self.df['DIF'].iloc[current_price_idx] < self.df['DIF'].iloc[prev_price_idx]):
                
                current_date = self.df.index[current_price_idx]
                print(f"  ⚠️ 顶背离: {current_date.date()}")
                print(f"     价格: {self.df['close'].iloc[current_price_idx]:.3f} > {self.df['close'].iloc[prev_price_idx]:.3f}")
                print(f"     MACD: {self.df['DIF'].iloc[current_price_idx]:.4f} < {self.df['DIF'].iloc[prev_price_idx]:.4f}")
        
        # 检测底背离（价格创新低但MACD不创新低）
        print("底背离检测:")
        for i in range(1, len(price_lows_idx)):
            current_price_idx = price_lows_idx[i]
            prev_price_idx = price_lows_idx[i-1]
            
            if (self.df['close'].iloc[current_price_idx] < self.df['close'].iloc[prev_price_idx] and
                self.df['DIF'].iloc[current_price_idx] > self.df['DIF'].iloc[prev_price_idx]):
                
                current_date = self.df.index[current_price_idx]
                print(f"  ✅ 底背离: {current_date.date()}")
                print(f"     价格: {self.df['close'].iloc[current_price_idx]:.3f} < {self.df['close'].iloc[prev_price_idx]:.3f}")
                print(f"     MACD: {self.df['DIF'].iloc[current_price_idx]:.4f} > {self.df['DIF'].iloc[prev_price_idx]:.4f}")
    
    def analyze_MACD_momentum(self):
        """4. 分析柱状图动能变化"""
        print("\n=== 4. 柱状图动能分析 ===")
        
        # 检测柱状图由负转正
        self.df['hist_positive'] = (
            (self.df['MACD'] > 0) & 
            (self.df['MACD'].shift(1) <= 0)
        )
        
        # 检测柱状图由正转负
        self.df['hist_negative'] = (
            (self.df['MACD'] < 0) & 
            (self.df['MACD'].shift(1) >= 0)
        )
        
        # 检测柱状图持续放大（动能增强）
        self.df['momentum_increasing'] = (
            (abs(self.df['MACD']) > abs(self.df['MACD'].shift(1))) &
            (abs(self.df['MACD'].shift(1)) > abs(self.df['MACD'].shift(2)))
        )
        
        hist_positive_dates = self.df[self.df['hist_positive']].index
        hist_negative_dates = self.df[self.df['hist_negative']].index
        momentum_dates = self.df[self.df['momentum_increasing']].index
        
        print(f"柱状图由负转正（多头开始发力）:")
        for date in hist_positive_dates[-5:]:  # 只显示最近5个
            print(f"  🟢 {date.date()} - 柱状图: {self.df.loc[date, 'MACD']:.4f}")
        
        print(f"柱状图由正转负（空头开始主导）:")
        for date in hist_negative_dates[-5:]:  # 只显示最近5个
            print(f"  🔴 {date.date()} - 柱状图: {self.df.loc[date, 'MACD']:.4f}")
        
        print(f"动能持续增强信号:")
        for date in momentum_dates[-5:]:  # 只显示最近5个
            print(f"  📊 {date.date()} - 柱状图: {self.df.loc[date, 'MACD']:.4f}")
    
    def detect_squeeze_breakout(self, threshold=0.005):
        """5. 检测收敛与发散（挤压突破）"""
        print(f"\n=== 5. 收敛发散检测（阈值: {threshold}） ===")
        
        # 检测收敛（MACD线与信号线接近）
        self.df['squeeze'] = abs(self.df['DIF'] - self.df['DEA']) < threshold
        
        # 检测收敛后的突破
        self.df['breakout_up'] = (
            self.df['squeeze'].shift(1) & 
            (self.df['MACD'] > threshold * 2)
        )
        
        self.df['breakout_down'] = (
            self.df['squeeze'].shift(1) & 
            (self.df['MACD'] < -threshold * 2)
        )
        
        squeeze_dates = self.df[self.df['squeeze']].index
        breakout_up_dates = self.df[self.df['breakout_up']].index
        breakout_down_dates = self.df[self.df['breakout_down']].index
        
        print(f"收敛状态（MACD线与信号线接近）:")
        for date in squeeze_dates[-5:]:  # 只显示最近5个
            print(f"  🔄 {date.date()} - 差值: {abs(self.df.loc[date, 'DIF'] - self.df.loc[date, 'DEA']):.4f}")
        
        print(f"收敛后向上突破:")
        for date in breakout_up_dates:
            print(f"  ⬆️ 突破: {date.date()} - 柱状图: {self.df.loc[date, 'MACD']:.4f}")
        
        print(f"收敛后向下突破:")
        for date in breakout_down_dates:
            print(f"  ⬇️ 突破: {date.date()} - 柱状图: {self.df.loc[date, 'MACD']:.4f}")
    
    def generate_trading_signals(self):
        """6. 生成综合交易信号"""
        print("\n=== 6. 综合交易信号生成 ===")
        
        # 初始化信号列
        self.df['signal'] = 0  # 0: 无信号, 1: 买入, -1: 卖出
        
        # 强买入信号：金叉 + 零轴上方 + 柱状图由负转正
        strong_buy = (
            self.df['golden_cross'] & 
            (self.df['DIF'] > 0) & 
            self.df['hist_positive']
        )
        
        # 买入信号：金叉 或 零轴上穿 或 底背离
        buy_signals = (
            self.df['golden_cross'] | 
            self.df['zero_cross_up']
        )
        
        # 强卖出信号：死叉 + 零轴下方 + 柱状图由正转负
        strong_sell = (
            self.df['death_cross'] & 
            (self.df['DIF'] < 0) & 
            self.df['hist_negative']
        )
        
        # 卖出信号：死叉 或 零轴下穿 或 顶背离
        sell_signals = (
            self.df['death_cross'] | 
            self.df['zero_cross_down']
        )
        
        # 设置信号
        self.df.loc[strong_buy, 'signal'] = 2  # 强买入
        self.df.loc[buy_signals & ~strong_buy, 'signal'] = 1  # 普通买入
        self.df.loc[strong_sell, 'signal'] = -2  # 强卖出
        self.df.loc[sell_signals & ~strong_sell, 'signal'] = -1  # 普通卖出
        
        # 显示最近的交易信号
        recent_signals = self.df[self.df['signal'] != 0].tail(10)
        
        print("最近交易信号:")
        for date, row in recent_signals.iterrows():
            signal_text = {
                2: "🟢 强买入",
                1: "📈 买入", 
                -1: "📉 卖出",
                -2: "🔴 强卖出"
            }.get(row['signal'], "未知")
            
            print(f"  {signal_text}: {date.date()}")
            print(f"     价格: {row['close']:.3f}, MACD: {row['DIF']:.4f}")
            print(f"     柱状图: {row['MACD']:.4f}")
            print()
    

    def run_full_analysis(self):
        """运行完整的MACD分析"""
        print("🚀 开始MACD完整分析...")
        print("=" * 60)
        
        # 执行所有分析
        self.detect_cross_signals()
        self.detect_zero_cross()
        self.detect_divergence()
        self.analyze_MACD_momentum()
        self.detect_squeeze_breakout()
        self.generate_trading_signals()
        
        print("=" * 60)
        print("✅ MACD分析完成！")


# 使用示例
if __name__ == "__main__":
    # 创建分析器实例
    analyzer = MACDAnalyzer('sh601818_qfq_data_with_indicators.csv')
    
    # 运行完整分析
    analyzer.run_full_analysis()