from data_updater import update_stock_data, load_config # 导入 load_config
from macd_checker import MACDChecker
import os

def get_stock_list(config):
    """从配置获取股票列表"""
    stock_pool_config = config.get("stock_pool", {})
    
    # 优先从文件读取
    file_path = stock_pool_config.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                # 假设每行一个股票代码，忽略空行和注释
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(f"⚠️ 从文件 {file_path} 读取股票列表失败: {e}")
            
    # 否则使用静态列表
    static_list = stock_pool_config.get("static_list", [])
    if static_list:
        return static_list
    else:
        print("⚠️ 配置文件中未找到有效的股票列表。")
        return []

def main():
    config = load_config()
    stock_list = get_stock_list(config)
    
    if not stock_list:
        print("❌ 没有找到要分析的股票。请检查 config.yaml 中的 stock_pool 配置。")
        return

    results = []
    for code in stock_list:
        print(f"\n{'='*60}")
        # 传递整个 config 给 update_stock_data
        df = update_stock_data(code, config)  
        if df is not None:
            # 传递 config 给 MACDChecker
            checker = MACDChecker(code, config=config) 
            result = checker.run()  # 使用 config.yaml 中的默认配置
            results.append(result)
            # plot 会根据 config 决定是否显示或保存
            checker.plot() 

    # (可选) 将结果保存到 CSV
    output_config = config.get("output", {})
    csv_output_dir = output_config.get("csv_output_dir", None)
    if csv_output_dir and results:
        os.makedirs(csv_output_dir, exist_ok=True)
        import pandas as pd
        results_df = pd.DataFrame(results)
        csv_path = os.path.join(csv_output_dir, "macd_analysis_results.csv")
        results_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n📊 分析结果已保存至: {csv_path}")

if __name__ == "__main__":
    main()
