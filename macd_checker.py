import numpy as np
import pandas as pd
import yaml
import os
from tools import TOOLS


def load_config():
    """加载配置文件"""
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 未找到，请创建 config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


class MACDChecker:
    """MACD信号检查类"""

    def __init__(self, stock_code="sh601818"):
        csv_file = f"{stock_code}_qfq_data_with_indicators.csv"
        self.tools = TOOLS(csv_file)
        self.stock_code = stock_code
        self.df = self.tools.df
        self.latest_two = self.tools.get_latest_two_all()

    def get_last_two_DIF_DEA_MACD(self):
        """返回前一日和当前日的 DIF, DEA, MACD"""
        prev_dif = self.df["DIF"].iloc[-2]
        curr_dif = self.df["DIF"].iloc[-1]
        prev_dea = self.df["DEA"].iloc[-2]
        curr_dea = self.df["DEA"].iloc[-1]
        prev_macd = self.df["MACD"].iloc[-2]
        curr_macd = self.df["MACD"].iloc[-1]
        return prev_dif, curr_dif, prev_dea, curr_dea, prev_macd, curr_macd

    def detect_macd_divergence(
        self, window=12, price_col="close", macd_col="DIF", window_for_peaks=3
    ):
        """
        检测 MACD 背离（作为类方法）
        :param window: 分析窗口大小（默认12）
        :param price_col: 价格列名
        :param macd_col: MACD列名（默认"DIF"）
        :param window_for_peaks: 极值点检测窗口（默认3）
        """
        df = self.df  # 使用 self.df
        recent = df.tail(window * 2).copy()
        if len(recent) < window:
            return {"divergence": "not_enough_data"}

        print(recent)

        close = recent[price_col]
        dif = recent[macd_col].ffill().fillna(0)

        # 找极值点
        price_peaks_mask, price_troughs_mask = find_peaks_and_troughs(
            close, window=window_for_peaks
        )
        dif_peaks_mask, dif_troughs_mask = find_peaks_and_troughs(
            dif, window=window_for_peaks
        )

        price_peaks = close[price_peaks_mask]
        price_troughs = close[price_troughs_mask]
        dif_peaks = dif[dif_peaks_mask]
        dif_troughs = dif[dif_troughs_mask]

        result = {
            "divergence": "no_divergence",
            "type": None,
            "strength": None,
            "details": "",
        }

        # 🔺 顶背离
        if len(price_peaks) >= 2 and len(dif_peaks) >= 2:
            latest_price_peak = price_peaks.iloc[-1]
            prev_price_peak = price_peaks.iloc[-2]
            latest_dif_peak = dif_peaks.iloc[-1]
            prev_dif_peak = dif_peaks.iloc[-2]

            if latest_price_peak > prev_price_peak and latest_dif_peak < prev_dif_peak:
                strength = "strong" if latest_dif_peak < 0 else "moderate"
                result.update(
                    {
                        "divergence": "bearish_divergence",
                        "type": "top",
                        "strength": strength,
                        "details": f"顶背离：价格↑({latest_price_peak:.2f} > {prev_price_peak:.2f}), DIF↓({latest_dif_peak:.4f} < {prev_dif_peak:.4f})",
                    }
                )
                return result

        # 🔻 底背离
        if len(price_troughs) >= 2 and len(dif_troughs) >= 2:
            latest_price_trough = price_troughs.iloc[-1]
            prev_price_trough = price_troughs.iloc[-2]
            latest_dif_trough = dif_troughs.iloc[-1]
            prev_dif_trough = dif_troughs.iloc[-2]

            if (
                latest_price_trough < prev_price_trough
                and latest_dif_trough > prev_dif_trough
            ):
                strength = "strong" if latest_dif_trough > 0 else "moderate"
                result.update(
                    {
                        "divergence": "bullish_divergence",
                        "type": "bottom",
                        "strength": strength,
                        "details": f"底背离：价格↓({latest_price_trough:.2f} < {prev_price_trough:.2f}), DIF↑({latest_dif_trough:.4f} > {prev_dif_trough:.4f})",
                    }
                )
                return result

        return result

    def get_cross_signal(self):
        """金叉与死叉 - 最简单的买卖信号"""
        # ✅ 正确方式：调用 get_last_two_DIF_DEA_MACD 获取数值
        prev_dif, curr_dif, prev_dea, curr_dea, prev_macd, curr_macd = (
            self.get_last_two_DIF_DEA_MACD()
        )

        # 金叉：DIF 上穿 DEA
        if prev_dif <= prev_dea and curr_dif > curr_dea:
            print(f"✅ {self.stock_code} 出现 MACD 金叉！买入信号")
            return "golden_cross"

        # 死叉：DIF 下穿 DEA
        elif prev_dif >= prev_dea and curr_dif < curr_dea:
            print(f"❌ {self.stock_code} 出现 MACD 死叉！卖出信号")
            return "death_cross"

        else:
            print(f"📊 {self.stock_code} 无金叉或死叉信号")
            return "no_signal"

    def get_trend_signal(self):
        """
        判断 DIF 和 DEA 是否都在零轴上方或下方
        返回趋势状态
        """
        # 获取最新一天的 DIF 和 DEA
        latest_dif = self.df["DIF"].iloc[-1]
        latest_dea = self.df["DEA"].iloc[-1]

        print(f"{self.stock_code} 当前 DIF={latest_dif:.4f}, DEA={latest_dea:.4f}")

        if latest_dif > 0 and latest_dea > 0:
            print("🟩【多头市场】DIF 和 DEA 均在零轴上方，近期股价处于上涨趋势")
            return "bullish"
        elif latest_dif < 0 and latest_dea < 0:
            print("🟥【空头市场】DIF 和 DEA 均在零轴下方，近期股价处于下跌趋势")
            return "bearish"
        else:
            print("🟨【震荡市场】DIF 和 DEA 分居零轴两侧，趋势不明确")
            return "neutral"

    def get_momentum_signal(self):
        """
        分析 MACD 柱状图的动能方向与变化
        """
        latest_macd = self.df["MACD"].iloc[-1]
        prev_macd = self.df["MACD"].iloc[-2]

        print(f"{self.stock_code} 当前 MACD 柱 = {latest_macd:.4f}")

        if latest_macd > 0:
            print("🟢 MACD 柱位于零轴上方，多头动能主导")
            momentum = "bullish_momentum"
            if prev_macd < 0:
                print("🚀【柱状图翻红】：空翻多，动能反转！强烈关注")
                momentum_change = "momentum_shift_up"
            else:
                momentum_change = "momentum_strong_up"
        elif latest_macd < 0:
            print("🔴 MACD 柱位于零轴下方，空头动能主导")
            momentum = "bearish_momentum"
            if prev_macd > 0:
                print("💀【柱状图翻绿】：多翻空，动能转弱！警惕下跌")
                momentum_change = "momentum_shift_down"
            else:
                momentum_change = "momentum_strong_down"
        else:
            print("🟨 MACD 柱为 0，动能平衡")
            momentum = "neutral"
            momentum_change = "neutral"

        return latest_macd, momentum, momentum_change

    def plot(self, window=30):
        recent = self.df.tail(window)
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # 价格图
        ax1.plot(recent['time'], recent['close'], label='Close')
        peaks, troughs = find_peaks_and_troughs(recent['close'], window=2)
        ax1.scatter(recent['time'][peaks], recent['close'][peaks], c='r', s=60, label='Peak')
        ax1.scatter(recent['time'][troughs], recent['close'][troughs], c='g', s=60, label='Trough')
        ax1.set_title(f"{self.stock_code} Price & MACD")
        ax1.legend()

        # DIF/DEA 图
        ax2.plot(recent['time'], recent['DIF'], label='DIF', color='blue')
        ax2.plot(recent['time'], recent['DEA'], label='DEA', color='orange')
        ax2.bar(recent['time'], recent['MACD'], label='MACD', alpha=0.3)
        ax2.axhline(0, color='gray', lw=0.8)
        ax2.legend()

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def run(self, divergence_window=None, peak_window=None):
        """
        🚀 终极版：融合金叉、趋势、柱状图动能的多维 MACD 分析
        :param divergence_window: 背离检测窗口（默认从配置读取）
        :param peak_window: 极值点检测窗口（默认从配置读取）
        """
        config = load_config().get("macd_checker", {})
        if divergence_window is None:
            divergence_window = config.get("divergence_window", 12)
        if peak_window is None:
            peak_window = config.get("peak_window", 3)
        print(f"🔍 终极 MACD 多维分析：{self.stock_code}")
        print("—" * 50)

        # 1️⃣ 获取金叉/死叉信号
        cross_signal = self.get_cross_signal()

        # 2️⃣ 获取趋势位置（零轴上下）
        trend_signal = self.get_trend_signal()

        # 3️⃣ 获取柱状图动能
        latest_macd, momentum, momentum_change = self.get_momentum_signal()

        # 4️⃣ 背离信
        divergence = self.detect_macd_divergence(
            window=divergence_window, window_for_peaks=peak_window
        )
        div_type = divergence.get("type")
        div_strength = divergence.get("strength")

        # === 开始融合判断 ===
        score = 0  # 评分系统：越高越强

        # ✅ 1. 金叉信号加分
        if cross_signal == "golden_cross":
            score += 2
            print("✅【金叉确认】DIF 上穿 DEA，买入信号成立")
        elif cross_signal == "death_cross":
            score -= 2
            print("❌【死叉确认】DIF 下穿 DEA，卖出信号成立")

        # ✅ 2. 趋势方向加分
        if trend_signal == "bullish":
            score += 1
            print("🟩【趋势向上】DIF & DEA > 0，多头市场")
        elif trend_signal == "bearish":
            score -= 1
            print("🟥【趋势向下】DIF & DEA < 0，空头市场")

        # ✅ 3. 柱状图动能加分
        if momentum == "bullish_momentum":
            score += 1
            print("🟢【多头动能】MACD 柱 > 0，上涨动力足")
        elif momentum == "bearish_momentum":
            score -= 1
            print("🔴【空头动能】MACD 柱 < 0，下跌压力大")

        # ✅ 4. 动能转折（翻红/翻绿）重点加分
        if momentum_change == "momentum_shift_up":
            score += 2
            print("🚀【动能反转】柱状图由负转正，空翻多！强烈关注")
        elif momentum_change == "momentum_shift_down":
            score -= 2
            print("💀【动能转弱】柱状图由正转负，多翻空！警惕风险")

        # ✅ 新增：背离修正
        if div_type == "top":
            score -= 3
            print("⚠️【顶背离修正】信号强度大幅下调！")
        elif div_type == "bottom":
            score += 3
            print("🔥【底背离确认】反转信号增强！强烈关注！")

        # === 综合评分决策 ===
        if score >= 4:
            combined = "strong_buy"
            advice = "✅ 强烈买入：趋势、动能、信号三重确认！可重仓做多"
        elif score >= 2:
            combined = "buy"
            advice = "🟢 可买入：信号有效，趋势配合，建议介入"
        elif score >= 0:
            combined = "hold"
            advice = "🟡 持有或观望：无明确方向，等待突破"
        elif score >= -2:
            combined = "sell"
            advice = "🔴 建议卖出：趋势偏弱，谨慎持有"
        else:
            combined = "strong_sell"
            advice = "❌ 强烈卖出：空头三重确认，建议清仓或做空"

        print(f"\n🏆 综合评分: {score}")
        print(f"💡 交易建议: {advice}")
        print(f"🎯 最终信号: {combined}")

        # 返回完整结果
        return {
            "stock_code": self.stock_code,
            "cross_signal": cross_signal,
            "trend_signal": trend_signal,
            "momentum": momentum,
            "momentum_change": momentum_change,
            "latest_macd": float(latest_macd),
            "score": score,
            "advice": advice,
            "combined_signal": combined,
            "divergence_type": div_type,
            "divergence_strength": div_strength,
            "divergence_details": divergence.get("details", ""),
        }

if __name__ == "__main__":
    # 构造测试数据
    test_data = pd.DataFrame({
        "time": pd.date_range("2024-11-25", periods=12),
        "close": [4.60, 4.50, 4.45, 4.55, 4.60, 4.50, 4.40, 4.35, 4.45, 4.55, 4.65, 4.75],
        "DIF":   [0.020, 0.015, 0.010, 0.012, 0.018, 0.016, 0.014, 0.015, 0.020, 0.025, 0.030, 0.035],
        "DEA":   [0.0] * 12,
        "MACD":  [0.0] * 12,
        "K":     [0.0] * 12,
        "D":     [0.0] * 12,
        "J":     [0.0] * 12,
        "RSI":   [0.0] * 12,
        "open":  [4.6]*12,
        "high":  [4.7]*12,
        "low":   [4.4]*12,
        "volume":[100000]*12,
    }).reset_index().rename(columns={'index': 'time'})

    # 保存为 CSV，让 TOOLS 能读取
    test_code = "TEST_BACKWARD"
    test_data.to_csv(f"{test_code}_qfq_data_with_indicators.csv", index=False)

    # 使用真实 MACDChecker
    checker = MACDChecker(stock_code=test_code)
    result = checker.detect_macd_divergence(window=10, window_for_peaks=2)

    print("\n" + "="*60)
    print("🧪 底背离测试结果")
    print("="*60)
    print(f"检测到: {result['divergence']}")
    print(f"类型: {result['type']}")
    print(f"详情: {result['details']}")
    checker.plot()

