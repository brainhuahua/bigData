import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def clean_filename(name1):
    # 替换 Windows 文件名非法字符为下划线
    return re.sub(r'[\\/*?:"<>|]', '_', name1)
# 初始化 Selenium
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 可选：后台运行
driver = webdriver.Chrome(options=options)
driver.get("https://spdspc.qhrb.com.cn/#/")
time.sleep(5)

# 点击“长期稳定盈利奖”
award_tab = driver.find_element(By.XPATH, "//div[contains(text(),'长期稳定盈利奖')]")
award_tab.click()


# 创建主数据目录
os.makedirs("data", exist_ok=True)

page = 1

'''
num 
'''

n = int(input("跳过几页？"))

# 如果存在并且含有内容则读取，否则创建

data_file_path = "data/选手总榜单.csv"

if os.path.exists(data_file_path):
    df = pd.read_csv(data_file_path, encoding='utf-8-sig')
    print("已读取原有文件")
else:
    # ❌ 文件不存在或为空，创建新 DataFrame
    columns = ['序号','排名', '昵称'] + [f"第{i}届" for i in range(6, 19)]
    df = pd.DataFrame(columns=columns)
    print("📄 文件不存在或为空，已创建新文件")


number = 1

first_row_nickname = '汪先生'


for i in range(1, n+1):
    next_btn = driver.find_element(By.XPATH, "//a[contains(text(),'下一页')]")
    if "disabled" in next_btn.get_attribute("class"):
        print("已到最后一页，结束。")

    else:
        # 等待选手表格出现
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//table/tbody/tr"))
        )
        print(f"跳过第{page}页")
        next_btn.click()
        page += 1
        number+=50
        # 等待直到表格第一行昵称发生变化
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, "//table/tbody/tr[1]/td[2]").text.strip() != first_row_nickname
        )

        first_row_nickname = driver.find_element(By.XPATH, "//table/tbody/tr[1]/td[2]").text.strip()

while True:

    print(f"正在处理第 {page} 页")

    # 等待选手表格出现
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//table/tbody/tr"))
    )

    first_row_nickname = driver.find_element(By.XPATH, "//table/tbody/tr[1]/td[2]").text.strip()

    # 获取当前页所有选手行
    rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
    print(f"当前页选手行数：{len(rows)}")  # <-- 添加这个
    for row in rows:
        try:

            start_time = time.time()

            cols = row.find_elements(By.TAG_NAME, "td")

            if len(cols) < 19:
                continue

            rank = cols[0].text.strip().replace('/', '_')  # 去掉特殊符号
            name = cols[1].text.strip()



            # 初始化一行数据
            row_data = {'序号': number,'排名': rank, '昵称': name}

            # 创建文件夹
            folder_name = f"{number}_{name}"
            folder_name = clean_filename(folder_name)
            folder_path = os.path.join("data", folder_name)
            os.makedirs(folder_path, exist_ok=True)

            main_window = driver.current_window_handle
            #6-13
            for i in range(5,13):
                score = cols[i].text.strip()
                row_data[f'第{i+1}届'] = score

                # 尝试点击得分，跳转详情页
                try:
                    p = cols[i].find_element(By.TAG_NAME, "p")
                    style = p.get_attribute("style")
                    if style and "cursor: pointer" in style:


                        existing_windows = driver.window_handles

                        p.click()

                        # 等待新窗口出现
                        WebDriverWait(driver, 10).until(
                            lambda d: len(d.window_handles) > len(existing_windows)
                        )

                        # 切换到新窗口
                        new_window = [w for w in driver.window_handles if w != main_window][0]
                        driver.switch_to.window(new_window)
                        # 等待 iframe 加载
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "frmMain"))
                        )
                        # 切换到 iframe
                        driver.switch_to.frame("frmMain")

                        # 现在就可以抓表格了！
                        rows_detail = driver.find_elements(By.XPATH, "//table[@class='admintable']//tr")

                        detail_data = {}
                        for row_d in rows_detail:
                            tds = row_d.find_elements(By.TAG_NAME, "td")
                            for k in range(int(len(tds)/2)):
                                detail_data[tds[k*2].text.strip()] = tds[k*2+1].text.strip()


                        # 保存详情页为 CSV
                        pd.DataFrame([detail_data]).to_csv(
                            os.path.join(folder_path, f"{i+1}.csv"),
                            index=False, encoding='utf-8-sig'
                        )

                        # 切出 iframe
                        driver.switch_to.default_content()

                        # 关闭窗口，切回主窗口
                        driver.close()
                        driver.switch_to.window(main_window)

                except :
                    # 关闭窗口，切回主窗口
                    driver.close()
                    driver.switch_to.window(main_window)
                    print(f"❗ 第{i+1}届得分非可点击链接，跳过详情。")
                    continue

            #14-16
            for i in range(13,16):
                score = cols[i].text.strip()
                row_data[f'第{i+1}届'] = score

                # 尝试点击得分，跳转详情页
                try:
                    p = cols[i].find_element(By.TAG_NAME, "p")
                    style = p.get_attribute("style")
                    if style and "cursor: pointer" in style:


                        existing_windows = driver.window_handles

                        p.click()

                        # 等待新窗口出现
                        WebDriverWait(driver, 10).until(
                            lambda d: len(d.window_handles) > len(existing_windows)
                        )

                        # 切换到新窗口
                        new_window = [w for w in driver.window_handles if w != main_window][0]
                        driver.switch_to.window(new_window)

                        # 等待这个表格出现（根据 class）
                        table = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//table[@class='fl-table table-hover']"))
                        )

                        # 现在就可以抓表格了！
                        rows_detail = driver.find_elements(By.XPATH, "(//table[@class='fl-table table-hover']/tbody)[2]//tr")

                        detail_data = {}
                        for row_d in rows_detail:
                            tds = row_d.find_elements(By.TAG_NAME, "td")
                            for k in range(int(len(tds) / 2)):
                                detail_data[tds[k * 2].text.strip()] = tds[k * 2 + 1].text.strip()

                        # 保存详情页为 CSV
                        pd.DataFrame([detail_data]).to_csv(
                            os.path.join(folder_path, f"{i+1}.csv"),
                            index=False, encoding='utf-8-sig'
                        )

                        # 关闭窗口，切回主窗口
                        driver.close()
                        driver.switch_to.window(main_window)

                except :
                    # 关闭窗口，切回主窗口
                    driver.close()
                    driver.switch_to.window(main_window)
                    print(f"❗ 第{i+1}届得分非可点击链接，跳过详情。")
                    continue
            #17-18
            for i in range(16,18):
                score = cols[i].text.strip()
                row_data[f'第{i+1}届'] = score

                # 尝试点击得分，跳转详情页
                try:
                    p = cols[i].find_element(By.TAG_NAME, "p")
                    style = p.get_attribute("style")
                    if style and "cursor: pointer" in style:


                        existing_windows = driver.window_handles

                        p.click()

                        # 等待新窗口出现
                        WebDriverWait(driver, 10).until(
                            lambda d: len(d.window_handles) > len(existing_windows)
                        )

                        # 切换到新窗口
                        new_window = [w for w in driver.window_handles if w != main_window][0]
                        driver.switch_to.window(new_window)

                        # 等待这个表格出现（根据 class）
                        table = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//table[@class='el-descriptions__table is-bordered']"))
                        )

                        # 现在就可以抓表格了！
                        tbody_detail = driver.find_elements(By.XPATH,"(//table[@class='el-descriptions__table is-bordered'])[1]//tbody")
                        detail_data = {}
                        for tbody in tbody_detail:
                            tbs = tbody.find_elements(By.TAG_NAME, "tr")

                            ths = tbs[0].find_elements(By.TAG_NAME, "th")
                            tds = tbs[0].find_elements(By.TAG_NAME, "td")

                            for k in range(len(ths)):
                                detail_data[ths[k].text.strip()] = tds[k].text.strip()
                        # 保存详情页为 CSV
                        pd.DataFrame([detail_data]).to_csv(
                            os.path.join(folder_path, f"{i+1}.csv"),
                            index=False, encoding='utf-8-sig'
                        )


                        # 关闭窗口，切回主窗口
                        driver.close()
                        driver.switch_to.window(main_window)

                except :
                    print(f"❗ 第{i+1}届得分非可点击链接，跳过")
                    # 关闭窗口，切回主窗口
                    driver.close()
                    driver.switch_to.window(main_window)
                    continue

            exists = not df[(df['序号'] == number) & (df['昵称'] == name)].empty
            # 添加到 DataFrame
            if exists:
                df.loc[(df['序号'] == number) & (df['昵称'] == name), :] = row_data

            else:
                df.loc[len(df)] = row_data


            end_time = time.time()
            print(f"第{number}位选手{name},耗时：{end_time - start_time:.2f} 秒") # <-- 添加这个
            print(f"第{number}位选手{name},{row_data}")
            number += 1

        except Exception as e:
            print(f"跳过选手：{number}，错误：{e}")
            number +=1
            driver.switch_to.window(main_window)
            continue

    df.to_csv("data/选手总榜单.csv", index=False, encoding='utf-8-sig')


    next_btn = driver.find_element(By.XPATH, "//a[contains(text(),'下一页')]")
    if "disabled" in next_btn.get_attribute("class"):
        print("已到最后一页，结束。")
        break
    else:
        next_btn.click()
        page += 1
        # 等待直到表格第一行昵称发生变化
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, "//table/tbody/tr[1]/td[2]").text.strip() != first_row_nickname
        )



# 保存总榜单信息
df.to_csv("data/选手总榜单.csv", index=False, encoding='utf-8-sig')
print("全部完成，总共选手数：", len(df))

driver.quit()
