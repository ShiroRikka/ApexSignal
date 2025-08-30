from data_updater import update_stock_data
from macd_checker import MACDChecker

stock_list = ["sh601328", "sh601818", "sh601288"]

results = []
for code in stock_list:
    print(f"\n{'='*60}")
    df = update_stock_data(code)
    if df is not None:
        checker = MACDChecker(code)
        result = checker.run()
        results.append(result)
        checker.plot()
