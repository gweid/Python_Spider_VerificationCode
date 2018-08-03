"""
验证有概率会失败，有时拉动滑块过快等原因都会造成失败
"""
import time
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CrackGeetest():

    def __init__(self):
        """
        初始化参数
        """
        self.url = 'https://auth.geetest.com/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.email = 'guanwei006@gmail.com'
        self.password = 'a6387578'

    def open_page(self):
        """
        打开网页并输入邮箱和密码
        :return:
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, '#base > div.content-outter > div > div > div:nth-child(3) > div > form > '
                             'div:nth-child(1) > div > '
                             'div.ivu-input-wrapper.ivu-input-type.ivu-input-group.ivu-input-group-with-prepend >'
                             ' input')))
        password = self.wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, '#base > div.content-outter > div > div > div:nth-child(3) > div > form > '
                             'div:nth-child(2) > div > '
                             'div.ivu-input-wrapper.ivu-input-type.ivu-input-group.ivu-input-group-with-prepend >'
                             ' input')))
        email.send_keys(self.email)
        time.sleep(0.5)
        password.send_keys(self.password)

    def get_button(self):
        """
        获取点击验证按钮
        :return:按钮
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip_content')))
        return button

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置参数
        """
        # ***这个class_name 一定要是带缺口验证码的，不能是不带缺口的，不然会出错***
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_slice')))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取整个网页截图
        :return:
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_slider(self):
        """
        获取滑块
        :return:滑块
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def get_image(self, name='captcha.png'):
        """
        获取验证码图片（将验证码的图片从整个网页截图中裁剪出来）
        :return:
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两验证码图片像素是否相同
        :param image1:图片1
        :param image2: 图片12
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1:不带缺口图片
        :param image2: 带缺口图片
        :return:
        """
        left = 60  # 滑块的右边缘是左边60位置
        for i in range(left, image1.size[0]):
            for j in range(image2.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):
        """
        根据偏移量获取运动轨迹
        :param distance: 偏移量
        :return: 运动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 初速度
        v = 0
        # 开始减速的位置
        mid1 = distance * 7 / 10
        # 计算时间间隔
        t = 0.2
        while current < distance:
            # 确定不同位置加速度,加速度尽可能小点，避免出现太快而不成功
            if current < mid1:
                a = 0.5
            else:
                a = -1
            # 初速度
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹，必须要round
            track.append(round(move))
        return track

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口
        :param slider:滑块
        :param track: 移动轨迹
        :return:
        """
        # 按住滑块
        ActionChains(self.browser).click_and_hold(slider).perform()
        # 拖动滑块
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.8)
        # 松开滑块
        ActionChains(self.browser).release().perform()

    def login(self):
        """
        登录
        :return:
        """
        submit = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#base > div.content-outter > div > div > '
                                                         'div:nth-child(3) > div > form >'
                                                         ' div:nth-child(5) > div > button > span')))
        submit.click()
        time.sleep(5)
        print('登录成功')

    def get_page(self):
        """
        获取网页源码
        :return:
        """
        print(self.browser.page_source)

    def main(self):
        """
        执行
        :return:
        """
        # 打开网站，输入邮箱和密码
        self.open_page()
        # 点击验证按钮
        button = self.get_button()
        time.sleep(0.5)
        button.click()
        # 获取不带缺口的验证码图片
        image1 = self.get_image('captcha1.png')
        # 点击按钮使带缺口的验证码出现
        slider = self.get_slider()
        slider.click()
        # 获取带缺口的验证码图片
        image2 = self.get_image('captcha2.png')
        # 获取缺口位置
        gap = self.get_gap(image1, image2)
        print('缺口位置', gap)
        # 为了更准确识别，将滑块稍微偏离一下缺口
        gap -= 2
        # 获取移动轨迹
        track = self.get_track(gap)
        print('滑动轨迹', track)
        # 移动滑块
        self.move_to_gap(slider, track)
        # 判断是否验证成功，不成功重新拖动滑块.成功则点击登录
        try:
            self.wait.until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
        except TimeoutException:
            self.main()
        finally:
            self.login()
        # 获取网页源码
        time.sleep(2)
        self.get_page()
        # 关闭浏览器
        time.sleep(1)
        self.browser.close()


if __name__ == '__main__':
    main = CrackGeetest()
    main.main()
