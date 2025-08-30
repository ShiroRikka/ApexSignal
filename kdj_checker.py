# kdj_checker.py
import os
import pandas as pd
import logging
from tools import TOOLS


def find_peaks_and_troughs(series, window=2):
    s = series.copy().ffill().bfill()
    w = 2 * window + 1
    roll_max = s.rolling(window=w, center=True, min_periods=1).max()
    roll_min = s.rolling(window=w, center=True, min_periods=1).min()
    peak_mask = (s == roll_max) & s.notna()
    trough_mask = (s == roll_min) & s.notna()
    return peak_mask.values, trough_mask.values


class KdjChecker:
    def __init__(self, stock_code: str, config=None):
        self.config = config
        self.stock_code = stock_code
        self.logger = logging.getLogger("ApexSignal")

        # 加载配置
        signal_config = self.config.get("signal_checker", {}).get("kdj", {})
        self.overbought = signal_config.get("overbought", 80)
        self.oversold = signal_config.get("oversold", 20)
        self.divergence_window = signal_config.get("divergence_window", 12)
        self.peak_window = signal_config.get("peak_window", 3)

        # 加载数据
        cache_dir = self.config.get("data_updater", {}).get("cache_dir", ".")
        csv_file = os.path.join(cache_dir, f"{stock_code}_qfq_data_with_indicators.csv")
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"数据文件不存在: {csv_file}")

        self.tools = TOOLS(csv_file)
        self.df = self.tools.df

        if self.df.empty:
            raise ValueError("数据为空")

        self.latest_k = self.df["K"].iloc[-1]
        self.latest_d = self.df["D"].iloc[-1]
        self.latest_j = self.df["J"].iloc[-1]

    def detect_kdj_divergence(self):
        """检测 KDJ 背离"""
        window = self.divergence_window
        peak_window = self.peak_window
        df = self.df.tail(window * 2).copy()
        if len(df) < window:
            return {"divergence": "not_enough_data"}

        close = df["close"]
        k = df["K"].ffill().fillna(0)

        close_peaks, close_troughs = find_peaks_and_troughs(close, peak_window)
        k_peaks, k_troughs = find_peaks_and_troughs(k, peak_window)

        close_p = close[close_peaks]
        close_t = close[close_troughs]
        k_p = k[k_peaks]
        k_t = k[k_troughs]

        result = {"divergence": "no_divergence", "type": None, "details": ""}

        # 顶背离
        if len(close_p) >= 2 and len(k_p) >= 2:
            if close_p.iloc[-1] > close_p.iloc[-2] and k_p.iloc[-1] < k_p.iloc[-2]:
                result.update({
                    "divergence": "bearish_divergence",
                    "type": "top",
                    "details": f"KDJ顶背离：价↑ K↓ ({k_p.iloc[-1]:.2f} < {k_p.iloc[-2]:.2f})"
                })
                return result

        # 底背离
        if len(close_t) >= 2 and len(k_t) >= 2:
            if close_t.iloc[-1] < close_t.iloc[-2] and k_t.iloc[-1] > k_t.iloc[-2]:
                result.update({
                    "divergence": "bullish_divergence",
                    "type": "bottom",
                    "details": f"KDJ底背离：价↓ K↑ ({k_t.iloc[-1]:.2f} > {k_t.iloc[-2]:.2f})"
                })
                return result

        return result

    def run(self):
        self.logger.info(f"🔍 KDJ 分析：{self.stock_code}")
        print("-" * 50)

        score = 0

        # 超买超卖
        if self.latest_k <= self.oversold:
            score += 3
            print("✅【K值超卖】K≤20，强烈反弹预期！")
        elif self.latest_k >= self.overbought:
            score -= 3
            print("❌【K值超买】K≥80，谨防回调！")

        # 金叉/死叉
        if self.df["K"].iloc[-2] <= self.df["D"].iloc[-2] and self.latest_k > self.latest_d:
            score += 2
            print("✅【K上穿D】金叉形成，看涨！")
        elif self.df["K"].iloc[-2] >= self.df["D"].iloc[-2] and self.latest_k < self.latest_d:
            score -= 2
            print("❌【K下穿D】死叉形成，看跌！")

        # J值极端
        if self.latest_j > 100:
            score -= 2
            print("⚠️【J>100】严重超买")
        elif self.latest_j < 0:
            score += 2
            print("🔥【J<0】深度超卖")

        # 背离
        divergence = self.detect_kdj_divergence()
        if divergence["type"] == "bottom":
            score += 3
            print("🔥【KDJ底背离】反转信号增强！")
        elif divergence["type"] == "top":
            score -= 3
            print("⚠️【KDJ顶背离】上涨动能衰竭")

        # 决策
        if score >= 4:
            advice = "✅ 强烈买入"
            signal = "strong_buy"
        elif score >= 2:
            advice = "🟢 可买入"
            signal = "buy"
        elif score >= -2:
            advice = "🟡 持平"
            signal = "hold"
        else:
            advice = "🔴 建议卖出"
            signal = "sell"

        print(f"\n🏆 综合评分: {score}")
        print(f"💡 建议: {advice}")

        return {
            "stock_code": self.stock_code,
            "k_value": float(self.latest_k),
            "d_value": float(self.latest_d),
            "j_value": float(self.latest_j),
            "score": score,
            "advice": advice,
            "combined_signal": signal,
            "divergence": divergence["type"],
            "divergence_details": divergence["details"]
        }

    def plot(self, window=30):
        output_config = self.config.get("output", {})
        show_plot = output_config.get("show_plot", True)
        plot_save_dir = output_config.get("plot_save_dir", None)

        if not show_plot and not plot_save_dir:
            self.logger.info("图表显示和保存均已禁用，跳过绘图。")
            return

        import matplotlib.pyplot as plt
        recent = self.df.tail(window)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        ax1.plot(recent['time'], recent['close'], label='Close')
        ax1.set_title(f"{self.stock_code} - Price & KDJ")
        ax1.legend()

        ax2.plot(recent['time'], recent['K'], label='K', color='blue')
        ax2.plot(recent['time'], recent['D'], label='D', color='orange')
        ax2.plot(recent['time'], recent['J'], label='J', color='purple')
        ax2.axhline(80, color='r', linestyle='--', alpha=0.5)
        ax2.axhline(20, color='g', linestyle='--', alpha=0.5)
        ax2.set_ylim(0, 100)
        ax2.legend()

        plt.xticks(rotation=45)
        plt.tight_layout()

        if show_plot:
            plt.show()
        if plot_save_dir:
            os.makedirs(plot_save_dir, exist_ok=True)
            path = os.path.join(plot_save_dir, f"{self.stock_code}_kdj_analysis.png")
            plt.savefig(path)
            self.logger.info(f"📈 KDJ 图表已保存至: {path}")
        plt.close()
