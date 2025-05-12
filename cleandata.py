import os
import pandas as pd

data_dir = "data"

cleandata_dir = "cleanData"

os.makedirs(cleandata_dir, exist_ok=True)
for folder in os.listdir(data_dir):
    folder_path = os.path.join(data_dir, folder)

    folder_name = folder.split(".")[0]

    if os.path.isdir(folder_path):
        summary = []
        # 遍历6.csv ~ 18.csv
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                if not df.empty:
                    data = df.iloc[0].to_dict()  # 提取详情数据
                    data['届数'] = int(file.replace(".csv", ""))  # 添加届数
                    summary.append(data)
            except Exception as e:
                print(f"⚠️ 读取 {file_path} 出错：{e}")

        # 汇总后保存
        if summary and len(summary) > 2:  ##参赛次数少于三次不作考虑
            df_summary = pd.DataFrame(summary)
            df_summary = df_summary.sort_values(by='届数')  # 排序
            df_summary.to_csv(os.path.join(cleandata_dir, f"{folder_name}.csv"),
                              index=False, encoding='utf-8-sig')
            print(f"✅ 已生成 {folder}_summary.csv")
