from data_updater import update_stock_data
from macd_checker import MACDChecker

stock_list = ["sh601328", "sh601818", "sh601288"]

results = []
for code in stock_list:
    print(f"\n{'='*60}")
    df = update_stock_data(code)  # 使用 config.yaml 中的默认配置
    if df is not None:
        checker = MACDChecker(code)
        result = checker.run()  # 使用 config.yaml 中的默认配置
        results.append(result)
        checker.plot()
