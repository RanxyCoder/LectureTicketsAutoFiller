from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
import time
import datetime


class InternalElementError(Exception):
    pass


def web_script(url, browser, pt, input_list):
    # 浏览器选择
    if browser == 0:
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)
    elif browser == 1:
        options = EdgeOptions()
        driver = webdriver.Edge(options=options)
    else:
        print('❌ 你输错了，0是谷歌，1是微软')
        return

    driver.get(url)

    # 登录部分
    login_button = driver.find_element(By.ID, "header-login-btn")
    login_button.click()
    driver.implicitly_wait(2)

    qq_button = driver.find_element(By.CSS_SELECTOR, "span.qq")
    qq_button.click()

    while True:
        wait_over = input("✅ 登录完了你打个 ok，别动窗口，我来抢：")
        if wait_over.strip().lower() == 'ok':
            break

    # 如果指定时间，就等到指定时刻再刷新
    if pt is not None:
        exe_time = datetime.datetime(*pt)
        wait_time = exe_time - datetime.datetime.now()
        if wait_time.total_seconds() <= 0:
            print('⏰ 你逗我玩呢？哥们儿有时光机吗？')
            return
        print(f"等待开始... 目标时间：{exe_time.strftime('%Y-%m-%d %H:%M:%S')}，还有 {wait_time.total_seconds():.1f} 秒")
        time.sleep(wait_time.total_seconds())

    print("🚀 开始抢填！")
    driver.execute_script("window.location.reload()")

    # 等待输入框加载
    timeout = 10
    locator = (By.XPATH, "//textarea[@placeholder='请输入']")
    try:
        elements = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located(locator))
    except Exception as e:
        raise InternalElementError(f"❌ 未找到输入框: {e}")

    # 输入数据
    min_len = min(len(input_list), len(elements))
    if len(input_list) != len(elements):
        print(f"⚠️ 提示：输入数量({len(input_list)})与表单字段({len(elements)})不一致，只填前 {min_len} 项。")

    for i in range(min_len):
        elements[i].send_keys(input_list[i])

    # 提交
    submit_button = driver.find_element(By.XPATH, "//button[text()='提交']")
    driver.execute_script("arguments[0].click();", submit_button)

    # 确认
    confirm_locator = (By.XPATH, "//button[contains(.,'确认')]")
    confirm_button = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(confirm_locator))
    confirm_button.click()

    print("✅ 抢填完成！时间：", datetime.datetime.now())


if __name__ == '__main__':
    web_script(
        "https://docs.qq.com/form/page/...",
        1,  # 1=Edge，0=Chrome
        (2025, 11, 1, 12, 0, 0),  # 年月日时分秒，None 表示立即执行
        ('姓名', 'XXXX学院', '138XXXXXXXX')  # 表单内容（按顺序往下填）
    )
