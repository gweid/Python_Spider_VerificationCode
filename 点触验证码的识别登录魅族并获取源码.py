"""
验证有概率会失败，视超级鹰识别的准确度而定
"""
import time
from PIL import Image
from io import BytesIO
from chaojiying_Python.chaojiying import Chaojiying
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHAOJIYING_USERNAME = 'guanwei'
CHAOJIYING_PASSWORD = 'a6387578'
CHAOJIYING_SOFT_ID = 896768


class MeiZuClick():

    def __init__(self):
        """
        初始化数据
        """
        self.url = 'https://login.flyme.cn/sso?appuri=&useruri=http%3A%2F%2Fstore.meizu.com'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = '13570773719'
        self.password = 'a6387578'
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)

    def open_page(self):
        """
        打开网页输入用户名和密码
        :return:None
        """
        self.browser.get(self.url)
        self.browser.maximize_window()
        username = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#account')))
        password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#password')))
        username.send_keys(self.username)
        time.sleep(1)
        password.send_keys(self.password)

    def get_button(self):
        """
        获取验证按钮
        :return: 按钮
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip_content')))
        return button

    def get_image_element(self):
        """
        获取验证码对象
        :return:
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_item_img')))
        return img

    def get_position(self):
        """
        获取验证码图片位置
        :return: 验证码位置元组
        """
        img = self.get_image_element()
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

    def get_image(self, name='captcha.png'):
        """
        将验证码的图片从网页截图里裁剪出来
        :param name: 保存图片名
        :return: 验证码图片
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        # top和bottom数据有偏差，需要自行通过实验进行加减
        captcha = screenshot.crop((left, top - 150, right, bottom - 80))
        captcha.save(name)
        return captcha

    def get_point(self, captcha_result):
        """
        解析识别结果
        :param captcha_result:识别结果
        :return: 转化后的结果
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def click_word(self, locations):
        """
        点击验证图片
        :param locations:点击位置
        :return: None
        """
        for location in locations:
            print(location)
            # location[1]的值要进行偏移一下，偏移多少由实验得出
            ActionChains(self.browser).move_to_element_with_offset(self.get_image_element(), location[0],
                                                                   location[1] - 40).click().perform()
            print(location[1] - 40)
            time.sleep(1)

    def click_confirm(self):
        """
        点击确认按钮
        :return: None
        """
        click = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip')))
        click.click()

    def login(self):
        """
        登录
        :return:
        """
        login = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'fullBtnBlue')))
        login.click()

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
        # 打开网页输入账号密码
        self.open_page()
        # 点击验证按钮
        button = self.get_button()
        time.sleep(1)
        button.click()
        # 拖动滚动条向上拉动一点，再向下拉动，因为验证码图片不全在在显示的网页截图中
        time.sleep(1)
        self.browser.execute_script('window.scrollTo(0,0)')
        self.browser.execute_script('window.scrollTo(0,100)')
        # 获取验证码图片
        image = self.get_image()
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')
        # 识别验证码，9004为超级鹰的验证码类型
        result = self.chaojiying.post_pic(bytes_array.getvalue(), 9004)
        print(result)
        locations = self.get_point(result)
        self.click_word(locations)
        self.click_confirm()
        # 登录
        time.sleep(3)
        self.login()
        # 获取网页源码
        time.sleep(2)
        print(self.browser.page_source)


if __name__ == '__main__':
    main = MeiZuClick()
    main.main()
