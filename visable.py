
import pandas as pd
from function import *




analyzes = ["期初权益","期末权益","累计入金","累计出金","综合排名","累计净值","最大回撤率","累计净利润",
           "日收益率均值","日收益率最大","日收益率最小","总交易天数","盈利天数","亏损天数","交易胜率","盈亏比","手续费/净利润","风险度均值"]

for analyze in analyzes:
    # 假设你已有一个DataFrame
    df = pd.read_csv(f"AnalyzeData/{clean_filename(analyze)}.csv", encoding='utf-8-sig')

    # 调用画图函数
    # plot_boxplot(df, f"{analyze}",f"AnalyzePicture/single/{clean_filename(analyze)}.png")
    kmeans_1d_clustering(df,f"{analyze}",n_clusters=3,save_path=f"AnalyzePicture/oneKmeans/{clean_filename(analyze)}")