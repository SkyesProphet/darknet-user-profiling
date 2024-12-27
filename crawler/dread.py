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
from selenium.common import NoSuchElementException
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException
from datetime import datetime


db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='tnh123456', db='darknetwork', charset='utf8mb4')
# cursor = db.cursor()
domain ='http://g66ol3eb5ujdckzqqfmjsbpdjufmjd5nsgdipvxmsh7rckzlhywlzlqd.onion/d/OpSec'

# 记录开始时间
start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def insertDB(db, user_id, username, content, votes, title, timestamp):
    try:
        # 创建游标
        with db.cursor() as cursor:
            # 如果没有提供 timestamp，则使用当前时间
            if not timestamp:
                timestamp = '0000-00-00 00:00:00'

            # 插入新评论
            insert_sql = """
                INSERT INTO comments (user_id, username, content, votes, title, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (user_id, username, content, votes, title, timestamp))
            db.commit()
            print(f"Inserted new comment for user_id: {user_id}")
            return True

    except pymysql.MySQLError as e:
        print(f"Error inserting data into the database: {e}")
        db.rollback()
        return False

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        db.rollback()
        return False

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

# 检查网页正确连接
# 检查网页是否成功连接并加载
def check_link(url, max_retries=3, timeout=120):
    for attempt in range(max_retries):
        try:
            # 初始化浏览器
            driver = get_tor_browser()

            # 设置隐式等待时间（可选）
            driver.implicitly_wait(10)

            # 打开网页
            driver.get(url)

            # 使用显式等待，确保页面完全加载
            wait = WebDriverWait(driver, timeout)
            try:
                # 等待页面中的某个元素加载完成，作为页面加载成功的标志
                # 你可以选择一个页面上一定会出现的元素，例如评论容器、文章标题等
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.item')))
                print("页面加载成功，跳出循环...")
                return driver
            except TimeoutException:
                print(f"页面在 {timeout} 秒内未加载完成，尝试重新加载... (尝试次数: {attempt + 1}/{max_retries})")
                driver.quit()  # 关闭当前浏览器实例
                continue

        except WebDriverException as e:
            print(f"发生异常: {e}")
            if attempt < max_retries - 1:
                print(f"尝试重新加载... (尝试次数: {attempt + 1}/{max_retries})")
                continue
            else:
                print("达到最大重试次数，放弃加载。")
                raise

    print("所有尝试均失败，无法加载页面。")
    return None

# 获取网站所有帖子的链接，先运行这个函数，再运行爬取评论函数
def GetLinks(driver, db):
    try:
        # 初始化游标
        cursor = db.cursor()

        while True:
            try:
                # 等待.postBoard元素出现，以确保页面已经加载完毕
                wait = WebDriverWait(driver, 10)
                post_board = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.postBoard')))
                
                # 查找所有包含文章的.item元素
                items = post_board.find_elements(By.CSS_SELECTOR, '.item')
                
                for item in items:
                    try:
                        # 在每个.item元素的上下文中查找标题链接
                        title_element = item.find_element(By.CSS_SELECTOR, 'a.title')
                        
                        # 尝试获取href属性，若失败则提供默认值
                        href = title_element.get_attribute('href') or 'No href attribute'
                        title = title_element.text.strip()  # 移除标题文本中的多余空白
                        
                        # 打印标题和URL在同一行
                        print(f"Title: {title}, URL: {href}")
                        
                        # 检查该URL是否已经在数据库中存在
                        check_sql = "SELECT COUNT(*) FROM dread_url WHERE url = %s"
                        cursor.execute(check_sql, (href,))
                        count = cursor.fetchone()[0]
                        
                        if count == 0:
                            # 如果URL不存在，则插入新记录，默认 is_crawled 为 0
                            insert_sql = """
                                INSERT INTO dread_url (url, is_crawled)
                                VALUES (%s, 0)
                            """
                            cursor.execute(insert_sql, (href,))
                            db.commit()
                            print(f"Inserted new URL: {href}")
                        else:
                            print(f"URL already exists: {href}")

                    except NoSuchElementException:
                        print("Warning: No title link found within this item.")
                    
                    except Exception as e:
                        db.rollback()  # 发生错误时回滚事务
                        print(f"Error processing item: {e}")
            
            except TimeoutException:
                print("Error: The page did not load within the expected time.")
                break
            
            except Exception as e:
                db.rollback()  # 发生错误时回滚事务
                print(f"An unexpected error occurred: {e}")
                break

            # 检查是否存在“下一页”按钮
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, '.next')
                if not next_button.is_displayed() or not next_button.is_enabled():
                    print("No more pages to load.")
                    break
                
                # 点击“下一页”按钮
                next_button.click()
                print("Navigating to the next page...")
                
                # 等待页面加载完成（可以根据需要调整等待时间）
                wait.until(EC.staleness_of(post_board))  # 等待当前页面的.postBoard元素失效
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.postBoard')))  # 等待新的.postBoard元素出现
                
            except NoSuchElementException:
                print("No 'Next Page' button found. Assuming this is the last page.")
                break
            
            except ElementClickInterceptedException:
                print("Error: Click on 'Next Page' button was intercepted. Trying again...")
                continue
            
            except Exception as e:
                print(f"Error navigating to the next page: {e}")
                break

    finally:
        # 关闭游标
        cursor.close()
        # 关闭数据库连接
        db.close()

# 爬取评论并存储到数据库
def scrape_comments(driver, title_url):
    try:
        # 打开文章页面
        driver.get(title_url)
        # 使用显式等待，确保页面完全加载
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.comment')))

        # 提取文章标题
        title = driver.find_element(By.CSS_SELECTOR, '.title').text.strip()
    
        # 等待页面加载完成
        # 获取所有评论（包括顶级评论和子评论）
        comments = driver.find_elements(By.CSS_SELECTOR, '.comment')

        for comment in comments:
            try:
                # 提取评论的唯一 ID
                user_id = comment.get_attribute('id')

                # 提取用户名
                username = comment.find_element(By.CSS_SELECTOR, 'a.username').text.strip()

                # 提取评论内容
                content = comment.find_element(By.CLASS_NAME, 'commentBody').text.strip()

                # 提取投票数
                votes = int(comment.find_element(By.CLASS_NAME, 'votes').text.split()[0])

                # 提取时间戳
                timestamp = comment.find_element(By.CLASS_NAME, 'timestamp').find_element(By.TAG_NAME, 'span').get_attribute('title')

                # 存入数据库
                insertDB(db, user_id, username, content, votes, title, timestamp)
                '''# 打印评论信息，按照指定格式
                print(f"Title: {title}")
                print(f"ID: {user_id}")
                print(f"Username: {username}")
                print(f"Content: {content}")
                print(f"Votes: {votes}")
                print(f"Timestamp: {timestamp}")
                print("-" * 50)  # 分隔线
                '''
            except NoSuchElementException:
                print("评论格式不正确，跳过此评论")
            except Exception as e:
                print(f"Error processing comment: {e}")

    except TimeoutException:
        print("Error: The article page did not load within the expected time.")
    except Exception as e:
        print(f"An unexpected error occurred while scraping comments: {e}")

    finally:
        # 返回到原始页面（如果需要）
        driver.back()

# 从指定网址获取评论
def get_comments(driver):
    try:
        with db.cursor() as cursor:
            # 获取所有未爬取的 URL，爬取过的会标记
            select_sql = "SELECT id, url FROM dread_url WHERE is_crawled = 0 LIMIT 1 FOR UPDATE;"
            while True:
                cursor.execute(select_sql)
                article = cursor.fetchone()
                
                if not article:
                    print("No more uncrawled URLs to process.")
                    break
                
                url_id, url = article

                print(f"Processing URL: {url}")

                try:
                    # 调用 scrape_comments 函数爬取评论
                    scrape_comments(driver, url)

                    # 标记,更新 is_crawled 为 1 表示已爬取
                    update_sql = "UPDATE dread_url SET is_crawled = 1 WHERE id = %s;"
                    cursor.execute(update_sql, (url_id,))
                    db.commit()
                    print(f"URL {url} has been successfully crawled and marked as crawled.")

                except Exception as e:
                    print(f"Error crawling URL {url}: {e}")
                    db.rollback()

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        db.rollback()

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        db.rollback()

    finally:
        # 关闭游标
        if 'cursor' in locals():
            cursor.close()

# 主函数
def main():
    global start_time
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"Start Time: {start_time}")

    # 检查并打开目标网页
    driver = check_link(domain)
    if not driver:
        print("Failed to open the target webpage. Exiting...")
        return

    try:
        # 爬取所有帖子链接,已爬取
        # GetLinks(driver, db)  # 首次先运行Getlinks函数获取网站所有url
       
        # 爬取评论
        get_comments(driver)     # 针对各url调用数据库依次爬取

        # 记录结束时间
        end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"End Time: {end_time}")
        # print(f"Total articles crawled: {craw_count}")

    finally:
        # 关闭浏览器
        driver.quit()
        # 关闭数据库连接
        # db.close()

if __name__ == "__main__":
    main()
