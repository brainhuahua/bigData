from selenium import webdriver
import time

# Chrome浏览器
driver = webdriver.Chrome()


driver.get("https://baidu.com/")
time.sleep(5)
time.sleep(5)  # 等待页面加载