import pandas as pd
import os
import re

def clean_filename(name1):
    # 替换 Windows 文件名非法字符为下划线
    return re.sub(r'[\\/*?:"<>|]', '_', name1)

def analyze_single_indicator_data(AnalyzeData, clean_data_dir, indicator_name):
    """
    从cleanData目录中提取所有选手的指定指标，计算每个选手该指标的平均值，
    并将结果保存到AnalyzeData目录下。

    参数：
    AnalyzeData：分析结果保存目录
    clean_data_dir：cleanData数据目录
    indicator_name：需要分析的指标名称
    """
    print(f"---------------------------------现在处理{indicator_name}--------------------------------------------")
    result = []
    num = 0
    # 确保分析结果目录存在
    os.makedirs(AnalyzeData, exist_ok=True)

    # 遍历cleanData下所有csv文件
    for file in os.listdir(clean_data_dir):
        if file.endswith(".csv"):
            file_path = os.path.join(clean_data_dir, file)
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                if indicator_name in df.columns:
                    name = file.replace(".csv", "")
                    col_values = df[indicator_name].astype(str)
                    if col_values.str.contains('%').any():
                        # 百分号字段：去掉%并转为比例
                        values = pd.to_numeric(col_values.str.replace('%', '', regex=False),
                                               errors='coerce').dropna() / 100
                    else:
                        # 正常数字字段
                        values = pd.to_numeric(col_values, errors='coerce').dropna()

                    #values = pd.to_numeric(df[indicator_name], errors='coerce').dropna()
                    if not values.empty:
                        avg_value = values.mean()  # 取平均
                        result.append({"选手": name, indicator_name: avg_value})
                else:
                    print(f"⚠️ 文件 {file} 中未找到 {indicator_name} 列")
            except Exception as e:
                print(f"⚠️ 文件 {file} 处理失败：{e}")
        print(f"处理完{num}")
        num += 1
    # 整理为DataFrame
    result_df = pd.DataFrame(result)
    # 保存到AnalyzeData目录
    result_df.to_csv(os.path.join(AnalyzeData, f"{clean_filename(indicator_name)}.csv"),
                     index=False, encoding='utf-8-sig')
    print(f"✅ {indicator_name} 指标分析完成，已保存到 {AnalyzeData}")
    return result_df