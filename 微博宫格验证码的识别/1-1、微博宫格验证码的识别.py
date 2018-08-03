import time
from PIL import Image
from os import listdir
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WeiboSlideCode():
    """
    微博宫格验证码登陆
    """

    def __init__(self):
        """
        初始化参数
        """
        self.url = 'https://passport.weibo.cn/signin/login'
        self.username = '13570773719'
        self.password = 'a6387578'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)

    def open(self):
        """
        打开微博输入用户密码并点击登录
        :return:None
        """
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        time.sleep(0.8)
        password.send_keys(self.password)
        time.sleep(0.8)
        submit.click()

    def get_position(self):
        """
        获取验证码图片位置信息
        :return: 位置元祖
        """
        try:
            img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'patt-shadow')))
        except TimeoutException:
            print('验证码没有出现')
            self.open()
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return:
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_image(self, name='captcha.png'):
        """
        将验证码图片从网页截图里面裁剪出来
        :return: 验证码图片
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断验证码图片与模板的图片每一个位置像素是否相同
        :param image1: 验证码图片
        :param image2: 模板图片
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两张图片像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        # 设定阀值
        threshold = 20
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def same_image(self, image, template):
        """
        识别两张图片是否是同一张图片
        :param image:验证码图片
        :param template: 模板图片
        :return: 是否同一张图片
        """
        threshold = 0.99
        count = 0
        for x in range(image.width):
            for y in range(image.height):
                if self.is_pixel_equal(image, template, x, y):
                    count += 1
        result = float(count) / (image.width * image.height)
        if result > threshold:
            print('匹配成功')
            return True
        return False

    def detect_image(self, image):
        """
        进行图片匹配并获取拖动顺序
        :param image: 验证码图片
        :return: 拖动顺序
        """
        for template_name in listdir('templates/'):
            # 打开文件夹下的图片
            template = Image.open('templates/' + template_name)
            print('正在匹配')
            if self.same_image(image, template):
                numbers = [int(number) for number in list(template_name.split('.')[0])]
                print('拖动顺序', numbers)
                return numbers

    def move(self, numbers):
        """
        根据顺序拖动验证码
        :param numbers: 验证码顺序
        :return: Nome
        """
        # 找到验证码图片中的四个小圆圈
        circles = self.browser.find_elements_by_css_selector('.patt-circ')
        dx = dy = 0
        for index in range(4):
            circle = circles[numbers[index] - 1]
            # 如果是第一次循环
            if index == 0:
                # 将鼠标移到第一个圆圈的中点并按住鼠标
                ActionChains(self.browser).move_to_element_with_offset(circle, circle.size['width'] / 2, circle.size[
                    'height'] / 2).click_and_hold().perform()
            else:
                # 小幅度移动次数
                times = 30
                # 拖动
                for i in range(times):
                    ActionChains(self.browser).move_by_offset(dx / times, dy / times).perform()
                    time.sleep(1 / times)
            # 如果是最后一次循环
            if index == 3:
                ActionChains(self.browser).release().perform()
            else:
                # 计算下一次横坐标移动距离
                dx = circles[numbers[index + 1] - 1].location['x'] - circle.location['x']
                # 计算下一次纵坐标移动距离
                dy = circles[numbers[index + 1] - 1].location['y'] - circle.location['y']

    def main(self):
        """
        执行
        :return:
        """
        # 打开网页输入用户密码并点击登录
        self.open()
        # 获取验证码图片
        image = self.get_image()
        # 获取拖动顺序
        numbers = self.detect_image(image)
        # 拖动进行验证
        self.move(numbers)


if __name__ == '__main__':
    main = WeiboSlideCode()
    main.main()
