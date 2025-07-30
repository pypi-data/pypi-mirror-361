# 小红书的自动发稿
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from tools.log_utils import logger
import time
import json
import os


class XiaohongshuPoster:
    # 添加静态变量来保存实例
    _instance = None
    
    def __init__(self,path=os.path.dirname(os.path.abspath(__file__))):
        # 如果已经有实例，直接返回
        if XiaohongshuPoster._instance is not None:
            self.driver = XiaohongshuPoster._instance.driver
            self.wait = XiaohongshuPoster._instance.wait
            self.token_file = XiaohongshuPoster._instance.token_file
            self.cookies_file = XiaohongshuPoster._instance.cookies_file
            self.token = XiaohongshuPoster._instance.token
            return
            
        #self.driver = webdriver.ChromiumEdge()#.Chrome()
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        # 获取当前执行文件所在目录
        current_dir = path
        self.token_file = os.path.join(current_dir, "xiaohongshu_token.json")
        self.cookies_file = os.path.join(current_dir, "xiaohongshu_cookies.json")
        self.token = self._load_token()
        self._load_cookies()
        
        # 保存实例
        XiaohongshuPoster._instance = self

    def _load_token(self):
        """从文件加载token"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
                    # 检查token是否过期
                    if token_data.get('expire_time', 0) > time.time():
                        return token_data.get('token')
            except:
                pass
        return None

    def _save_token(self, token):
        """保存token到文件"""
        token_data = {
            'token': token,
            # token有效期设为30天
            'expire_time': time.time() + 30 * 24 * 3600
        }
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f)

    def _load_cookies(self):
        """从文件加载cookies"""
        if os.path.exists(self.cookies_file):
            logger.info(f"加载cookies文件: {self.cookies_file}")
            try:
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                    self.driver.get("https://creator.xiaohongshu.com")
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
            except:
                pass

    def _save_cookies(self):
        """保存cookies到文件"""
        cookies = self.driver.get_cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)
            
    def login_to_publish(self,title, content, images=None,slow_mode=False):
        #self.driver.get("https://creator.xiaohongshu.com/publish/publish?from=menu")
        self._load_cookies()
        self.driver.refresh()
        self.driver.get("https://creator.xiaohongshu.com/publish/publish?from=menu")
        time.sleep(3)
        if self.driver.current_url != "https://creator.xiaohongshu.com/publish/publish?from=menu":
            return False, "登录失败"
        #time.sleep(1)
        # 如果是发布视频，则不操作这一步
        # 切换到上传图文
        
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".creator-tab")
        if len(tabs) > 1:
            tabs[2].click()
        time.sleep(1)
        # # 输入标题和内容

        # 上传图片
        if images:
            upload_input = self.driver.find_element(By.CSS_SELECTOR, ".upload-input")
            # 将所有图片路径用\n连接成一个字符串一次性上传
            upload_input.send_keys('\n'.join(images))
            time.sleep(1)
        time.sleep(1)
        title = title[:20]
        title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".d-text")))
        title_input.send_keys(title)

        # Start of Selection
        # Start of Selection
        logger.info(content)
        content_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor")))
        content_input.send_keys(content)
        # 发布
        if slow_mode:
            time.sleep(5)
        time.sleep(2)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, ".publishBtn")

        submit_btn.click()
        logger.info('发布成功')
        time.sleep(2)
        return True, "发布成功"

    def login_to_publish_video(self,title, content, videos=None,slow_mode=False):
        #self.driver.get("https://creator.xiaohongshu.com/publish/publish?from=menu")
        self._load_cookies()
        self.driver.refresh()
        self.driver.get("https://creator.xiaohongshu.com/publish/publish?from=menu")
        time.sleep(3)
        if self.driver.current_url != "https://creator.xiaohongshu.com/publish/publish?from=menu":
            return False, "登录失败"


        # # 输入标题和内容
        if videos:
            upload_input = self.driver.find_element(By.CSS_SELECTOR, ".upload-input")
            # 将所有图片路径用\n连接成一个字符串一次性上传
            upload_input.send_keys('\n'.join(videos))
            time.sleep(1)
        time.sleep(3)
        title = title[:20]
        title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".d-text")))
        title_input.send_keys(title)

        # Start of Selection
        logger.info(content)
        content_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor")))
        content_input.send_keys(content)
        # 发布
        if slow_mode:
            time.sleep(5)
        time.sleep(2)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, ".publishBtn")

        submit_btn.click()
        logger.info('发布成功')
        time.sleep(2)
        return True, "发布成功"
    
    def login(self, phone, country_code="+86"):
        """登录小红书"""
        # 如果token有效则直接返回
        if self.token:
            return True, "已有有效token，无需重新登录"

        # 尝试加载cookies进行登录
        self.driver.get("https://creator.xiaohongshu.com/login")
        self._load_cookies()
        self.driver.refresh()
        time.sleep(3)
        # 检查是否已经登录
        if self.driver.current_url != "https://creator.xiaohongshu.com/login":
            logger.info("使用cookies登录成功")
            self.token = self._load_token()
            self._save_cookies()
            time.sleep(2)
            return True, "使用cookies登录成功"
        else:
            # 清理无效的cookies
            self.driver.delete_all_cookies()
            logger.info("无效的cookies，已清理")

        # 如果cookies登录失败，则进行手动登录
        self.driver.get("https://creator.xiaohongshu.com/login")

        # 等待登录页面加载完成
        time.sleep(5)
        # 点击国家区号输入框
        skip = True
        if not skip:
            country_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请选择选项']")))
            country_input.click()
            time.sleep(30)

            # 等待区号列表出现并点击+886
            # 等待区号列表出现并点击+86

            try:
                self.driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div/div/div/div[2]/div[1]/div[1]/div/div/div[1]/input").click()
                time.sleep(2)
                self.driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div/div/div/div[2]/div[1]/div[1]/div/div/div[1]/input").send_keys(
                    country_code)
                time.sleep(2)
                self.driver.find_element(By.XPATH, "/html/body/div[6]/div/div").click()
                # china_option = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'css-cqcgee')]//div[contains(text(), '+86')]")))
                time.sleep(2)
            except Exception as e:
                logger.info("无法找到国家区号选项")
                logger.info(e)

        # 定位手机号输入框
        phone_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='手机号']")))
        phone_input.clear()
        phone_input.send_keys(phone)

        # 点击发送验证码按钮
        try:
            send_code_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".css-uyobdj")))
            send_code_btn.click()
        except:
            # 尝试其他可能的选择器
            try:
                send_code_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".css-1vfl29")))
                send_code_btn.click()
            except:
                try:
                    send_code_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'发送验证码')]")))
                    send_code_btn.click()
                except:
                    logger.info("无法找到发送验证码按钮")
                    return False, "无法找到发送验证码按钮"

        return True, "成功打开浏览器，发送验证码成功"

    def wait_for_verify_code(self,verification_code):
        """等待验证码输入并登录
        
        Args:
            verification_code: 验证码
            
        Returns:
            tuple: (成功状态, 消息)
        """
        try:
            # 输入验证码
            code_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='验证码']")))
            code_input.clear()
            code_input.send_keys(verification_code)

            # 点击登录按钮
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".beer-login-btn")))
            login_button.click()

            # 等待登录成功,获取token
            time.sleep(3)
            # 保存cookies
            self._save_cookies()
            return True, "验证码通过，登录成功"
        except Exception as e:
            logger.info(f"验证码输入失败: {str(e)}")
            return False, f"验证码输入失败: {str(e)}"

    def post_article(self, title, content, images=None):
        """发布文章
        Args:
            title: 文章标题
            content: 文章内容
            images: 图片路径列表
        """
        # 如果token失效则重新登录

        # 设置token
        # self.driver.execute_script(f'localStorage.setItem("token", "{self.token}")')
        #time.sleep(3)
        #logger.info("点击发布按钮")
        # 点击发布按钮
        publish_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.el-tooltip__trigger.el-tooltip__trigger")))
        publish_btn.click()

        # 如果是发布视频，则不操作这一步
        # 切换到上传图文
        time.sleep(3)
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".creator-tab")
        if len(tabs) > 1:
            tabs[1].click()
        time.sleep(2)
        # # 输入标题和内容
        # title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".title-input")))
        # content_input = self.driver.find_element(By.CSS_SELECTOR, ".content-input")

        # title_input.send_keys(title)
        # content_input.send_keys(content)

        # 上传图片
        if images:
            upload_input = self.driver.find_element(By.CSS_SELECTOR, ".upload-input")
            # 将所有图片路径用\n连接成一个字符串一次性上传
            upload_input.send_keys('\n'.join(images))
            time.sleep(1)
        time.sleep(2)
        title=title[:20]
        title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".d-text")))
        title_input.send_keys(title)

        # Start of Selection
        # Start of Selection
        logger.info(content)
        content_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor")))
        content_input.send_keys(content)
        # 发布
        time.sleep(2)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, ".publishBtn")

        submit_btn.click()
        logger.info('发布成功')
        time.sleep(2)

    def post_video_article(self, title, content, videos=None):
        """发布文章
        Args:
            title: 文章标题
            content: 文章内容
            videos: 视频路径列表
        """
        # 如果token失效则重新登录

        # 设置token
        # self.driver.execute_script(f'localStorage.setItem("token", "{self.token}")')
        time.sleep(3)
        #logger.info("点击发布按钮")
        # 点击发布按钮
        publish_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.el-tooltip__trigger.el-tooltip__trigger")))
        publish_btn.click()

        # 如果是发布视频，则不操作这一步
        # 切换到上传图文
        time.sleep(3)
        # # 输入标题和内容
        # title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".title-input")))
        # content_input = self.driver.find_element(By.CSS_SELECTOR, ".content-input")

        # title_input.send_keys(title)
        # content_input.send_keys(content)

        # 上传图片
        if videos:
            upload_input = self.driver.find_element(By.CSS_SELECTOR, ".upload-input")
            # 将所有图片路径用\n连接成一个字符串一次性上传
            upload_input.send_keys('\n'.join(videos))
            time.sleep(1)
        time.sleep(3)
        title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".d-text")))
        title_input.send_keys(title)

        # Start of Selection
        # Start of Selection
        logger.info(content)
        content_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor")))
        content_input.send_keys(content)
        # 发布
        time.sleep(6)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, ".publishBtn")

        submit_btn.click()
        logger.info('发布成功')
        time.sleep(3)


    def close(self):
        """关闭浏览器"""
        self.driver.quit()
        XiaohongshuPoster._instance = None


    @classmethod
    def reset_instance(cls):
        """重置实例，用于关闭浏览器后重新创建"""
        if cls._instance is not None:
            try:
                cls._instance.driver.quit()
            except:
                pass
        cls._instance = None


if __name__ == "__main__":
    # 测试XiaohongshuPoster类的功能
    import argparse
    
    parser = argparse.ArgumentParser(description='测试小红书发布功能')
    parser.add_argument('--mode', type=str, default='login', choices=['login', 'post_image', 'post_video'], 
                        help='测试模式: login-仅登录, post_image-发布图文, post_video-发布视频')
    parser.add_argument('--title', type=str, default='测试标题', help='发布内容的标题')
    parser.add_argument('--content', type=str, default='这是一条测试内容', help='发布的正文内容')
    parser.add_argument('--images', type=str, nargs='+', help='要上传的图片路径列表')
    parser.add_argument('--videos', type=str, nargs='+', help='要上传的视频路径列表')
    parser.add_argument('--phone', type=str, help='登录用的手机号')
    parser.add_argument('--country_code', type=str, default='+86', help='国家区号')
    parser.add_argument('--slow_mode', action='store_true', help='慢速模式，增加等待时间')
    parser.add_argument('--verification_code', type=str, help='验证码，用于登录后的验证')
    
    args = parser.parse_args()
    
    poster = None
    try:
        logger.info("初始化XiaohongshuPoster...")
        poster = XiaohongshuPoster()
        logger.info("初始化完成")
        
        if args.mode == 'login':
            if not args.phone:
                logger.info("登录模式需要提供手机号，请使用 --phone 参数")
                exit(1)
            logger.info(f"尝试登录，手机号: {args.phone}")
            success, message = poster.login(args.phone, args.country_code)
            logger.info(f"登录结果: {success}, {message}")
            
            # 如果提供了验证码，则进行验证
            if args.verification_code:
                success, message = poster.wait_for_verify_code(args.verification_code)
                logger.info(f"验证结果: {success}, {message}")
            
        elif args.mode == 'post_image':
            logger.info(f"尝试发布图文，标题: {args.title}")
            success, message = poster.login_to_publish(args.title, args.content, args.images, args.slow_mode)
            logger.info(f"图文发布结果: {success}, {message}")
            
        elif args.mode == 'post_video':
            logger.info(f"尝试发布视频，标题: {args.title}")
            success, message = poster.login_to_publish_video(args.title, args.content, args.videos, args.slow_mode)
            logger.info(f"视频发布结果: {success}, {message}")
            
        logger.info("测试完成")
    except Exception as e:
        import traceback
        logger.info(f"测试过程中发生错误: {e}")
        logger.info(traceback.format_exc())
    finally:
        if poster:
            logger.info("关闭浏览器...")
            try:
                poster.close()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.info(f"关闭浏览器时发生错误: {e}")

