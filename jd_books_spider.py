# --*-- coding: utf-8 --*--
# @Author  : sheldon
# @Software: PyCharm
import time

import pymysql
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import random
import json





import csv
from lxml import etree

options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
# 不加载图片
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 50)  # 设置等待时间
url = 'https://www.jd.com/'
data_list = []  # 设置全局变量用来存储数据
keyword = "python爬虫"  # 关键词


def search():
    browser.get('https://www.jd.com/')
    try:
        input = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#key"))
        )  # 等到搜索框加载出来
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#search > div > div.form > button"))
        )  # 等到搜索按钮可以被点击
        input[0].send_keys(keyword)  # 向搜索框内输入关键词
        submit.click()  # 点击
        total = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > em:nth-child(1) > b')
            )
        )  # 记录一下总页码,等到总页码加载出来
        # # 滑动到底部，加载出后三十个货物信息
        # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # wait.until(
        #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#J_goodsList > ul > li:nth-child(60)"))
        # )
        html = browser.page_source  # 获取网页信息
        prase_html(html)  # 调用提取数据的函数
        return total[0].text  # 返回总页数
    except TimeoutError:
        search()


def next_page(page_number):
    try:
        # 滑动到底部
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randint(1, 3))  # 设置随机延迟
        button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.pn-next > em'))
        )  # 翻页按钮
        button.click()  # 翻页动作
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#J_goodsList > ul > li:nth-child(30)"))
        )  # 等到30个商品都加载出来
        # 滑动到底部，加载出后三十个货物信息
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#J_goodsList > ul > li:nth-child(60)"))
        )  # 等到60个商品都加载出来
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"), str(page_number))
        )  # 判断翻页成功,高亮的按钮数字与设置的页码一样
        html = browser.page_source  # 获取网页信息
        prase_html(html)  # 调用提取数据的函数
    except TimeoutError:
        return next_page(page_number)


def prase_html(html):
    html = etree.HTML(html)
    # 开始提取信息,找到ul标签下的全部li标签
    try:
        lis = browser.find_elements_by_class_name('gl-item')
        # 遍历
        for li in lis:
            # 名字
            title = li.find_element_by_xpath('.//div[@class="p-name p-name-type-2"]//em').text
            # 价格
            price = li.find_element_by_xpath('.//div[@class="p-price"]//i').text
            # 评论数
            comment = li.find_elements_by_xpath('.//div[@class="p-commit"]//a')
            # 商铺名字
            shop_name = li.find_elements_by_xpath('.//div[@class="p-shop"]//a')
            if comment:
                comment = comment[0].text
            else:
                comment = None
            if shop_name:
                shop_name = shop_name[0].text
            else:
                shop_name = None
            data_dict = {}  # 写入字典
            data_dict["title"] = title
            data_dict["price"] = price
            data_dict["shop_name"] = shop_name
            data_dict["comment"] = comment
            print(data_dict)
            data_list.append(data_dict)  # 写入全局变量
    except TimeoutError:
        prase_html(html)


def save_html():
    content = json.dumps(data_list, ensure_ascii=False, indent=2)
    # 把全局变量转化为json数据
    with open("jingdongbooks.json", "a+", encoding="utf-8") as f:
        f.write(content)
        print("json文件写入成功")

    with open('jingdongbooks.csv', 'w', encoding='utf-8-sig', newline='') as f:
        # 表头
        title = data_list[0].keys()
        # 声明writer
        writer = csv.DictWriter(f, title)
        # 写入表头
        writer.writeheader()
        # 批量写入数据
        writer.writerows(data_list)
    print('csv文件写入完成')


def main():
    print("第", 1, "页：")
    total = int(search())
    for i in range(2, 5):
        # for i in range(2, total + 1):
        time.sleep(random.randint(1, 3))  # 设置随机延迟
        print("第", i, "页：")
        next_page(i)
    save_html()


if __name__ == "__main__":
    main()