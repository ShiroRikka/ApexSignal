import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

class SimpleMACD:
    """最简单的MACD用法演示"""
    
    def __init__(self, csv_file):
        """加载数据"""
        self.df = pd.read_csv(csv_file)
        self.df['time'] = pd.to_datetime(self.df['time'])
        self.df.set_index('time', inplace=True)
        
        # 重命名列名，使其更直观
        self.df.rename(columns={
            'DIF': 'macd_line',
            'DEA': 'signal_line', 
            'MACD': 'histogram'
        }, inplace=True)
        
        print(f"数据加载完成，共 {len(self.df)} 条记录")
    
    def golden_cross_death_cross(self):
        """用法1：金叉与死叉 - 最简单的买卖信号"""
        print("\n📈 用法1：金叉与死叉")
        print("=" * 40)
        
        # 金叉：MACD线从下向上穿过信号线
        golden_cross = (
            (self.df['macd_line'] > self.df['signal_line']) & 
            (self.df['macd_line'].shift(1) <= self.df['signal_line'].shift(1))
        )
        
        # 死叉：MACD线从上向下穿过信号线
        death_cross = (
            (self.df['macd_line'] < self.df['signal_line']) & 
            (self.df['macd_line'].shift(1) >= self.df['signal_line'].shift(1))
        )
        
        print("金叉信号（买入）:")
        for date in self.df[golden_cross].index:
            print(f"  ✅ {date.date()}: 价格={self.df.loc[date, 'close']:.3f}")
        
        print("\n死叉信号（卖出）:")
        for date in self.df[death_cross].index:
            print(f"  ❌ {date.date()}: 价格={self.df.loc[date, 'close']:.3f}")
    
    def zero_line_cross(self):
        """用法2：零轴穿越 - 判断多空趋势"""
        print("\n⬆️⬇️ 用法2：零轴穿越")
        print("=" * 40)
        
        # 上穿零轴：多头信号
        zero_up = (
            (self.df['macd_line'] > 0) & 
            (self.df['macd_line'].shift(1) <= 0)
        )
        
        # 下穿零轴：空头信号
        zero_down = (
            (self.df['macd_line'] < 0) & 
            (self.df['macd_line'].shift(1) >= 0)
        )
        
        print("上穿零轴（多头市场）:")
        for date in self.df[zero_up].index:
            print(f"  📊 {date.date()}: MACD={self.df.loc[date, 'macd_line']:.4f}")
        
        print("\n下穿零轴（空头市场）:")
        for date in self.df[zero_down].index:
            print(f"  📊 {date.date()}: MACD={self.df.loc[date, 'macd_line']:.4f}")
    
    def divergence_simple(self):
        """用法3：背离 - 趋势反转信号"""
        print("\n🔄 用法3：背离检测")
        print("=" * 40)
        
        # 简化版背离检测
        window = 15
        
        # 找价格和MACD的高点和低点
        price_highs = argrelextrema(self.df['close'].values, np.greater, order=window)[0]
        price_lows = argrelextrema(self.df['close'].values, np.less, order=window)[0]
        macd_highs = argrelextrema(self.df['macd_line'].values, np.greater, order=window)[0]
        macd_lows = argrelextrema(self.df['macd_line'].values, np.less, order=window)[0]
        
        print("顶背离（价格新高，MACD不新高）:")
        for i in range(2, len(price_highs)):
            price_date = self.df.index[price_highs[i]]
            price_idx = price_highs[i]
            
            # 找到最接近但早于当前价格高点的MACD高点
            relevant_macd_highs = [m for m in macd_highs if m < price_idx]
            if len(relevant_macd_highs) >= 2:
                # 取最近的两个MACD高点
                macd_highs_sorted = sorted(relevant_macd_highs)
                current_macd_idx = macd_highs_sorted[-1]
                prev_macd_idx = macd_highs_sorted[-2]
                
                # 检查顶背离：价格创新高但MACD没有
                if (self.df['close'].iloc[price_idx] > self.df['close'].iloc[price_highs[i-1]] and
                    self.df['macd_line'].iloc[current_macd_idx] < self.df['macd_line'].iloc[prev_macd_idx]):
                    print(f"  ⚠️  {price_date.date()}: 注意可能的顶部反转")
                    print(f"      价格: {self.df['close'].iloc[price_idx]:.3f} > {self.df['close'].iloc[price_highs[i-1]]:.3f}")
                    print(f"      MACD: {self.df['macd_line'].iloc[current_macd_idx]:.4f} < {self.df['macd_line'].iloc[prev_macd_idx]:.4f}")
        
        print("\n底背离（价格新低，MACD不新低）:")
        for i in range(2, len(price_lows)):
            price_date = self.df.index[price_lows[i]]
            price_idx = price_lows[i]
            
            # 找到最接近但早于当前价格低点的MACD低点
            relevant_macd_lows = [m for m in macd_lows if m < price_idx]
            if len(relevant_macd_lows) >= 2:
                # 取最近的两个MACD低点
                macd_lows_sorted = sorted(relevant_macd_lows)
                current_macd_idx = macd_lows_sorted[-1]
                prev_macd_idx = macd_lows_sorted[-2]
                
                # 检查底背离：价格创新低但MACD没有
                if (self.df['close'].iloc[price_idx] < self.df['close'].iloc[price_lows[i-1]] and
                    self.df['macd_line'].iloc[current_macd_idx] > self.df['macd_line'].iloc[prev_macd_idx]):
                    print(f"  ✅ {price_date.date()}: 注意可能的底部反弹")
                    print(f"      价格: {self.df['close'].iloc[price_idx]:.3f} < {self.df['close'].iloc[price_lows[i-1]]:.3f}")
                    print(f"      MACD: {self.df['macd_line'].iloc[current_macd_idx]:.4f} > {self.df['macd_line'].iloc[prev_macd_idx]:.4f}")
    
    def histogram_momentum(self):
        """用法4：柱状图动能 - 观察涨跌力度"""
        print("\n📊 用法4：柱状图动能")
        print("=" * 40)
        
        # 柱状图由负转正：多头开始发力
        hist_positive = (
            (self.df['histogram'] > 0) & 
            (self.df['histogram'].shift(1) <= 0)
        )
        
        # 柱状图由正转负：空头开始主导
        hist_negative = (
            (self.df['histogram'] < 0) & 
            (self.df['histogram'].shift(1) >= 0)
        )
        
        print("柱状图由负转正（多头发力）:")
        for date in self.df[hist_positive].index:
            print(f"  🟢 {date.date()}: 柱状图={self.df.loc[date, 'histogram']:.4f}")
        
        print("\n柱状图由正转负（空头主导）:")
        for date in self.df[hist_negative].index:
            print(f"  🔴 {date.date()}: 柱状图={self.df.loc[date, 'histogram']:.4f}")
        
        # 动能增强：柱状图持续放大
        momentum_strong = (
            (abs(self.df['histogram']) > abs(self.df['histogram'].shift(1))) &
            (abs(self.df['histogram'].shift(1)) > abs(self.df['histogram'].shift(2)))
        )
        
        print(f"\n动能持续增强（最近5次）:")
        strong_dates = self.df[momentum_strong].tail(5).index
        for date in strong_dates:
            print(f"  💪 {date.date()}: 柱状图={self.df.loc[date, 'histogram']:.4f}")
    
    def squeeze_breakout(self):
        """用法5：收敛发散 - 预判趋势启动"""
        print("\n🎯 用法5：收敛发散")
        print("=" * 40)
        
        threshold = 0.005
        
        # 收敛：MACD线与信号线接近
        squeeze = abs(self.df['macd_line'] - self.df['signal_line']) < threshold
        
        # 收敛后突破
        breakout_up = (
            squeeze.shift(1) & 
            (self.df['histogram'] > threshold * 2)
        )
        
        breakout_down = (
            squeeze.shift(1) & 
            (self.df['histogram'] < -threshold * 2)
        )
        
        print("收敛状态（准备突破）:")
        squeeze_dates = self.df[squeeze].tail(5).index
        for date in squeeze_dates:
            diff = abs(self.df.loc[date, 'macd_line'] - self.df.loc[date, 'signal_line'])
            print(f"  🔄 {date.date()}: 差值={diff:.4f}")
        
        print("\n收敛后向上突破:")
        for date in self.df[breakout_up].index:
            print(f"  ⬆️ {date.date()}: 柱状图={self.df.loc[date, 'histogram']:.4f}")
        
        print("\n收敛后向下突破:")
        for date in self.df[breakout_down].index:
            print(f"  ⬇️ {date.date()}: 柱状图={self.df.loc[date, 'histogram']:.4f}")
    
    def simple_trading_signals(self):
        """用法6：综合交易信号"""
        print("\n💰 用法6：综合交易信号")
        print("=" * 40)
        
        # 买入信号：金叉 或 零轴上穿
        buy_signals = (
            ((self.df['macd_line'] > self.df['signal_line']) & (self.df['macd_line'].shift(1) <= self.df['signal_line'].shift(1))) |
            ((self.df['macd_line'] > 0) & (self.df['macd_line'].shift(1) <= 0))
        )
        
        # 卖出信号：死叉 或 零轴下穿
        sell_signals = (
            ((self.df['macd_line'] < self.df['signal_line']) & (self.df['macd_line'].shift(1) >= self.df['signal_line'].shift(1))) |
            ((self.df['macd_line'] < 0) & (self.df['macd_line'].shift(1) >= 0))
        )
        
        print("买入信号:")
        buy_dates = self.df[buy_signals].tail(5).index
        for date in buy_dates:
            price = self.df.loc[date, 'close']
            macd = self.df.loc[date, 'macd_line']
            print(f"  📈 {date.date()}: 价格={price:.3f}, MACD={macd:.4f}")
        
        print("\n卖出信号:")
        sell_dates = self.df[sell_signals].tail(5).index
        for date in sell_dates:
            price = self.df.loc[date, 'close']
            macd = self.df.loc[date, 'macd_line']
            print(f"  📉 {date.date()}: 价格={price:.3f}, MACD={macd:.4f}")
    
    def run_all(self):
        """运行所有MACD用法演示"""
        print("🎯 MACD六大用法简单演示")
        print("=" * 60)
        
        self.golden_cross_death_cross()
        self.zero_line_cross()
        self.divergence_simple()
        self.histogram_momentum()
        self.squeeze_breakout()
        self.simple_trading_signals()
        
        print("\n" + "=" * 60)
        print("✅ 所有MACD用法演示完成！")

# 使用示例
if __name__ == "__main__":
    # 创建简单MACD分析器
    macd = SimpleMACD('sh601818_qfq_data_with_indicators.csv')
    
    # 运行所有用法演示
    macd.run_all()