import numpy as np

from tools import TOOLS


def find_peaks_and_troughs(series, window=3):
    """
    找出序列中的局部高点（峰值）和低点（谷值）
    返回：两个布尔数组，peak_mask 和 trough_mask
    """
    # 创建副本避免警告
    s = series.copy()
    s = s.ffill().bfill()  # 修复警告
    values = s.values  # 转为 numpy 数组，按位置访问
    peak_mask = np.zeros(len(values), dtype=bool)
    trough_mask = np.zeros(len(values), dtype=bool)

    for i in range(window, len(values) - window):
        # 检查是否是局部最大值
        if all(values[i] >= values[i - j] for j in range(1, window + 1)) and all(
            values[i] >= values[i + j] for j in range(1, window + 1)
        ):
            peak_mask[i] = True

        # 检查是否是局部最小值
        if all(values[i] <= values[i - j] for j in range(1, window + 1)) and all(
            values[i] <= values[i + j] for j in range(1, window + 1)
        ):
            trough_mask[i] = True

    return peak_mask, trough_mask


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
        """
        df = self.df  # 使用 self.df
        recent = df.tail(window * 2).copy()
        if len(recent) < window:
            return {"divergence": "not_enough_data"}

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

    def run(self, divergence_window=12, peak_window=3):
        """
        🚀 终极版：融合金叉、趋势、柱状图动能的多维 MACD 分析
        """
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
    checker = MACDChecker("sh601288")

    print("🧪 测试1：宽松背离检测（window=20, peak_window=4）")
    result1 = checker.run(divergence_window=20, peak_window=4)

    print("\n\n🧪 测试2：严格背离检测（window=8, peak_window=2）")
    result2 = checker.run(divergence_window=8, peak_window=2)

    print("\n\n🧪 测试3：默认参数")
    result3 = checker.run()

