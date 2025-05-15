import pandas as pd

# 替换为你的文件路径
used_names_df = pd.read_csv("predict.csv", encoding="utf-8")     # 列：选手，预测得分，预测排名
prediction_names_df = pd.read_csv("选手_曾用名表.csv", encoding="utf-8")    # 列：当前文件名，曾用名

# 去重
used_names_unique = used_names_df.drop_duplicates(subset=["选手"], keep="first")

# 映射表
mapping = used_names_unique.set_index("选手")[["预测得分", "预测排名"]].to_dict(orient="index")

# 映射函数
def get_score(name):
    return mapping.get(name, {"预测得分": None, "预测排名": None})["预测得分"]

def get_rank(name):
    return mapping.get(name, {"预测得分": None, "预测排名": None})["预测排名"]

# 添加到曾用名表
prediction_names_df["预测得分"] = prediction_names_df["当前文件名"].apply(get_score)
prediction_names_df["预测排名"] = prediction_names_df["当前文件名"].apply(get_rank)

# 保存
prediction_names_df.to_csv("曾用名表_添加预测结果_UTF8.csv", index=False, encoding="utf-8")
print("已保存为 曾用名表_添加预测结果_UTF8.csv")
