import random
import time
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='tnh123456', db='darknetwork', charset='utf8')
cursor = db.cursor()
crawId = random.randint(1, 10000)
domain = 'http://24hourszdh472wmgdccon4daihqfutw37leemsbrvwxxdd44n2vxu4id.onion/'
# domain ='http://g66ol3eb5ujdckzqqfmjsbpdjufmjd5nsgdipvxmsh7rckzlhywlzlqd.onion/d/OpSec'
# 爬取商品的个数
craw_count = 0
# 记录开始时间
start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
def insertLog(id,website_id, website_name, craw_start_time, craw_end_time,craw_count):

    try:
        sql = """  
            INSERT INTO website_craw(id,website_id,website_name,craw_start_time,craw_end_time,craw_count)   
            VALUES (%s,%s,%s,%s, %s, %s)  
        """
        cursor.execute(sql, (id,website_id,website_name,craw_start_time,craw_end_time,craw_count))
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)

def selectDomainId(website_name):
    # 使用参数化查询来避免SQL注入
    sql = 'SELECT id FROM websites WHERE domain = %s'
    cursor.execute(sql, (website_name,))
    rest = cursor.fetchone()
    return rest[0] if rest else None  # 返回id或None

def insertDB( name,price,description,domain,stock,craw_id):
    try:
        sql = """  
            INSERT INTO goods_net(name,price,description,domain,stock,craw_id)   
            VALUES (%s, %s, %s, %s, %s,%s)  
        """
        cursor.execute(sql, (name,price,description,domain,stock,craw_id))
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)

# 设置 Firefox 使用 Tor 的代理
def get_tor_browser():
    options = Options()
    options.headless = False  # 如果需要无头浏览，设为 True
        # 配置 Firefox 使用本地的 Tor 代理
    options.set_preference('network.proxy.type', 1)
    options.set_preference('network.proxy.socks', '127.0.0.1')
    options.set_preference('network.proxy.socks_port', 9150)
    options.set_preference('network.proxy.socks_remote_dns', True)
    # 设置 Firefox 二进制文件的路径
    options.binary_location = r"D:\Study Tools\Tor Browser\Browser\firefox.exe"
    # 配置firefox文件
    profile = FirefoxProfile(r"D:\Study Tools\Tor Browser\Browser\TorBrowser\Data\Browser\profile.default")
    options.profile = profile
    # 设置 geckodriver 的路径
    service = Service(executable_path=r"D:\Dev Tools\geckodriver\geckodriver.exe")  # 请将路径替换为实际的 geckodriver 路径
    driver = webdriver.Firefox(service=service, options=options)

    return driver

driver = None
try:
    # 启动带有 Tor 代理的浏览器
    driver = get_tor_browser()
    driver.get("http://24hourszdh472wmgdccon4daihqfutw37leemsbrvwxxdd44n2vxu4id.onion/")
    # /html/body/form/p[2]/input
    # 等待输入框元素加载完成
    input = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/form/p[2]/input"))
    )
    input.send_keys('24SezAm') # 输入验证码

    # 等待提交按钮加载完成
    button = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/form/input'))
    )
    button.click() # 点击提交验证码

    # 等待页面上的表格加载完成
    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.XPATH, '/html/body/div[1]/div/div[3]/div[3]/table'))
    )

    table_products = driver.find_elements(by=By.XPATH, value='/html/body/div[1]/div/div[3]/div[3]/table')

    for table_product in table_products:
        # 找到里面的tr标签 带有 odd 或者 even
        odd_element = table_product.find_elements(by=By.CLASS_NAME, value='odd')
        even_element = table_product.find_elements(by=By.CLASS_NAME, value='even')
        for odd in odd_element:
            name = WebDriverWait(odd, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div/div[3]/div[3]/table[1]/tbody/tr[2]/td[1]/a"))
            ).get_attribute('title')
            description = odd.find_element(by=By.CLASS_NAME, value="product_desc").text
            price = odd.find_element(by=By.CLASS_NAME, value="product_price").text.split('$')[-1].split('\n')[0].strip()
            print(price)
            craw_count = craw_count + 1
            insertDB(name, price, description, domain, None, crawId)
        for even in even_element:
            name = WebDriverWait(even, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div/div[3]/div[3]/table[1]/tbody/tr[2]/td[1]/a"))
            ).get_attribute('title')
            description = even.find_element(by=By.CLASS_NAME, value="product_desc").text
            price = even.find_element(by=By.CLASS_NAME, value="product_price").text.split('$')[-1].split('\n')[
                0].strip()
            craw_count = craw_count + 1
            insertDB(name, price, description, domain, None, crawId)
        time.sleep(random.uniform(10, 20))

except Exception as e:
    print(e)

finally:
    # 记录结束时间
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    website_id = selectDomainId(domain)
    insertLog(crawId,website_id,domain,start_time,end_time,craw_count)
    # 关闭 WebDriver
    # if driver is not None:
        # driver.quit()
