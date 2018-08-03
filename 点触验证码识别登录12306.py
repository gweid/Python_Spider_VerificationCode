"""
有概率会失败，视超级鹰的识别准确率而定
"""
import time
from PIL import Image
from io import BytesIO
from chaojiying import Chaojiying
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHAOJIYING_USERNAME = 'guanwei'
CHAOJIYING_PASSWORD = 'a6387578'
CHAOJIYING_SOLD_ID = 896768


class Train():
    """
    模拟登录12306
    """

    def __init__(self):
        """
        初始化数据
        """
        self.url = 'https://kyfw.12306.cn/otn/login/init'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = 'a6387578'
        self.password = '6387578'
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOLD_ID)

    def __del__(self):
        """
        关闭浏览器
        :return: None
        """
        time.sleep(10)
        self.browser.close()

    def open_page(self):
        """
        打开网页，并输入账号密码
        :return:None
        """
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#username')))
        password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#password')))
        username.send_keys(self.username)
        time.sleep(0.8)
        password.send_keys(self.password)

    def get_touclick_element(self):
        """
        获取图片对象
        :return: 图片对象
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'touclick-image')))
        return img

    def get_position(self):
        """
        获取验证码图片位置信息
        :return: 验证码位置信息元组
        """
        img = self.get_touclick_element()
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_image(self, name='image.png'):
        """
        将验证码图片从网页截图中裁剪出来
        :return:验证码图片
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def verification_code_recognition(self, image):
        """
        利用超级鹰识别验证码
        :return: 识别结果
        """
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')
        result = self.chaojiying.post_pic(bytes_array.getvalue(), 9004)
        return result

    def get_point(self, captcha_result):
        """
        解析识别结果
        :param captcha_result:验证码的识别结果
        :return: 解析后的结果（即正确的位置坐标）
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def click_word(self, locations):
        """
        点击验证图片
        :param locations: 验证码的坐标
        :return: Nome
        """
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_touclick_element(), location[0],
                                                                   location[1]).click().perform()
            time.sleep(1)

    def login(self):
        """
        登录12306
        :return:None
        """
        login = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn200s')))
        login.click()

    def main(self):
        """
        执行
        :return:None
        """
        # 打开网页，输入账号密码
        self.open_page()
        # 获取验证码图片
        image = self.get_image()
        # 识别验证码,其中9004是超级鹰的验证码类型
        result = self.verification_code_recognition(image)
        print(result)
        # 获取验证码坐标信息
        locations = self.get_point(result)
        # 点击验证码
        self.click_word(locations)
        # 点击登录
        time.sleep(1)
        self.login()


if __name__ == '__main__':
    main = Train()
    main.main()
