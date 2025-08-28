def get_price_day_tx_fixed(code, end_date="", count=10, frequency="1d"):
    """修复版的腾讯日线获取函数"""
    unit = "week" if frequency in "1w" else "month" if frequency in "1M" else "day"
    if end_date:
        end_date = (
            end_date.strftime("%Y-%m-%d")
            if isinstance(end_date, pd.Timestamp)
            else end_date.split(" ")[0]
        )
    end_date = "" if end_date == pd.Timestamp.now().strftime("%Y-%m-%d") else end_date

    URL = f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date},{count},qfq"
    st = json.loads(requests.get(URL).content)
    ms = "qfq" + unit
    stk = st["data"][code]
    buf = stk[ms] if ms in stk else stk[unit]

    # 修复：手动创建DataFrame，避免列数不匹配问题
    # 腾讯接口返回的数据顺序是：日期,开盘,收盘,最高,最低,成交量
    data = {
        "time": [item[0] for item in buf],
        "open": [item[1] for item in buf],
        "close": [item[2] for item in buf],
        "high": [item[3] for item in buf],
        "low": [item[4] for item in buf],
        "volume": [item[5] for item in buf],
    }

    df = pd.DataFrame(data)

    # 转换数据类型
    df["time"] = pd.to_datetime(df["time"])
    numeric_cols = ["open", "close", "high", "low", "volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    df.set_index(["time"], inplace=True)
    df.index.name = ""
    return df
