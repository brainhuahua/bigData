import os
import pandas as pd
from function import *

cleandata_dir = "cleanData"
AnalyzeData_dir = "AnalyzeData"


analyzes = ["期初权益","期末权益","累计入金","累计出金","综合排名","累计净值","最大回撤率","累计净利润",
           "日收益率均值","日收益率最大","日收益率最小","总交易天数","盈利天数","亏损天数","交易胜率","盈亏比","手续费/净利润","风险度均值"]


for analyze in analyzes:

    analyze_single_indicator_data(AnalyzeData_dir, cleandata_dir,analyze)

