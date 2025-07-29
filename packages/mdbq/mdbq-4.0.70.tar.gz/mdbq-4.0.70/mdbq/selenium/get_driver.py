# -*- coding:utf-8 -*-
import os
import platform
import getpass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import re
import socket
import tempfile
import shutil
import uuid

dir_path = os.path.expanduser("~")


class GetDriverException(Exception):
    """自定义异常：GetDriver相关错误"""
    pass


class GetDriver:
    """
    Selenium ChromeDriver 管理器，支持多平台、代理、无头模式、下载目录、User-Agent等高级配置。
    支持上下文管理器（with语法），自动资源清理。
    """
    def __init__(self, url=None, headless=False, proxy=None, user_agent=None, download_dir=None, chrome_path=None, chromedriver_path=None, maximize_window=True):
        """
        初始化GetDriver
        :param url: 允许的安全站点（用于insecure origin as secure）
        :param headless: 是否无头模式
        :param proxy: 代理（支持http、https、socks5，格式如socks5://127.0.0.1:1080）
        :param user_agent: 自定义User-Agent
        :param download_dir: 下载目录
        :param chrome_path: Chrome浏览器路径
        :param chromedriver_path: Chromedriver路径
        """
        self.url = url
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent
        self.download_dir = os.path.expanduser(download_dir) if download_dir else os.path.expanduser('~/Downloads')
        self.chrome_path = chrome_path
        self.chromedriver_path = chromedriver_path
        self.temp_dirs = []  # 存储临时目录路径，用于清理
        self.driver = None
        if not self.user_agent:
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            ]
            import random
            self.user_agent = user_agents[random.randint(0, len(user_agents) - 1)]
        self.maximize_window = maximize_window

    def __enter__(self):
        """
        支持with语法自动获取driver
        :return: selenium.webdriver.Chrome实例
        """
        self.driver = self.getdriver()
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支持with语法自动清理资源
        """
        self.quit()

    def close(self):
        """
        关闭浏览器窗口并清理临时目录
        """
        if self.driver:
            try:
                self.driver.close()
            except:
                pass
        self._cleanup_temp_dirs()

    def quit(self):
        """
        彻底退出浏览器并清理临时目录
        """
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self._cleanup_temp_dirs()

    def _cleanup_temp_dirs(self):
        """
        清理所有创建的临时目录
        """
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                pass
        self.temp_dirs = []

    def check_proxy(self):
        """
        校验代理格式和连通性，支持http/https/socks5
        :return: True/False
        """
        if not self.proxy:
            return True
        # 支持协议前缀
        proxy_pattern = r'^(socks5|http|https)://(\d{1,3}(\.\d{1,3}){3}):(\d+)$'
        if not re.match(proxy_pattern, self.proxy):
            return False
        proto, ip, _, _, port = re.match(proxy_pattern, self.proxy).groups()
        try:
            sock = socket.create_connection((ip, int(port)), timeout=5)
            sock.close()
            return True
        except:
            return False

    def getdriver(self):
        """
        创建并返回Chrome WebDriver实例，自动注入反检测JS，异常时抛出GetDriverException
        :return: selenium.webdriver.Chrome实例
        :raises: GetDriverException
        """
        if not self.check_proxy():
            raise GetDriverException(f"代理不可用或格式错误: {self.proxy}")
        option = webdriver.ChromeOptions()  # 浏览器启动选项
        if self.headless:
            option.add_argument("--headless")  # 设置无界面模式
        option.add_argument("--window-size=1920,1080")
        option.add_argument("--disable-gpu")
        option.add_argument("--no-sandbox")
        option.add_argument("--disable-dev-shm-usage")
        # 添加唯一的用户数据目录，避免Chrome实例冲突
        temp_dir = tempfile.mkdtemp(prefix=f'chrome_automation_{uuid.uuid4().hex[:8]}_')
        option.add_argument(f'--user-data-dir={temp_dir}')
        option.add_argument('--no-first-run')
        option.add_argument('--no-default-browser-check')
        option.add_argument('--disable-background-timer-throttling')
        option.add_argument('--disable-backgrounding-occluded-windows')
        option.add_argument('--disable-renderer-backgrounding')
        option.add_argument('--disable-features=TranslateUI')
        option.add_argument('--disable-ipc-flooding-protection')
        # 关键安全浏览禁用参数
        option.add_argument('--allow-insecure-localhost')
        option.add_argument('--allow-running-insecure-content')
        option.add_argument('--disable-features=BlockInsecurePrivateNetworkRequests,SafeBrowsing,DownloadBubble,SafeBrowsingEnhancedProtection,DownloadWarning')
        option.add_argument('--safebrowsing-disable-download-protection')
        option.add_argument('--disable-client-side-phishing-detection')
        option.add_argument('--disable-popup-blocking')
        option.add_argument('--ignore-certificate-errors')
        if self.url:
            option.add_argument(f"--unsafely-treat-insecure-origin-as-secure={self.url}")
        # User-Agent
        option.add_argument(f'--user-agent={self.user_agent}')
        # 自动化相关设置
        option.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        option.add_experimental_option("useAutomationExtension", False)
        # 代理设置
        if self.proxy:
            option.add_argument(f'--proxy-server={self.proxy}')
        # 下载配置
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "download_restrictions": 0,
        }
        # 平台与路径自动检测
        sys_platform = platform.system().lower()
        chrome_path = self.chrome_path
        chromedriver_path = self.chromedriver_path
        try:
            if sys_platform == 'windows':
                if not chrome_path:
                    chrome_path = os.path.join(f'C:\\Users\\{getpass.getuser()}', 'chrome\\chrome_win64\\chrome.exe')
                if not chromedriver_path:
                    chromedriver_path = os.path.join(f'C:\\Users\\{getpass.getuser()}', 'chrome\\chromedriver.exe')
                option.binary_location = chrome_path
                service = Service(chromedriver_path)
            elif sys_platform == 'linux':
                if not chrome_path:
                    chrome_path = '/usr/bin/chrome'
                    """
                    # sudo mv /usr/bin/google-chrome /usr/bin/google-chrome.bak  # 备份原有
                    # sudo ln -s /usr/bin/chrome /usr/bin/google-chrome # 创建软链接
                    """
                if not chromedriver_path:
                    chromedriver_path = '/usr/local/bin/chromedriver'
                option.binary_location = chrome_path
                service = Service(chromedriver_path)
            elif sys_platform == 'darwin':
                if not chrome_path:
                    # 优先使用用户指定的默认路径
                    chrome_path_candidates = [
                        '/usr/local/chrome/Google Chrome for Testing.app/Contents/MacOS/Google Chrome',
                        '/usr/local/chrome/Google Chrome for Testing.app',
                        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                        '/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome',
                    ]
                    chrome_path = next((p for p in chrome_path_candidates if os.path.exists(p)), None)
                if not chromedriver_path:
                    chromedriver_path_candidates = [
                        '/usr/local/chrome/chromedriver',
                        '/usr/local/bin/chromedriver',
                        '/opt/homebrew/bin/chromedriver',
                    ]
                    chromedriver_path = next((p for p in chromedriver_path_candidates if os.path.exists(p)), None)
                if not chrome_path or not chromedriver_path:
                    raise GetDriverException("未找到Chrome或Chromedriver，请手动指定chrome_path和chromedriver_path")
                # option.binary_location = chrome_path  # macOS 设置此参数报错
                service = Service(chromedriver_path)
            else:
                raise GetDriverException(f"不支持的平台: {sys_platform}")
        except Exception as e:
            raise GetDriverException(f"浏览器路径配置异常: {e}")
        option.add_experimental_option("prefs", prefs)
        try:
            driver = webdriver.Chrome(service=service, options=option)
            if self.maximize_window:
                driver.maximize_window()
            # --- 防反爬：注入多段JS隐藏Selenium特征 ---
            js_hide_features = [
                "Object.defineProperty(navigator, 'webdriver', {get: () => false});",
                "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});",
                "Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});",
                "window.chrome = {runtime: {}};",
                "delete window.navigator.__proto__.webdriver;",
                r"for (let key in window) {if (key.match(/^[\$\_]{3,}/)) {try {delete window[key];} catch(e){}}}"
            ]
            for js in js_hide_features:
                pass
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})
            self.temp_dirs.append(temp_dir)
            self.driver = driver
            return driver
        except Exception as e:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                pass
            raise GetDriverException(f"启动ChromeDriver失败: {e}")


if __name__ == '__main__':
    with GetDriver(
        headless=True,
        proxy=None,  # 代理（'socks5://127.0.0.1:1080'）
        user_agent=None,
        download_dir=None, 
        chrome_path=None, 
        chromedriver_path=None,
    ) as driver:
        driver.get('https://www.baidu.com')
        print(driver.title)
