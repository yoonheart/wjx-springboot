import logging
import random
import re
import threading
import traceback
from threading import Thread
import time
import json
import sys
import os

import numpy
import requests
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

current_ip = None  # 当前使用的IP
ip_use_count = 0   # 当前IP已使用次数
IP_MAX_USE = 10    # 单个IP最大使用次数（你实测的10-12份）
ip_lock = threading.Lock()  # IP操作锁

def zanip():
    """优化版：加重试+错误处理，确保拿到有效IP"""
    api = "api填写处"
    max_retry = 3  # 最多重试3次
    retry_count = 0

    while retry_count < max_retry:
        try:
            response = requests.get(api, timeout=10)
            response.raise_for_status()  # 触发HTTP错误
            ip = response.text.strip()
            if validate(ip):
                return ip
            else:
                print(f"IP格式不合法: {ip}")
        except Exception as e:
            print(f"获取IP失败（第{retry_count+1}次重试）: {e}")
        retry_count += 1
        time.sleep(1)  # 重试间隔1秒

    print("多次获取IP失败，使用本机IP")
    return None


# ========== 全局配置（从JSON动态加载） ==========
config = {}

# 新增：全局变量提前初始化（解决多线程读取不到的问题）
cur_num = 0
cur_fail = 0
lock = threading.Lock()


# ========== 工具函数 ==========
# 校验IP地址合法性
def validate(ip):
    pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):(\d{1,5})$"
    return bool(re.match(pattern, ip))


# 检测题目是否可见（核心：适配条件逻辑题）
def is_question_visible(driver: WebDriver, question_id: int) -> bool:
    try:
        element = driver.find_element(By.ID, f"div{question_id}")
        return element.is_displayed() and element.size['width'] > 0 and element.size['height'] > 0
    except NoSuchElementException:
        return False


# 概率归一化（避免除以0）
def normalize_prob(prob_list):
    prob_sum = sum(prob_list)
    if prob_sum == 0 or len(prob_list) == 0:
        return [1 / len(prob_list)] * len(prob_list) if len(prob_list) > 0 else [1]
    return [x / prob_sum for x in prob_list]


# ========== 题型处理函数（修复版） ==========
# 填空题处理函数
def vacant(driver: WebDriver, current):
    try:
        # 从配置中按实际题号取参数
        current_str = str(current)
        content = config.get("texts", {}).get(current_str, ["默认内容"])
        p = config.get("texts_prob", {}).get(current_str, [1] * len(content))

        # 概率归一化
        norm_p = normalize_prob(p)
        # 确保概率长度和内容长度一致
        if len(norm_p) != len(content):
            norm_p = [1 / len(content)] * len(content)

        text_index = numpy.random.choice(a=range(len(content)), p=norm_p)
        selected_text = content[text_index]

        input_elem = driver.find_element(By.CSS_SELECTOR, f"#q{current}")
        input_elem.clear()  # 清空原有内容
        input_elem.send_keys(selected_text)
    except Exception as e:
        print(f"处理填空题{current}失败: {e}")


# 单选题处理函数（新增其他选项文本输入功能）
def single(driver: WebDriver, current):
    try:
        xpath = f'//*[@id="div{current}"]/div[2]/div'
        options = driver.find_elements(By.XPATH, xpath)
        if not options:
            return

        # 从配置中按实际题号取参数
        p = config.get("single_prob", {}).get(str(current), -1)
        if p == -1:
            r = random.randint(1, len(options))
        else:
            norm_p = normalize_prob(p)
            assert len(norm_p) == len(options), f"第{current}题参数长度({len(p)})与选项数({len(options)})不匹配！"
            r = numpy.random.choice(a=range(1, len(options) + 1), p=norm_p)

        # 点击选中选项
        option_element = driver.find_element(By.CSS_SELECTOR,
                                           f"#div{current} > div.ui-controlgroup > div:nth-child({r})")
        option_element.click()

        # 新增：检查是否是"其他"选项并处理文本输入
        option_text = option_element.text
        if "其他" in option_text:
            # 查找对应的文本输入框
            try:
                # 问卷星"其他"选项的文本框通常有以下几种选择器
                other_input_selectors = [
                    f"#q{current}_other",  # 常见格式
                    f"#div{current} input[type='text']",  # 兜底
                    f"#div{current} textarea"  # 可能是多行文本
                ]

                other_input = None
                for selector in other_input_selectors:
                    try:
                        other_input = driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue

                if other_input:
                    # 获取当前题目的"其他"选项文本和概率
                    other_text_list = config.get("single_other_texts", {}).get(str(current), ["其他情况"])
                    other_text_prob = config.get("single_other_texts_prob", {}).get(str(current), None)

                    # 根据概率选择文本
                    if other_text_prob and len(other_text_prob) == len(other_text_list):
                        # 概率归一化
                        norm_prob = normalize_prob(other_text_prob)
                        # 使用numpy根据概率选择
                        text_index = numpy.random.choice(range(len(other_text_list)), p=norm_prob)
                        other_text = other_text_list[text_index]
                    else:
                        # 无概率配置时，均等随机选择
                        other_text = random.choice(other_text_list)

                    # 输入文本
                    other_input.clear()
                    other_input.send_keys(other_text)
            except Exception as e:
                print(f"  处理第{current}题'其他'选项文本失败: {e}")

    except Exception as e:
        print(f"处理单选题{current}失败: {e}")


# 下拉框处理函数
def droplist(driver: WebDriver, current):
    try:
        driver.find_element(By.CSS_SELECTOR, f"#select2-q{current}-container").click()
        time.sleep(0.5)

        options = driver.find_elements(By.XPATH, f"//*[@id='select2-q{current}-results']/li")
        if not options or len(options) <= 1:
            return

        # 从配置中按实际题号取参数
        p = config.get("droplist_prob", {}).get(str(current), [1] * (len(options) - 1))
        norm_p = normalize_prob(p[:len(options) - 1])  # 只取前len(options)-1个（排除"请选择"）

        r = numpy.random.choice(a=range(1, len(options)), p=norm_p)
        driver.find_element(By.XPATH, f"//*[@id='select2-q{current}-results']/li[{r + 1}]").click()
    except Exception as e:
        print(f"处理下拉框题{current}失败: {e}")


# 多选题处理函数
def multiple(driver: WebDriver, current):
    try:
        xpath = f'//*[@id="div{current}"]/div[2]/div'
        options = driver.find_elements(By.XPATH, xpath)
        if not options:
            return

        # 从配置中按实际题号取参数
        p = config.get("multiple_prob", {}).get(str(current), [50] * len(options))
        # 确保概率长度和选项一致
        p = p[:len(options)] if len(p) > len(options) else p + [50] * (len(options) - len(p))

        mul_list = []
        max_attempts = 100  # 防止无限循环
        attempts = 0
        while sum(mul_list) <= 0 and attempts < max_attempts:
            mul_list = [numpy.random.choice(a=[0, 1], p=[1 - (item / 100), item / 100]) for item in p]
            attempts += 1

        # 至少选一个（兜底）
        if sum(mul_list) == 0:
            mul_list[random.randint(0, len(mul_list) - 1)] = 1

        for idx, item in enumerate(mul_list):
            if item == 1:
                option_element = driver.find_element(By.CSS_SELECTOR,
                                                    f"#div{current} > div.ui-controlgroup > div:nth-child({idx + 1})")
                option_element.click()

                # 检查是否是"其他"选项并处理文本输入
                option_text = option_element.text
                if "其他" in option_text:
                    # 查找对应的文本输入框
                    try:
                        # 问卷星"其他"选项的文本框通常有以下几种选择器
                        other_input_selectors = [
                            f"#q{current}_other",  # 常见格式
                            f"#div{current} input[type='text']",  # 兜底
                            f"#div{current} textarea"  # 可能是多行文本
                        ]

                        other_input = None
                        for selector in other_input_selectors:
                            try:
                                other_input = driver.find_element(By.CSS_SELECTOR, selector)
                                break
                            except NoSuchElementException:
                                continue

                        if other_input:
                            # 获取当前题目的"其他"选项文本和概率
                            other_text_list = config.get("other_texts", {}).get(str(current), ["其他情况"])
                            other_text_prob = config.get("other_texts_prob", {}).get(str(current), None)

                            # 根据概率选择文本
                            if other_text_prob and len(other_text_prob) == len(other_text_list):
                                # 概率归一化
                                norm_prob = normalize_prob(other_text_prob)
                                # 使用numpy根据概率选择
                                text_index = numpy.random.choice(range(len(other_text_list)), p=norm_prob)
                                other_text = other_text_list[text_index]
                            else:
                                # 无概率配置时，均等随机选择
                                other_text = random.choice(other_text_list)

                            # 输入文本
                            other_input.clear()
                            other_input.send_keys(other_text)
                    except Exception as e:
                        print(f"  处理第{current}题'其他'选项文本失败: {e}")
    except Exception as e:
        print(f"处理多选题{current}失败: {e}")


# 矩阵题处理函数
def matrix(driver: WebDriver, current):
    try:
        xpath1 = f'//*[@id="divRefTab{current}"]/tbody/tr'
        rows = driver.find_elements(By.XPATH, xpath1)
        q_num = sum(1 for tr in rows if tr.get_attribute("rowindex") is not None)
        if q_num == 0:
            return

        xpath2 = f'//*[@id="drv{current}_1"]/td'
        cols = driver.find_elements(By.XPATH, xpath2)
        if not cols:
            return

        # 从配置中按实际题号取矩阵题参数
        matrix_sub_probs = config.get("matrix_prob", {}).get(str(current), [-1] * q_num)

        for i in range(1, q_num + 1):
            # 取对应子题的参数
            p = matrix_sub_probs[i - 1] if (i - 1 < len(matrix_sub_probs)) else -1

            # 计算实际选项数量（cols[0]通常是标题列，后面是选项列）
            actual_options = len(cols) - 1

            if p == -1:
                # 无配置时随机选择
                opt = random.randint(2, len(cols))
            elif isinstance(p, list):
                # 有配置时使用配置的概率
                if len(p) == actual_options:
                    # 概率长度匹配时正常使用
                    norm_p = normalize_prob(p)
                    opt = numpy.random.choice(a=range(2, len(cols) + 1), p=norm_p)
                else:
                    # 概率长度不匹配时，优先使用配置的第一个选项
                    print(f"  概率长度不匹配，使用第一个选项")
                    opt = 2  # 选择第一个选项（对应cols[1]）

            driver.find_element(By.CSS_SELECTOR, f"#drv{current}_{i} > td:nth-child({opt})").click()
    except Exception as e:
        print(f"处理矩阵题{current}失败: {e}")


# 排序题处理函数
def reorder(driver: WebDriver, current):
    try:
        xpath = f'//*[@id="div{current}"]/ul/li'
        options = driver.find_elements(By.XPATH, xpath)
        for j in range(1, len(options) + 1):
            b = random.randint(j, len(options))
            driver.find_element(By.CSS_SELECTOR, f"#div{current} > ul > li:nth-child({b})").click()
            time.sleep(0.4)
    except Exception as e:
        print(f"处理排序题{current}失败: {e}")


# 量表题处理函数
def scale(driver: WebDriver, current):
    try:
        xpath = f'//*[@id="div{current}"]/div[2]/div/ul/li'
        options = driver.find_elements(By.XPATH, xpath)
        if not options:
            return

        # 从配置中按实际题号取参数
        p = config.get("scale_prob", {}).get(str(current), -1)
        if p == -1:
            b = random.randint(1, len(options))
        else:
            norm_p = normalize_prob(p)
            assert len(norm_p) == len(options), f"第{current}题参数长度({len(p)})与选项数({len(options)})不匹配！"
            b = numpy.random.choice(a=range(1, len(options) + 1), p=norm_p)

        driver.find_element(By.CSS_SELECTOR, f"#div{current} > div.scale-div > div > ul > li:nth-child({b})").click()
    except Exception as e:
        print(f"处理量表题{current}失败: {e}")


# ========== 刷题逻辑（修复版） ==========
def brush(driver: WebDriver):
    current = 0
    max_question_check = config.get("max_question_check", 200)  # 从配置读取最大检测题号

    while current < max_question_check:
        current += 1

        # 核心：只处理可见的题目（适配条件逻辑）
        if not is_question_visible(driver, current):
            continue

        try:
            q_type = driver.find_element(By.CSS_SELECTOR, f"#div{current}").get_attribute("type")

            if q_type == "1" or q_type == "2":  # 填空题
                vacant(driver, current)
            elif q_type == "3":  # 单选
                single(driver, current)
            elif q_type == "4":  # 多选
                multiple(driver, current)
            elif q_type == "5":  # 量表题
                scale(driver, current)
            elif q_type == "6":  # 矩阵题
                matrix(driver, current)
            elif q_type == "7":  # 下拉框
                droplist(driver, current)
            elif q_type == "8":  # 滑块题
                score = random.randint(1, 100)
                driver.find_element(By.CSS_SELECTOR, f"#q{current}").send_keys(score)
            elif q_type == "11":  # 排序题
                reorder(driver, current)
            else:
                print(f"第{current}题为不支持题型（类型码：{q_type}），跳过")

        except Exception as e:
            print(f"处理第{current}题时出错: {e}")
            continue

    # 翻页/提交逻辑
    time.sleep(0.5)
    try:
        driver.find_element(By.CSS_SELECTOR, "#divNext").click()
        time.sleep(0.5)
        brush(driver)  # 递归处理下一页
    except:
        try:
            driver.find_element(By.XPATH, '//*[@id="ctlNext"]').click()
            submit(driver)
        except:
            print("未找到提交按钮，尝试直接提交")
            submit(driver)


# 提交函数
def submit(driver: WebDriver):
    time.sleep(1)
    # 点击确认弹窗
    try:
        driver.find_element(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a').click()
        time.sleep(1)
    except:
        pass
    # 智能检测
    try:
        driver.find_element(By.XPATH, '//*[@id="SM_BTN_1"]').click()
        time.sleep(3)
    except:
        pass
    # 滑块验证
    try:
        slider = driver.find_element(By.XPATH, '//*[@id="nc_1__scale_text"]/span')
        sliderButton = driver.find_element(By.XPATH, '//*[@id="nc_1_n1z"]')
        if str(slider.text).startswith("请按住滑块"):
            width = slider.size.get("width")
            ActionChains(driver).drag_and_drop_by_offset(sliderButton, width, 0).perform()
    except:
        pass


# 运行函数
def run(xx, yy):
    global config, current_ip, ip_use_count
    target_num = config.get("target_num", 3)
    fail_threshold = config.get("fail_threshold", target_num / 4 + 1)
    use_ip = True   #config.get("use_ip", False)

    global cur_num, cur_fail
    while True:
        with lock:
            if cur_num >= target_num:
                break

        # ========== IP复用逻辑（核心修复：IP副本+原子操作） ==========
        local_ip = None
        with ip_lock:
            # 首次/IP已用完/无IP时，获取新IP
            if not use_ip or current_ip is None or ip_use_count >= IP_MAX_USE:
                if use_ip:
                    new_ip = zanip()
                    if new_ip:
                        current_ip = new_ip
                        ip_use_count = 0  # 重置使用次数
                    else:
                        current_ip = None
                else:
                    current_ip = None

            # 给当前线程分配「IP副本」（关键！避免后续被其他线程篡改）
            local_ip = current_ip

            # 只有拿到有效IP时，才累加全局使用次数
            if local_ip:
                ip_use_count += 1

        # ========== Edge驱动配置（补全无头+超时+反检测） ==========
        temp_option = Options()

        # 1. 关闭无头模式（弹出浏览器）
        # temp_option.add_argument("--headless=new")
        # temp_option.add_argument("--window-size=1920,1080")  # 无头模式必须指定窗口大小

        # 2. 基础反检测（隐藏webdriver特征）
        temp_option.add_experimental_option("excludeSwitches", ["enable-automation"])
        temp_option.add_experimental_option("useAutomationExtension", False)

        # 3. 指纹伪装：同一IP期间，UA固定；换IP时随机（更真实）
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/118.0.0.0 Safari/537.36"
        ]
        # 用local_ip计算UA索引（而非全局current_ip），确保同一IP的UA一致
        ua_index = hash(local_ip) % len(user_agents) if local_ip else random.randint(0, len(user_agents)-1)
        temp_option.add_argument(f"user-agent={user_agents[ua_index]}")

        # 4. 禁用WebRTC/扩展/GPU（减少特征，防止真实IP泄露）
        temp_option.add_argument("--disable-webrtc")
        temp_option.add_argument("--disable-extensions")
        temp_option.add_argument("--disable-gpu")

        # 5. 开启无痕模式（每次运行清空缓存/Cookie）
        temp_option.add_argument("--incognito")

        # 6. 禁用图片加载（加快页面加载，减少资源消耗）
        temp_option.add_argument("--blink-settings=imagesEnabled=false")

        # 绑定代理IP（用local_ip副本，不再依赖全局变量）
        if use_ip and local_ip:
            temp_option.add_argument(f"--proxy-server={local_ip}")
        else:
            print(f"⚠️ 线程 {threading.current_thread().name} 未使用代理IP，使用本机IP")

        # 初始化Edge驱动 + 超时配置（防止卡死）
        driver = webdriver.Edge(options=temp_option)
        driver.set_window_size(550, 650)
        driver.set_page_load_timeout(15)  # 页面加载超时15秒
        driver.set_script_timeout(10)     # 脚本执行超时10秒

        # 关键：隐藏navigator.webdriver（核心反检测）
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
                Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
                Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            """}
        )

        # ========== 刷题逻辑（补全超时+失败处理） ==========
        try:
            # 显式等待页面加载完成（最多15秒）
            driver.get(config["url"])
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 页面加载后随机延迟（模拟真人等待）
            time.sleep(random.uniform(1.0, 2.5))
            url1 = driver.current_url
            brush(driver)
            time.sleep(random.uniform(4.0, 5.0))
            url2 = driver.current_url

            if url1 != url2:
                with lock:
                    if cur_num >= target_num:
                        continue
                    cur_num += 1
                    print(f"✅ 已填写{cur_num}份 - 失败{cur_fail}次  -执行时间: {time.strftime('%H:%M:%S', time.localtime())}")
        except TimeoutException:
            # 处理页面加载超时
            print(f"❌ 线程 {threading.current_thread().name} 页面加载超时（IP: {local_ip}），更换IP重试")
            with lock:
                cur_fail +=1
            # 超时直接强制换IP
            with ip_lock:
                current_ip = None
                ip_use_count = 0
        except:
            # 原有异常处理逻辑保留
            traceback.print_exc()
            with lock:
                cur_fail +=1
            print("\033[42m", f"❌ 线程 {threading.current_thread().name} 已失败{cur_fail}次,失败超过{int(fail_threshold)}次将强制停止", "\033[0m")

            # 失败时，当前IP使用次数不累计（避免浪费）
            with ip_lock:
                if current_ip and ip_use_count > 0:
                    ip_use_count -= 1

            if cur_fail >= fail_threshold:
                logging.critical("失败次数过多，程序强制停止")
                quit()
        finally:
            # 无论成功/失败，都确保关闭浏览器
            try:
                driver.quit()
            except:
                pass
        continue


# ========== 主函数（补全线程启动延迟） ==========
if __name__ == "__main__":
    # 从命令行参数读取配置
    if len(sys.argv) < 2:
        print("请传入配置参数")
        sys.exit(1)

    try:
        config_json = None

        # 尝试判断第一个参数是文件路径还是直接的JSON字符串
        first_arg = sys.argv[1]

        # 检查是否是文件路径（如果文件存在）
        if os.path.exists(first_arg):
            # 读取临时文件中的JSON配置
            config_file_path = first_arg
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config_json = f.read()
        else:
            # 直接使用命令行参数作为JSON字符串
            config_json = first_arg

        # 解析JSON配置
        config = json.loads(config_json)

        # 处理前端传递的配置结构
        # 检查是否有"传过来的所有问题答案"字段
        if "传过来的所有问题答案" in config:
            questions = config["传过来的所有问题答案"]

            # 初始化配置字典
            texts = {}
            texts_prob = {}
            other_texts = {}
            other_texts_prob = {}
            single_other_texts = {}
            single_other_texts_prob = {}

            # 遍历所有问题
            for question in questions:
                qid = question["id"]
                qtype = question["type"]

                # 处理填空题
                if qtype == "填空题":
                    # 检查是否有textAnswers字段
                    if "textAnswers" in question:
                        text_list = []
                        prob_list = []
                        for answer in question["textAnswers"]:
                            if "text" in answer:
                                text_list.append(answer["text"])
                                prob_list.append(answer.get("probability", 100))
                        if text_list:
                            texts[qid] = text_list
                            texts_prob[qid] = prob_list
                    # 检查是否有options字段
                    elif "options" in question:
                        text_list = []
                        prob_list = []
                        for option in question["options"]:
                            if "text" in option:
                                text_list.append(option["text"])
                                prob_list.append(option.get("probability", 100))
                        if text_list:
                            texts[qid] = text_list
                            texts_prob[qid] = prob_list

                # 处理多选题的其他选项文本
                elif qtype == "多选题":
                    if "optionTextAnswers" in question:
                        for option_index, text_answers in question["optionTextAnswers"].items():
                            text_list = []
                            prob_list = []
                            for answer in text_answers:
                                if "text" in answer:
                                    text_list.append(answer["text"])
                                    prob_list.append(answer.get("probability", 100))
                            if text_list:
                                other_texts[qid] = text_list
                                other_texts_prob[qid] = prob_list

                # 处理单选题的其他选项文本
                elif qtype == "单选题":
                    if "optionTextAnswers" in question:
                        for option_index, text_answers in question["optionTextAnswers"].items():
                            text_list = []
                            prob_list = []
                            for answer in text_answers:
                                if "text" in answer:
                                    text_list.append(answer["text"])
                                    prob_list.append(answer.get("probability", 100))
                            if text_list:
                                single_other_texts[qid] = text_list
                                single_other_texts_prob[qid] = prob_list

            # 更新配置对象
            if texts:
                config["texts"] = texts
            if texts_prob:
                config["texts_prob"] = texts_prob
            if other_texts:
                config["other_texts"] = other_texts
            if other_texts_prob:
                config["other_texts_prob"] = other_texts_prob
            if single_other_texts:
                config["single_other_texts"] = single_other_texts
            if single_other_texts_prob:
                config["single_other_texts_prob"] = single_other_texts_prob

        # 初始化全局变量
        target_num = config.get("target_num", 3)
        fail_threshold = config.get("fail_threshold", target_num / 4 + 1)
        cur_num = 0
        cur_fail = 0

        # 获取线程数配置
        num_threads = config.get("num_threads", 2)  # 默认双线程

        # 启动多线程（加延迟，避免同时竞争）
        threads: list[Thread] = []
        for i in range(num_threads):
            x = 50 + i * 60
            y = 50
            thread = Thread(target=run, args=(x, y))
            threads.append(thread)
            time.sleep(0.5)  # 线程启动延迟0.5秒，减少资源竞争
            thread.start()

        for thread in threads:
            thread.join()
            
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行出错: {e}")
        traceback.print_exc()
        sys.exit(1)