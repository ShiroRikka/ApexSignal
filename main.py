# main.py
from data_updater import update_stock_data, load_config
from macd_checker import MacdChecker
from rsi_checker import RsiChecker
from kdj_checker import KdjChecker
import os
import logging

def setup_logger(config):
    level = getattr(logging, config.get("output", {}).get("log_level", "INFO").upper())
    logger = logging.getLogger("ApexSignal")
    logger.setLevel(level)

    if not logger.handlers:
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)

        # 可选：添加文件日志
        log_dir = config.get("output", {}).get("log_dir", "./logs")
        os.makedirs(log_dir, exist_ok=True)
        fh = logging.FileHandler(f"{log_dir}/apexsignal.log", encoding='utf-8')
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def get_stock_list(config):
    """从配置获取股票列表"""
    stock_pool_config = config.get("stock_pool", {})
    file_path = stock_pool_config.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(f"⚠️ 从文件 {file_path} 读取股票列表失败: {e}")
    static_list = stock_pool_config.get("static_list", [])
    if static_list:
        return static_list
    else:
        print("⚠️ 配置文件中未找到有效的股票列表。")
        return []


def main():
    config = load_config()
    logger = setup_logger(config)
    stock_list = get_stock_list(config)

    if not stock_list:
        print("❌ 没有找到要分析的股票。")
        return

    results = []
    for code in stock_list:
        print(f"\n{'=' * 60}")
        print(f"🔄 正在分析股票: {code}")

        # 更新数据
        df = update_stock_data(code, config)
        if df is None:
            continue

        # === MACD 分析 ===
        try:
            macd_checker = MacdChecker(code, config=config)
            macd_result = macd_checker.run()
            macd_checker.plot()
        except Exception as e:
            print(f"❌ MACD 分析失败: {e}")
            macd_result = {"score": 0, "combined_signal": "error"}

        # === RSI 分析 ===
        try:
            rsi_checker = RsiChecker(code, config=config)
            rsi_result = rsi_checker.run()
            rsi_checker.plot()
        except Exception as e:
            print(f"❌ RSI 分析失败: {e}")
            rsi_result = {"score": 0, "combined_signal": "error"}

        try:
            kdj_checker = KdjChecker(code, config=config)
            kdj_result = kdj_checker.run()
            kdj_checker.plot()
        except Exception as e:
            print(f"❌ KDJ 分析失败: {e}")
            kdj_result = {"score": 0, "combined_signal": "error"}

        # === 三因子融合信号 ===
        combined_score = (
                macd_result.get("score", 0) +
                rsi_result.get("score", 0) +
                kdj_result.get("score", 0)
        )

        final_signal = "strong_buy" if combined_score >= 8 else \
            "buy" if combined_score >= 4 else \
                "hold" if combined_score >= -2 else \
                    "sell" if combined_score >= -6 else \
                        "strong_sell"

        # 保存结果
        results.append({
            "stock_code": code,
            "macd_score": macd_result.get("score", 0),
            "rsi_score": rsi_result.get("score", 0),
            "kdj_score": kdj_result.get("score", 0),
            "combined_score": combined_score,
            "final_signal": final_signal,
            "macd_advice": macd_result.get("advice", ""),
            "rsi_advice": rsi_result.get("advice", ""),
            "kdj_advice": kdj_result.get("advice", "")
        })

    # 保存结果
    output_config = config.get("output", {})
    csv_output_dir = output_config.get("csv_output_dir", None)
    if csv_output_dir and results:
        os.makedirs(csv_output_dir, exist_ok=True)
        import pandas as pd
        results_df = pd.DataFrame(results)
        csv_path = os.path.join(csv_output_dir, "multi_signal_analysis.csv")
        results_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n📊 多因子分析结果已保存至: {csv_path}")


if __name__ == "__main__":
    main()
