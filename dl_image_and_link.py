import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
import os
import urllib.parse
import time

def setup_driver(edge_driver_path):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    ]
    options = webdriver.EdgeOptions()
    options.add_argument("start-maximized")
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    service = EdgeService(executable_path=edge_driver_path)
    driver = webdriver.Edge(service=service, options=options)
    return driver

def is_valid_extension(extension):
    return extension.lower() == '.jpg'

def debug_element_details(elements, description):
    print(f"{description} - Total elements found: {len(elements)}")
    for idx, element in enumerate(elements[:5]):  # 只显示前5个元素的部分内容
        print(f"{description} {idx + 1}: {element.get_attribute('outerHTML')[:100]}...")

def load_page_with_retry(driver, url, max_retry=5):
    retry_count = 0
    while retry_count < max_retry:
        try:
            driver.get(url)
            print("等待页面加载完成...")
            if wait_for_element(driver, By.TAG_NAME, 'body', timeout=7):
                print(f"页面已加载: {driver.current_url}")
                return True
            else:
                retry_count += 1
                print(f"页面加载超时，重试第 {retry_count} 次，刷新页面...")
                driver.refresh()
                time.sleep(2)  # 刷新页面后短暂等待
        except Exception as e:
            retry_count += 1
            print(f"页面加载异常，重试第 {retry_count} 次，错误: {e}")
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            time.sleep(2)  # 刷新页面后短暂等待
            driver.refresh()

    print(f"超过最大重试次数，加载失败: {url}")
    return False

def wait_for_element(driver, by, value, timeout=7):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return True
    except Exception:
        return False

def download_images_from_url(driver, url, folder_prefix):
    print(f"正在访问链接: {url}")
    if not load_page_with_retry(driver, url):
        return

    try:
        # 输出部分HTML内容用于调试
        print("页面部分内容预览:")
        print(driver.page_source[:500])

        # 等待图片元素加载
        print("等待图片元素加载...")
        if not wait_for_element(driver, By.TAG_NAME, 'img', timeout=10):
            print(f"图片元素加载失败: {url}")
            return
        print("图片元素已加载。")

        # 获取所有图片元素
        print("获取图片元素...")
        images = driver.find_elements(By.TAG_NAME, 'img')
        debug_element_details(images, "Image")
        print(f"发现图片数量: {len(images)}")

        for idx, img in enumerate(images):
            src = img.get_attribute('src')
            print(f"图片链接: {src}")
            if src:
                # 解析图片URL以获取文件扩展名
                parsed_url = urllib.parse.urlparse(src)
                file_name, file_extension = os.path.splitext(parsed_url.path)

                # 对于一些带有参数的URL，需移除参数
                if '?' in file_extension:
                    file_extension = file_extension.split('?')[0]

                # 只下载.jpg图片
                if not is_valid_extension(file_extension):
                    print(f"跳过非.jpg图片: {src}")
                    continue

                # 定义文件路径和名称
                img_file_path = f'images/{folder_prefix}_img_{idx}{file_extension}'

                try:
                    # 下载图片并保存
                    print(f"下载图片: {src}")
                    img_data = requests.get(src).content
                    with open(img_file_path, 'wb') as handler:
                        handler.write(img_data)
                    print(f'下载成功: {folder_prefix}_img_{idx}{file_extension}')
                except Exception as e:
                    print(f'下载失败: {e}')
                
                # 每次下载完图片后，等待1秒再处理下一张
                time.sleep(1)

    except Exception as e:
        print(f'页面加载或处理失败: {url}, 错误: {e}')

    # 每次下载完一页后，等待5秒再处理下一页
    time.sleep(5)

def find_post_links_from_main_url(driver, main_url):
    print(f"正在访问主链接: {main_url}")
    if not load_page_with_retry(driver, main_url):
        return []

    try:
        # 输出部分HTML内容用于调试
        print("主页部分内容预览:")
        print(driver.page_source[:500])

        # 查找所有指向帖子的链接
        print("查找帖子链接...")
        links = driver.find_elements(By.TAG_NAME, 'a')
        debug_element_details(links, "Link")
        post_links = []
        seen_links = set()
        for link in links:
            href = link.get_attribute('href')
            # 排除重复链接，并确保是帖子链接
            if href and '/p/' in href and href not in seen_links:
                print(f"发现帖子链接: {href}")
                post_links.append(href)
                seen_links.add(href)

        print(f"发现帖子链接数量: {len(post_links)}")
        return post_links

    except Exception as e:
        print(f'主页加载或处理失败: {main_url}, 错误: {e}')
        return []

if __name__ == "__main__":
    edge_driver_path = '.venv\Scripts\msedgedriver.exe'  # 请根据实际路径调整
    main_url = 'https://tieba.baidu.com/f?kw=%E6%88%91%E7%9A%84%E9%9D%92%E6%98%A5%E6%81%8B%E7%88%B1%E7%89%A9%E8%AF%AD%E6%9E%9C%E7%84%B6%E6%9C%89%E9%97%AE%E9%A2%98&tab=album&subtab=album_good&cat_id=a51aaa1ea8d3fd1fc11a960a304e251f95ca5f7b'

    driver = setup_driver(edge_driver_path)

    # 创建保存图片的文件夹
    if not os.path.exists('images'):
        os.makedirs('images')

    try:
        # Step 1: 从主页上下载图片
        print("从主页下载图片...")
        download_images_from_url(driver, main_url, "main")

        # Step 2: 从主链接查找所有可以跳转的帖子链接
        post_links = find_post_links_from_main_url(driver, main_url)

        # 确保已收集到所有帖子链接后再处理

        print(f"收集到的帖子链接数量: {len(post_links)}")

        # Step 3: 从主页开始处理这些帖子链接，逐个爬取图片
        if post_links:
            for index, post_link in enumerate(post_links, start=1):
                print(f"开始处理 {index}/{len(post_links)}: {post_link}")
                download_images_from_url(driver, post_link, f"post_{index}")
                print(f"处理完成 {index}/{len(post_links)}: {post_link}")
        else:
            print("未找到任何帖子链接。")
    finally:
        # 关闭WebDriver
        driver.quit()