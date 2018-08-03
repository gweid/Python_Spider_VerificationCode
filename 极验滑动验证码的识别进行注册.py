"""
验证有概率会失败
"""
import time
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BORDER = 6


class CrackGeetest():

    def __init__(self):
        """
        初始化数据
        """
        self.url = 'https://auth.geetest.com/register/'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.email = '1104915882@qq.com'

    def open_page(self):
        """
        打开注册界面并输入注册邮箱
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ivu-input')))
        time.sleep(0.5)
        email.send_keys(self.email)

    def get_button(self):
        """
        获取验证按钮
        """
        button = self.wait.until(EC.element_to_be_clickable
                                 ((By.CSS_SELECTOR, '#captchaId2 > div > div.geetest_btn > div.geetest_radar_btn > '
                                                    'div.geetest_radar_tip > span.geetest_radar_tip_content')))
        return button

    def get_position(self):
        """
        获取验证码位置
        """
        # ***这个class_name一定要是带缺口的验证码的class_name
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_slice')))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_slider(self):
        """
        获取滑块
        """
        slider = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def get_image(self, name='captcha.png'):
        """
        获取验证码图片（将验证码图片从网页截图中裁剪出来）
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两图片像素
        :param image1:图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[2]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1:不带缺口的图片
        :param image2: 带缺口的图片
        :return:
        """
        left = 60
        for i in range(left, image1.size[0]):  # 滑块的位置会出现在左边，所以直接从滑块右侧即60出开始识别缺口
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        track = []
        current = 0  # 当前位移
        mid = distance * 4 / 5  # 减速阀值
        t = 0.2  # 计算间隔
        v = 0  # 初速度
        while current < distance:
            if current < mid:
                a = 2  # 加速度为正
            else:
                a = -3  # 加速度为负
            # 初速度v0
            v0 = v
            # 当前速度 v = v0 + at
            v = v0 + a * t
            # 移动距离 x = v0t + 1/2at^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, tracks):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param tracks: 轨迹
        :return:
        """
        # *****必须写成以下模式，不要把它分开写，不然会验证失败*****
        ActionChains(self.browser).click_and_hold(slider).perform()
        for i in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=i, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def __del__(self):
        """
        关闭浏览器
        :return: None
        """
        self.browser.close()

    def main(self):
        """
        执行
        :return:
        """
        # 打开网页输入邮箱
        self.open_page()
        # 点击按钮进行验证
        button = self.get_button()
        button.click()
        # 获取不带缺口的验证码图片
        image1 = self.get_image('captcha1.png')
        # 点击使带缺口的验证码出现
        slider = self.get_slider()
        slider.click()
        # 获取带缺口的验证码图片
        image2 = self.get_image('captcha2.png')
        # 获取缺口位置
        gap = self.get_gap(image1, image2)
        print('缺口位置', gap)
        # 减去缺口位移
        gap -= BORDER
        # 获取移动轨迹
        tracks = self.get_track(gap)
        # 移动滑块
        self.move_to_gap(slider, tracks)

        success = self.wait.until(EC.text_to_be_present_in_element((
            By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
        print(success)

        # 如果验证失败重试
        if not success:
            self.main()


if __name__ == '__main__':
    main = CrackGeetest()
    main.main()
