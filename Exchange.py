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
domain = 'http://mxxxxxxxs4uqwd6cylditj7rh7zaz2clh7ofgik2z5jpeq5ixn4ziayd.onion/route/login.php'  # 目标网站域名
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
    options.binary_location = "{FIREFOX_PATH}"    # 替换为Firefox浏览器可执行文件路径
    
    # 设置geckodriver驱动路径
    service = Service(executable_path="geckodriver.exe")    # 替换为geckodriver可执行文件路径
    
    return webdriver.Firefox(service=service, options=options)

def wait_and_find_element(driver, by, value, timeout=60):
    """
    等待并查找元素，带有超时处理
    
    参数:
        driver: Selenium WebDriver实例
        by: 定位方式(如By.ID, By.CLASS_NAME等)
        value: 定位值
        timeout: 超时时间(秒),默认60秒
        
    返回:
        WebElement: 找到的元素,如果超时则返回None
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
        product_data (dict): 包含商品信息的字典
        categories: 商品分类信息（当前未使用）
    """
    file_path = "Exchange.txt"    # 替换为实际的输出文件路径
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n----------------------------------------\n")
        f.write(f"序号: {product_data['序号']}\n")
        f.write(f"卖家ID: {product_data['卖家ID']}\n")
        f.write(f"商品标题: {product_data['标题']}\n")
        f.write(f"单价(USD): {product_data['单价']}\n")
        f.write(f"成交额: {product_data['成交额']}\n")
        f.write(f"成交量: {product_data['成交量']}\n")
        f.write(f"好评:风险: {product_data['好评:风险']}\n")
        f.write(f"咨询数: {product_data['咨询数']}\n")
        f.write(f"热度: {product_data['热度']}\n")
        f.write(f"卖家在线时长: {product_data['卖家在线时长']}\n")
        f.write("----------------------------------------\n")

def crawl_products_on_page(driver):
    """
    爬取当前页面的所有产品信息
    
    参数:
        driver: Selenium WebDriver实例
    """
    global craw_count
    
    try:
        # 等待表格加载完成
        print("等待表格数据加载...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )
        
        # 获取所有商品行
        rows = driver.find_elements(By.TAG_NAME, "tr")    # 跳过表头和分隔行
        print(f"找到 {len(rows)} 行数据")
        
        for row in rows:
            try:
                # 跳过非商品行
                if row.find_elements(By.CSS_SELECTOR, "td[colspan='13']"):    # 跳过表头和分隔行
                    continue
                    
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 10:    # 确保至少有必要的列数
                    continue
                    
                # 检查是否为有效商品行
                if not cells[0].text.strip().isdigit():    # 序号列作为检查
                    continue
                    
                try:
                    # 提取商品信息
                    product_data = {
                        "序号": str(0 + int(cells[0].text.strip())),
                        "卖家ID": cells[1].text.strip(),
                        "标题": cells[2].find_element(By.TAG_NAME, "a").text.strip(),
                        "单价": cells[3].text.strip(),
                        "成交额": cells[4].text.strip(),
                        "成交量": cells[5].text.strip(),
                        "好评:风险": cells[6].text.strip(),
                        "咨询数": cells[7].text.strip(),
                        "热度": cells[8].text.strip(),
                        "卖家在线时长": cells[9].text.strip()
                    }
                    
                    # 保存商品数据
                    write_product_to_file(product_data, None)
                    
                    # 打印商品信息
                    print(f"序号: {product_data['序号']}")
                    print(f"卖家ID: {product_data['卖家ID']}")
                    print(f"商品标题: {product_data['标题']}")
                    print(f"单价(USD): {product_data['单价']}")
                    print(f"成交额: {product_data['成交额']}")
                    print(f"成交量: {product_data['成交量']}")
                    print(f"好评:风险: {product_data['好评:风险']}")
                    print(f"咨询数: {product_data['咨询数']}")
                    print(f"热度: {product_data['热度']}")
                    print(f"卖家在线时长: {product_data['卖家在线时长']}")
                    print("----------------------------------------")
                    craw_count += 1
                    
                except Exception as e:
                    print(f"处理商品数据时出错: {str(e)}")
                    continue
                    
            except Exception as e:
                print(f"处理行数据时出错: {str(e)}")
                continue
                
            time.sleep(random.uniform(0.5, 1))    # 随机延迟，避免请求过快
            
    except Exception as e:
        print(f"爬取页面数据时出错: {str(e)}")
        
    print(f"当前页面处理完成，已爬取总数据: {craw_count}")

def main():
    """
    主函数，控制整个爬虫流程
    """
    global craw_count
    driver = None
    
    try:
        print("启动浏览器...")
        driver = get_tor_browser()
        
        # 访问目标网站
        initial_url = domain
        print("正在访问网站...")
        driver.get(initial_url)
        
        print("等待Tor网络连接...")
        time.sleep(30)    # 等待Tor网络建立连接
        
        # 检查页面加载状态
        print("等待页面加载...")
        max_retries = 10    # 最大重试次数
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 验证页面加载状态
                current_url = driver.current_url
                if "onion" not in current_url:
                    print(f"尝试 {retry_count + 1}/{max_retries}: 等待Tor连接...")
                    time.sleep(30)
                    retry_count += 1
                    continue
                
                # 检查页面内容
                if "Error" in driver.title or "无法访问" in driver.page_source:
                    print(f"尝试 {retry_count + 1}/{max_retries}: 页面加载出错，重试中...")
                    driver.refresh()
                    time.sleep(30)
                    retry_count += 1
                    continue
                
                # 等待数据表格加载
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                
                # 验证数据是否加载完成
                rows = driver.find_elements(By.TAG_NAME, "tr")
                if len(rows) > 1:    # 检查是否有实际数据行
                    print("页面加载成功！")
                    break
                    
                print(f"尝试 {retry_count + 1}/{max_retries}: 等待数据加载...")
                time.sleep(30)
                retry_count += 1
                
            except TimeoutException:
                print(f"尝试 {retry_count + 1}/{max_retries}: 页面加载超时，重试中...")
                driver.refresh()
                time.sleep(30)
                retry_count += 1
                continue
            except Exception as e:
                print(f"尝试 {retry_count + 1}/{max_retries}: 发生错误 {str(e)}")
                time.sleep(30)
                retry_count += 1
                continue
        
        if retry_count >= max_retries:
            print("页面加载失败，请检查网络连接或网站可用性")
            return
            
        print("开始爬取数据...")
        current_page = 1
        
        # 循环处理每一页数据
        while True:
            try:
                print(f"\n正在爬取第 {current_page} 页...")
                time.sleep(15)    # 每页处理前等待
                
                # 爬取当前页面的产品
                crawl_products_on_page(driver)
                
                # 查找分页按钮
                page_buttons = driver.find_elements(By.CLASS_NAME, "button_page")
                if not page_buttons:
                    print("未找到分页按钮")
                    break
                
                # 处理翻页
                next_page_found = False
                for button in page_buttons:
                    if button.text.strip() == str(current_page + 1):
                        parent = button.find_element(By.XPATH, "./..")    # 获取父元素
                        if parent.tag_name == "a":    # 确保是可点击的链接
                            next_url = parent.get_attribute('href')
                            if next_url:
                                print(f"找到第 {current_page + 1} 页链接")
                                current_page += 1
                                driver.get(next_url)
                                time.sleep(15)    # 翻页后等待加载
                                next_page_found = True
                                break
                
                if not next_page_found:
                    print("已到达最后一页")
                    break
                    
            except TimeoutException:
                print("页面加载超时，尝试重新加载...")
                driver.refresh()
                time.sleep(30)
                continue
            except Exception as e:
                print(f"处理页面时出错: {e}")
                time.sleep(30)
                continue

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