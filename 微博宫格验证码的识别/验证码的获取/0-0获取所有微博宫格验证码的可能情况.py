import time
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CrackWeiboSlide():
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
        打开网页输入账号密码并点击
        :return: None
        """
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        time.sleep(1)
        password.send_keys(self.password)
        time.sleep(1)
        submit.click()

    def get_position(self):
        """
        获取验证码图片位置
        :return: 验证码位置元祖
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
        :return: 截图
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_image(self, name='weiboi_image.png'):
        """
        将验证码图片从网页截图中裁剪出来并保存
        :param name:将图片保存为...
        :return: 验证码图片
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def main(self):
        """
        批量获取验证码
        :return:
        """
        count = 0
        while True:
            self.open()
            self.get_image(str(count) + '.png')
            time.sleep(3)
            count += 1


if __name__ == '__main__':
    main = CrackWeiboSlide()
    main.main()
