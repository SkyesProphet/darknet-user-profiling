import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

# 基础配置
domain = 'http://xbtppbb7oz5j2stohmxzvkprpqw5dwmhhhdo2ygv6c7cs4u46ysufjyd.onion/market'    # 目标网站域名
craw_count = 0    # 爬取计数器
start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())    # 记录开始时间

def get_tor_browser():
    """
    配置并返回一个使用Tor代理的Firefox浏览器实例
    
    返回:
        webdriver.Firefox: 配置好的Firefox浏览器实例
    """
    options = Options()
    options.headless = False    # 设置为True则不显示浏览器窗口
    
    # 配置Tor代理设置
    options.set_preference('network.proxy.type', 1)
    options.set_preference('network.proxy.socks', '127.0.0.1')
    options.set_preference('network.proxy.socks_port', 9150)    # Tor代理端口
    options.set_preference('network.proxy.socks_version', 5)
    options.set_preference('network.proxy.socks_remote_dns', True)
    
    # 设置Firefox浏览器路径
    options.binary_location = "{FIREFOX_PATH}"    # Firefox浏览器路径
    
    # 设置geckodriver驱动路径
    service = Service(executable_path="geckodriver.exe")    # geckodriver驱动路径
    
    return webdriver.Firefox(service=service, options=options)

def wait_and_find_element(driver, by, value, timeout=60):
    """
    等待并查找元素，带有超时处理
    
    参数:
        driver: WebDriver实例
        by: 定位方式
        value: 定位值
        timeout: 超时时间（秒）
        
    返回:
        WebElement或None: 找到的元素或None(如果超时)
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"等待元素超时: {value}")
        return None

def write_product_to_file(product_data, categories):
    """
    将商品数据写入指定文件
    
    参数:
        product_data (dict): 商品数据字典
        categories: 商品分类（当前未使用）
    """
    file_path = "freecity.txt"    # 输出文件路径
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n----------------------------------------\n")
        f.write(f"序号: {product_data['序号']}\n")
        f.write(f"标题: {product_data['标题']}\n")
        f.write(f"价格: {product_data['价格']}\n")
        f.write(f"卖家: {product_data['卖家']}\n")
        f.write("----------------------------------------\n")

def simulate_human_behavior(driver):
    """
    模拟人类浏览行为，增加随机性
    
    参数:
        driver: WebDriver实例
    """
    try:
        scroll_amount = random.randint(300, 1000)    # 随机滚动距离
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(1, 3))    # 随机等待时间
        
        if random.random() < 0.3:    # 30%概率向上滚动
            driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
            time.sleep(random.uniform(0.5, 2))
    except Exception as e:
        print(f"模拟人类行为时出错: {e}")

def get_all_product_links(driver):
    """
    获取所有页面的商品链接
    
    参数:
        driver: WebDriver实例
        
    返回:
        list: 商品链接列表
    """
    all_product_links = set()    # 使用集合去重
    current_page = 1
    max_retries = 3    # 最大重试次数
    
    while True:
        retry_count = 0
        while retry_count < max_retries:
            try:
                print(f"\n正在获取第 {current_page} 页的商品链接...")
                time.sleep(random.uniform(3, 15))    # 随机等待时间
                
                simulate_human_behavior(driver)    # 模拟人类行为
                
                # 获取商品链接
                elements = driver.find_elements(By.CLASS_NAME, "tradeitem")
                page_links = set()
                for element in elements:
                    try:
                        href = element.get_attribute('href')
                        if href:
                            page_links.add(href)
                        time.sleep(random.uniform(0.1, 0.5))
                    except:
                        continue
                
                print(f"第 {current_page} 页找到 {len(page_links)} 个商品链接")
                all_product_links.update(page_links)
                
                time.sleep(random.uniform(20, 45))    # 翻页前随机等待
                
                # 处理翻页
                next_page_found = False
                pagination = driver.find_element(By.CLASS_NAME, "pagination")
                page_links = pagination.find_elements(By.TAG_NAME, "li")
                
                for link in page_links:
                    try:
                        if "active" in link.get_attribute("class") or "disabled" in link.get_attribute("class"):
                            continue
                            
                        a_tag = link.find_element(By.TAG_NAME, "a")
                        href = a_tag.get_attribute("href")
                        page_text = a_tag.text
                        
                        if href and page_text.isdigit() and int(page_text) == current_page + 1:
                            print(f"找到第 {current_page + 1} 页链接")
                            current_page += 1
                            driver.get(href)
                            next_page_found = True
                            break
                    except Exception as e:
                        continue
                
                if not next_page_found:
                    print("所有页面链接获取完成")
                    break
                
                break    # 成功则跳出重试循环
                
            except Exception as e:
                retry_count += 1
                print(f"获取页面链接时出错 (尝试 {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    time.sleep(random.uniform(20, 45) * retry_count)
                else:
                    print("达到最大重试次数，跳过当前页面")
                    break
        
        if not next_page_found:
            break
    
    print(f"总共获取到 {len(all_product_links)} 个商品链接")
    return list(all_product_links)

def main():
    """
    主函数，控制整个爬虫流程
    """
    global craw_count
    driver = None
    max_retries = 3    # 最大重试次数
    
    try:
        print("启动浏览器...")
        driver = get_tor_browser()
        
        print("正在访问网站...")
        driver.get(domain)
        
        print("等待Tor网络连接和登录时间...")
        time.sleep(random.uniform(45, 90))    # 初始连接随机等待
        
        print("开始获取所有商品链接...")
        all_product_links = get_all_product_links(driver)
        
        print("\n开始处理商品数据...")
        for link in all_product_links:
            retry_count = 0
            while retry_count < max_retries:
                try:
                    driver.get(link)
                    time.sleep(random.uniform(15, 35))    # 访问商品页面间随机等待
                    
                    simulate_human_behavior(driver)    # 模拟人类行为
                    
                    # 提取商品信息
                    title = driver.find_element(By.XPATH, "//div[@class='note text-light']").text.strip() or "无标题"
                    
                    try:
                        price_div = driver.find_element(By.XPATH, "//div[@class='col-md-6']/p[contains(text(), '价格:')]")
                        price = price_div.text.replace('价格:', '').strip()
                    except:
                        price = "未标价"
                        
                    try:
                        seller = driver.find_element(By.XPATH, "//h5[text()='关于卖家']/following-sibling::p").text.strip()
                    except:
                        seller = "未知卖家"
                    
                    # 构建商品数据
                    product_data = {
                        "序号": str(craw_count + 1),
                        "标题": title,
                        "价格": price,
                        "卖家": seller
                    }
                    
                    # 保存商品数据
                    write_product_to_file(product_data, [])
                    
                    # 打印商品信息
                    print("\n----------------------------------------")
                    print(f"序号: {product_data['序号']}")
                    print(f"标题: {product_data['标题']}")
                    print(f"价格: {product_data['价格']}")
                    print(f"卖家: {product_data['卖家']}")
                    print("----------------------------------------")
                    
                    craw_count += 1
                    time.sleep(random.uniform(5, 15))    # 处理完商品后随机等待
                    break
                    
                except Exception as e:
                    retry_count += 1
                    print(f"处理商品数据时出错 (尝试 {retry_count}/{max_retries}): {str(e)}")
                    if retry_count < max_retries:
                        time.sleep(random.uniform(15, 35) * retry_count)
                    else:
                        print("达到最大重试次数，跳过当前商品")
                        break

    except Exception as e:
        print(f"爬取过程中出现错误: {e}")
        
    finally:
        if driver:
            driver.quit()
        print(f"\n爬取完成,共获取 {craw_count} 条数据")
        print(f"开始时间: {start_time}")
        print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

if __name__ == "__main__":
    main()