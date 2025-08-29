# -*- coding:utf-8 -*-
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file

from Ashare import get_price
from MyTT import KDJ, MACD, RSI

app = Flask(__name__)


@app.route("/")
def index():
    """主页，显示股票数据查询表单"""
    return render_template("index.html")


@app.route("/get_stock_data", methods=["POST"])
def get_stock_data():
    """获取股票数据并计算技术指标"""
    try:
        # 获取表单数据
        code = request.form.get("code", "sh601818")
        count = int(request.form.get("count", 120)) + 1  # 包含今天
        frequency = request.form.get("frequency", "1d")

        # 获取股票数据
        df = get_price(code, end_date="", count=count, frequency=frequency)

        if df.empty:
            return jsonify({"error": "无法获取股票数据，请检查股票代码"}), 400

        # 准备数据用于技术指标计算
        CLOSE = df["close"].values
        HIGH = df["high"].values
        LOW = df["low"].values

        # 计算技术指标
        K, D, J = KDJ(CLOSE, HIGH, LOW, 9, 3, 3)
        DIF, DEA, MACD_BAR = MACD(CLOSE, 12, 26, 9)
        RSI_VALUE = RSI(CLOSE, 14)

        # 将技术指标添加到DataFrame
        df["K"] = K
        df["D"] = D
        df["J"] = J
        df["DIF"] = DIF
        df["DEA"] = DEA
        df["MACD"] = MACD_BAR
        df["RSI"] = RSI_VALUE

        # 保存数据到CSV文件
        filename = f"{code}_qfq_data_with_indicators.csv"
        df.to_csv(filename)

        # 转换DataFrame为HTML表格
        table_html = df.tail(10).to_html(
            classes="table table-striped table-hover", table_id="stock-data-table"
        )

        # 获取基本信息
        latest_data = df.iloc[-1]
        basic_info = {
            "code": code,
            "date": str(df.index[-1]),
            "close": round(latest_data["close"], 2),
            "high": round(latest_data["high"], 2),
            "low": round(latest_data["low"], 2),
            "volume": int(latest_data["volume"]),
            "K": round(latest_data["K"], 2) if not pd.isna(latest_data["K"]) else None,
            "D": round(latest_data["D"], 2) if not pd.isna(latest_data["D"]) else None,
            "J": round(latest_data["J"], 2) if not pd.isna(latest_data["J"]) else None,
            "DIF": round(latest_data["DIF"], 2)
            if not pd.isna(latest_data["DIF"])
            else None,
            "DEA": round(latest_data["DEA"], 2)
            if not pd.isna(latest_data["DEA"])
            else None,
            "MACD": round(latest_data["MACD"], 2)
            if not pd.isna(latest_data["MACD"])
            else None,
            "RSI": round(latest_data["RSI"], 2)
            if not pd.isna(latest_data["RSI"])
            else None,
        }

        return jsonify(
            {
                "success": True,
                "table_html": table_html,
                "basic_info": basic_info,
                "filename": filename,
                "total_rows": len(df),
            }
        )

    except Exception as e:
        return jsonify({"error": f"发生错误: {str(e)}"}), 500


@app.route("/download/<filename>")
def download_file(filename):
    """下载CSV文件"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"文件下载失败: {str(e)}", 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
