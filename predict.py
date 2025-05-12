import pandas as pd
import os
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import platform

# 中文字体适配
system = platform.system()
if system == "Windows":
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
elif system == "Darwin":
    plt.rcParams['font.sans-serif'] = ['Heiti TC']
else:
    plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False



analyzes = ["期初权益","期末权益","累计入金","累计出金",
            "累计净值","最大回撤率","累计净利润","日收益率均值",
            "日收益率最大","日收益率最小","总交易天数","盈利天数",
            "亏损天数","交易胜率","盈亏比","手续费/净利润","风险度均值"]



def load_cleanData_merge(clean_data_dir, target_col="第18届排名"):
    """
    批量读取 cleanData/*.csv 并合并为大DataFrame
    百分数字段自动转换为小数
    """
    data_list = []
    for file in os.listdir(clean_data_dir):
        if file.endswith(".csv"):
            file_path = os.path.join(clean_data_dir, file)
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df['选手'] = file.replace(".csv", "")

            # ✅ 百分号转小数
            for col in analyzes:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # 如果原来有%（手动检测），才除以100
                    percent_mask = df[col].astype(str).str.contains('\d+\.\d+%|\d+%', regex=True)
                    df.loc[percent_mask, col] = df.loc[percent_mask, col] / 100

            data_list.append(df)

    full_df = pd.concat(data_list, ignore_index=True)
    columns = analyzes + ['选手']
    if target_col in full_df.columns:
        columns.append(target_col)
    full_df = full_df[columns]
    print(f"✅ 已读取 cleanData，共{len(full_df)}条记录（百分号已转换）")
    return full_df


def train_global_model(clean_data_dir, target_col="综合排名"):
    """
    批量读取 cleanData 并训练 XGBoost 模型
    """
    df = load_cleanData_merge(clean_data_dir, target_col)
    df = df.dropna()

    X = df[analyzes].values
    y = df[target_col].values

    model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X, y)

    print(f"✅ XGBoost模型训练完成，样本数：{X.shape[0]}, 特征数：{X.shape[1]}")
    return model, analyzes

def predict_single_player(model, player_row, features):
    """
    单选手预测
    """
    X_player = player_row[features].values
    pred_score = model.predict(X_player)[0]
    return pred_score

def predict_and_rank_all(model, clean_data_dir, target_col="第18届排名", save_path=None):
    """
    全体选手预测 + 排名
    """
    df = load_cleanData_merge(clean_data_dir, target_col)
    df = df.dropna()
    X_all = df[analyzes].values
    pred_scores = model.predict(X_all)

    df['预测得分'] = pred_scores
    df['预测排名'] = df['预测得分'].rank(ascending=True, method='first').astype(int)

    if save_path:
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"✅ 预测结果已保存：{save_path}")


    return df

# 示例用法
if __name__ == "__main__":



    clean_data_dir = "cleanData"

    # 训练
    model, features = train_global_model(clean_data_dir)

    # 单人预测
    df = load_cleanData_merge(clean_data_dir)
    single_player = df.iloc[[0]]  # 取第一个选手
    score = predict_single_player(model, single_player, features)
    print(f"🎯 单人预测得分：{score:.4f}")

    # 全体预测 + 排名
    result_df = predict_and_rank_all(
        model,
        clean_data_dir,
        save_path="第18届排名预测_XGBoost.csv"
    )

    full_df = pd.read_csv(f"第18届排名预测_XGBoost.csv", encoding='utf-8-sig')
    full_df = full_df.groupby('选手', as_index=False).mean()
    columns_to_keep = ['选手', '预测得分', '预测排名']
    new_df = full_df[columns_to_keep]
    new_df.to_csv(f"predict.csv", index=False, encoding='utf-8-sig')