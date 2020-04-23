# _*_ coding: utf-8 _*_
__author__ = 'fanafany'
__date__ = '2020-04-23 14:36 '
import time
import random
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

class Bili_Spider():
    login_url = 'https://passport.bilibili.com/login'


    def __init__(self):
        self.user_name = '18652358716'
        self.pass_word = '520520'
        chrome_options = Options()
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
                                   options=chrome_options)

    def compare_pixel(self, image1, image2, i, j):
        # 判断两个像素是否相同
        pixel1 = image1.load()[i, j]
        pixel2 = image2.load()[i, j]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        return False

    def crop_image(self,image_file_name):
        #截取验证码图片
        time.sleep(1)
        img = self.browser.find_element_by_css_selector(".geetest_canvas_img.geetest_absolute")
        location = img.location
        print("图片的位置",location)

        #得到它的长和宽
        size = img.size

        top, buttom, left, right = location["y"],location["y"]+size["height"],location["x"],location["x"]+size["width"]
        print("验证码截图坐标", left, top, buttom, right)
        screen_shot = self.browser.get_screenshot_as_png()
        screen_shot = Image.open(BytesIO(screen_shot))
        captcha = screen_shot.crop((int(left), int(top), int(right), int(buttom)))
        captcha.save(image_file_name)
        return captcha

    def check_login(self):
        try:
            self.browser.find_element_by_xpath("//span[contains(text(),'创作中心')]")
            return True
        except Exception as e:
            return False
    def login(self):

        try:
            self.browser.maximize_window()
        except Exception as e:
            pass
        while not self.check_login():
            self.browser.get(self.login_url)
            username_ele = self.browser.find_element_by_css_selector("#login-username")
            password_ele = self.browser.find_element_by_css_selector("#login-passwd")
            username_ele.send_keys(self.user_name)
            password_ele.send_keys(self.pass_word)

            #点击登录调出滑动验证码
            login_btn = self.browser.find_element_by_css_selector(".btn.btn-login")
            login_btn.click()

            #延迟时间，等验证码出现
            time.sleep(1)

            #执行js改变style为空,显示没有缺口的图
            self.browser.execute_script('document.querySelectorAll("canvas")[3].style=""')
            #截取验证码
            image1 = self.crop_image("captcha1.png")

            #执行js改变style为空,显示有缺口的图
            self.browser.execute_script('document.querySelectorAll("canvas")[3].style="display: none; opacity: 1;"')
            # 截取验证码
            image2 = self.crop_image("captcha2.png")

            left = 60
            has_find = False
            for i in range(60, image1.size[0]):
                if has_find:
                    break
                for j in range(image1.size[1]):
                    if not self.compare_pixel(image1, image2, i, j):
                        left = i
                        has_find = True
                        break

            left -= 6
            print(left)

            #拖动图片
            #根据偏移量获取移动轨迹
            #一开始加速，然后减速，生长曲线，且加入点随机变动
            #移动轨迹
            track = []
            #当前位移
            current = 0
            #减速阈值
            mid = left * 4 / 5
            #间隔时间
            t = 0.2
            v = 0
            while current < left:
                if current < mid:
                    a = 2
                else:
                    a = -3
                v0 = v
                #当前速度
                v = v0 + a * t
                #移动距离
                move = v0 * t + 1 / 2 * a * t * t
                #当前位移
                current += move
                #加入轨迹
                track.append(round(move))

            slider = self.browser.find_element_by_css_selector(".geetest_slider_button")
            ActionChains(self.browser).click_and_hold(slider).perform()
            for x in track:
                ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            time.sleep(0.5)
            ActionChains(self.browser).release().perform()
            time.sleep(5)

        Cookies = self.browser.get_cookies()
        print(Cookies)
        cookie_dict = {}
        for cookie in  Cookies:
            cookie_dict[cookie['name']] = cookie['value']
        self.browser.close()
        return cookie_dict



if __name__ == '__main__':
    bili = Bili_Spider()
    bili.login()


