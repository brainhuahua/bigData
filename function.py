import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import platform
import re
from sklearn.cluster import KMeans

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
    num = 1
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



def remove_outliers_iqr(series):
    """
    使用IQR方法剔除pandas Series中的异常值。
    返回剔除后的Series。
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return series[(series >= lower_bound) & (series <= upper_bound)]

def plot_boxplot(df, indicator_name, save_path=None, title_fontsize=14):
    """
    中文支持 + 自动剔除异常值：绘制单指标的箱型图

    参数：
    df：DataFrame，包含需要绘制的数据
    indicator_name：字符串，DataFrame中需要绘制的列名
    save_path：可选，若不为None则保存图片到此路径
    title_fontsize：标题字体大小
    """

    # ✅ 全平台中文显示
    system = platform.system()
    if system == "Windows":
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    elif system == "Darwin":  # macOS
        plt.rcParams['font.sans-serif'] = ['Heiti TC']
    else:  # Linux 或其他
        plt.rcParams['font.sans-serif'] = ['SimHei']

    plt.rcParams['axes.unicode_minus'] = False

    # 自动剔除异常值
    series = df[indicator_name].dropna()
    series_filtered = remove_outliers_iqr(series)

    # 创建图形
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=series_filtered, color="skyblue")
    plt.title(f"{indicator_name} 分布箱型图 (剔除异常值)", fontsize=title_fontsize)
    plt.xlabel(indicator_name, fontsize=12)

    # 保存 or 显示
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"✅ 已保存箱型图：{save_path}")
    else:
        plt.show()

    plt.close()


def kmeans_1d_clustering(df, indicator_name, n_clusters=3, save_path=None):
    """
    单指标一维KMeans聚类，并保存每类数量和均值

    参数：
    df：DataFrame，包含需要绘制的数据
    indicator_name：指标列名
    n_clusters：聚类个数，默认3
    save_path：可选，若不为None则保存结果csv
    """
    # 中文显示
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    data = df[[indicator_name]].dropna()

    # 聚类
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    data['Cluster'] = model.fit_predict(data[[indicator_name]])

    # 合并回原df
    df = df.merge(data[['Cluster']], left_index=True, right_index=True, how='left')

    # 每类样本数量和均值
    cluster_summary = df.groupby('Cluster')[indicator_name].agg(['count', 'mean']).reset_index()
    print(cluster_summary)

    # 可视化
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Cluster', y=indicator_name, hue='Cluster', data=df, palette="Set2", legend=False)
    plt.title(f"{indicator_name} - {n_clusters}类KMeans聚类结果")

    # 保存结果
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path+'_Kmeans.csv', index=False, encoding='utf-8-sig')
        cluster_summary.to_csv(save_path+'_Kmeans_ClusterSummary.csv', index=False, encoding='utf-8-sig')
        plt.savefig(save_path+'_Kmeans.png', bbox_inches='tight', dpi=300)
        print(f"✅ 聚类结果和统计已保存：{save_path}")

    plt.close()

    return df, cluster_summary