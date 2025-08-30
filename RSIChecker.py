# -*- coding: utf-8 -*-
"""
rsi_checker.py
RSI 超买超卖 + 背离 + 拐点 多维信号检查器
"""
import os
import numpy as np
import pandas as pd
import logging
from typing import Dict, Tuple
from tools import TOOLS

# --- 复用极值点检测函数 ---
def find_peaks_and_troughs(series, window=2):
    """
    使用中心滚动窗口找局部峰值和谷值
    """
    s = series.copy().ffill().bfill()
    w = 2 * window + 1  # 窗口大小
    roll_max = s.rolling(window=w, center=True, min_periods=1).max()
    roll_min = s.rolling(window=w, center=True, min_periods=1).min()

    peak_mask = (s == roll_max) & (s.notna())
    trough_mask = (s == roll_min) & (s.notna())

    return peak_mask.values, trough_mask.values


class RsiChecker:
    """RSI信号检查类"""

    def __init__(self, stock_code: str, config=None):
        self.config = config
        self.stock_code = stock_code
        self.logger = logging.getLogger("ApexSignal")  # 全局logger

        # 加载配置参数
        rsi_config = self.config.get("indicators", {}).get("rsi", {})
        signal_config = self.config.get("signal_checker", {}).get("rsi", {})

        self.rsi_period = rsi_config.get("period", 14)
        self.overbought = signal_config.get("overbought", 70)
        self.oversold = signal_config.get("oversold", 30)
        self.weak_buy_zone = signal_config.get("weak_buy_zone", 35)   # 弱买入区
        self.weak_sell_zone = signal_config.get("weak_sell_zone", 65) # 弱卖出区
        self.divergence_window = signal_config.get("divergence_window", 12)
        self.peak_window = signal_config.get("peak_window", 3)

        # 数据加载
        cache_dir = self.config.get("data_updater", {}).get("cache_dir", ".")
        csv_file = os.path.join(cache_dir, f"{stock_code}_qfq_data_with_indicators.csv")
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"数据文件不存在: {csv_file}")

        self.tools = TOOLS(csv_file)
        self.df = self.tools.df

        if self.df.empty:
            raise ValueError(f"数据文件 {csv_file} 为空")

        self.latest_rsi = self.df["RSI"].iloc[-1]
        self.prev_rsi = self.df["RSI"].iloc[-2]

    def get_price_trend(self, window=5):
        """判断近期价格趋势（简单均线法）"""
        close = self.df["close"]
        ma = close.rolling(window).mean()
        latest_close = close.iloc[-1]
        latest_ma = ma.iloc[-1]
        if latest_close > latest_ma:
            return "above_ma"
        elif latest_close < latest_ma:
            return "below_ma"
        else:
            return "near_ma"

    def detect_rsi_divergence(self, window=None, price_col="close", rsi_col="RSI", peak_window=None):
        """检测 RSI 背离"""
        if window is None:
            window = self.divergence_window
        if peak_window is None:
            peak_window = self.peak_window

        df = self.df
        recent = df.tail(window * 2).copy()
        if len(recent) < window:
            return {"divergence": "not_enough_data"}

        price = recent[price_col]
        rsi = recent[rsi_col].ffill().fillna(0)

        price_peaks_mask, price_troughs_mask = find_peaks_and_troughs(price, window=peak_window)
        rsi_peaks_mask, rsi_troughs_mask = find_peaks_and_troughs(rsi, window=peak_window)

        price_peaks = price[price_peaks_mask]
        price_troughs = price[price_troughs_mask]
        rsi_peaks = rsi[rsi_peaks_mask]
        rsi_troughs = rsi[rsi_troughs_mask]

        result = {
            "divergence": "no_divergence",
            "type": None,
            "strength": None,
            "details": "",
        }

        # 🔺 顶背离：价格创新高，RSI未创新高
        if len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
            latest_price_peak = price_peaks.iloc[-1]
            prev_price_peak = price_peaks.iloc[-2]
            latest_rsi_peak = rsi_peaks.iloc[-1]
            prev_rsi_peak = rsi_peaks.iloc[-2]

            if latest_price_peak > prev_price_peak and latest_rsi_peak < prev_rsi_peak:
                strength = "strong" if latest_rsi_peak > self.overbought else "moderate"
                result.update({
                    "divergence": "bearish_divergence",
                    "type": "top",
                    "strength": strength,
                    "details": f"顶背离：价格↑({latest_price_peak:.2f} > {prev_price_peak:.2f}), RSI↓({latest_rsi_peak:.2f} < {prev_rsi_peak:.2f})"
                })
                return result

        # 🔻 底背离：价格创新低，RSI未创新低
        if len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
            latest_price_trough = price_troughs.iloc[-1]
            prev_price_trough = price_troughs.iloc[-2]
            latest_rsi_trough = rsi_troughs.iloc[-1]
            prev_rsi_trough = rsi_troughs.iloc[-2]

            if latest_price_trough < prev_price_trough and latest_rsi_trough > prev_rsi_trough:
                strength = "strong" if latest_rsi_trough < self.oversold else "moderate"
                result.update({
                    "divergence": "bullish_divergence",
                    "type": "bottom",
                    "strength": strength,
                    "details": f"底背离：价格↓({latest_price_trough:.2f} < {prev_price_trough:.2f}), RSI↑({latest_rsi_trough:.2f} > {prev_rsi_trough:.2f})"
                })
                return result

        return result

    def get_extreme_signal(self):
        """超买超卖信号"""
        rsi = self.latest_rsi
        if rsi <= self.oversold:
            self.logger.info(f"✅ {self.stock_code} RSI={rsi:.2f} ≤ {self.oversold}，进入超卖区！")
            return "oversold"
        elif rsi >= self.overbought:
            self.logger.info(f"❌ {self.stock_code} RSI={rsi:.2f} ≥ {self.overbought}，进入超买区！")
            return "overbought"
        elif rsi <= self.weak_buy_zone:
            self.logger.info(f"🟡 {self.stock_code} RSI={rsi:.2f} ≤ {self.weak_buy_zone}，接近超卖区，关注反弹")
            return "weak_oversold"
        elif rsi >= self.weak_sell_zone:
            self.logger.info(f"🟠 {self.stock_code} RSI={rsi:.2f} ≥ {self.weak_sell_zone}，接近超买区，警惕回调")
            return "weak_overbought"
        else:
            self.logger.info(f"📊 {self.stock_code} RSI={rsi:.2f}，处于中性区间")
            return "neutral"

    def get_momentum_signal(self):
        """RSI 动能方向变化（拐头）"""
        if self.prev_rsi < self.latest_rsi:
            self.logger.info(f"🚀 RSI 拐头向上：{self.prev_rsi:.2f} → {self.latest_rsi:.2f}，空翻多！")
            return "rsi_upward_momentum"
        elif self.prev_rsi > self.latest_rsi:
            self.logger.info(f"💀 RSI 拐头向下：{self.prev_rsi:.2f} → {self.latest_rsi:.2f}，多翻空！")
            return "rsi_downward_momentum"
        else:
            return "rsi_flat"

    def plot(self, window=30):
        """绘制价格与RSI图表"""
        output_config = self.config.get("output", {})
        show_plot = output_config.get("show_plot", True)
        plot_save_dir = output_config.get("plot_save_dir", None)

        if not show_plot and not plot_save_dir:
            self.logger.info("图表显示和保存均已禁用，跳过绘图。")
            return

        import matplotlib.pyplot as plt
        recent = self.df.tail(window)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # 价格图
        ax1.plot(recent.index, recent['close'], label='Close Price')
        ax1.set_title(f"{self.stock_code} - Price & RSI")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # RSI 图
        ax2.plot(recent.index, recent['RSI'], label='RSI', color='purple')
        ax2.axhline(self.overbought, color='r', linestyle='--', alpha=0.7, label=f'Overbought ({self.overbought})')
        ax2.axhline(self.oversold, color='g', linestyle='--', alpha=0.7, label=f'Oversold ({self.oversold})')
        ax2.axhline(50, color='gray', linestyle='-', alpha=0.5)
        ax2.set_ylim(0, 100)
        ax2.set_ylabel("RSI")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.xticks(rotation=45)
        plt.tight_layout()

        if show_plot:
            plt.show()
        if plot_save_dir:
            os.makedirs(plot_save_dir, exist_ok=True)
            save_path = os.path.join(plot_save_dir, f"{self.stock_code}_rsi_analysis.png")
            plt.savefig(save_path)
            self.logger.info(f"📈 RSI 图表已保存至: {save_path}")
        plt.close()

    def run(self):
        """🚀 RSI 多维信号融合分析"""
        self.logger.info(f"🔍 RSI 多维分析：{self.stock_code}")
        print("-" * 50)

        # 1️⃣ 超买超卖信号
        extreme_signal = self.get_extreme_signal()

        # 2️⃣ 动能拐点
        momentum_signal = self.get_momentum_signal()

        # 3️⃣ 趋势位置
        trend_status = self.get_price_trend()
        if trend_status == "above_ma":
            print("🟩【趋势向上】价格位于5日均线上方")
        elif trend_status == "below_ma":
            print("🟥【趋势向下】价格位于5日均线下方")
        else:
            print("🟨【震荡中】价格贴近5日均线")

        # 4️⃣ 背离检测
        divergence = self.detect_rsi_divergence()
        div_type = divergence.get("type")
        div_details = divergence.get("details", "")

        # === 评分系统 ===
        score = 0

        if extreme_signal == "oversold":
            score += 3
            print("✅【严重超卖】极强反弹预期！")
        elif extreme_signal == "weak_oversold":
            score += 1
            print("🟡【接近超卖】关注反弹机会")

        if extreme_signal == "overbought":
            score -= 3
            print("❌【严重超买】谨防回调！")
        elif extreme_signal == "weak_overbought":
            score -= 1
            print("🟠【接近超买】注意止盈")

        if momentum_signal == "rsi_upward_momentum":
            score += 2
            print("🚀【RSI拐头向上】动能反转，看涨！")
        elif momentum_signal == "rsi_downward_momentum":
            score -= 2
            print("💀【RSI拐头向下】动能转弱，看跌！")

        if div_type == "bottom":
            score += 3
            print(f"🔥【底背离确认】{div_details}")
        elif div_type == "top":
            score -= 3
            print(f"⚠️【顶背离警告】{div_details}")

        # === 最终决策 ===
        if score >= 4:
            advice = "✅ 强烈买入：超卖+拐头+背离三重确认！"
            signal = "strong_buy"
        elif score >= 2:
            advice = "🟢 可买入：信号明确，建议介入"
            signal = "buy"
        elif score >= -1:
            advice = "🟡 持平观望：无明确方向"
            signal = "hold"
        elif score >= -3:
            advice = "🔴 建议卖出：弱势明显"
            signal = "sell"
        else:
            advice = "❌ 强烈卖出：多空信号共振下行"
            signal = "strong_sell"

        print(f"\n🏆 综合评分: {score}")
        print(f"💡 交易建议: {advice}")
        print(f"🎯 最终信号: {signal}")

        return {
            "stock_code": self.stock_code,
            "rsi_value": float(self.latest_rsi),
            "extreme_signal": extreme_signal,
            "momentum_signal": momentum_signal,
            "price_trend": trend_status,
            "divergence_type": div_type,
            "divergence_details": div_details,
            "score": score,
            "advice": advice,
            "combined_signal": signal,
        }
