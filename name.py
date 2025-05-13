# 所有名字总结
import pandas as pd
import os


def find_all_aliases(clean_data_dir, name_col='账户昵称', output_path="选手_曾用名表.csv"):
    """
    遍历cleanData中所有csv，提取每个选手历史用过的名字 + 当前文件名

    参数：
    clean_data_dir：cleanData目录路径
    name_col：csv中包含曾用名的列名
    output_path：输出csv文件路径
    """
    alias_list = []

    for file in os.listdir(clean_data_dir):
        if file.endswith(".csv"):
            file_path = os.path.join(clean_data_dir, file)
            df = pd.read_csv(file_path, encoding='utf-8-sig')

            current_name = file.replace(".csv", "")
            historical_names = set()

            # 1. 当前文件名加入
            historical_names.add(current_name)

            # 2. csv中提取曾用名
            if name_col in df.columns:
                names_in_file = df[name_col].dropna().unique()
                historical_names.update(names_in_file)
            else:
                print(f"⚠️ {file} 中未找到列 {name_col}")

            # 3. 保存结果
            for old_name in historical_names:
                alias_list.append({
                    "当前文件名": current_name,
                    "曾用名": old_name
                })

    result_df = pd.DataFrame(alias_list)
    result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 曾用名表已生成：{output_path}")

    return result_df


find_all_aliases(
    clean_data_dir="cleanData",
    name_col="账户昵称",
    output_path="选手_曾用名表.csv"
)
