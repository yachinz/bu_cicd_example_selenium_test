#! /usr/bin/python3
from argparse import ArgumentParser
from pyvirtualdisplay import Display
from random import random, randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from threading import Thread, Lock
from yaml import safe_load


with open('resources/config.yaml') as yaml_in:
    config = safe_load(yaml_in)


class BrowserTest:
    def __init__(self):
        self.browser = webdriver.Firefox(firefox_profile=webdriver.FirefoxProfile())

    def open_home(self):
        self.browser.set_page_load_timeout(30)
        self.browser.get(config['selenium_test_url'])
        sleep(randint(5, 10) + random())
        assert config['company'] in self.browser.title

    def _get_p_tags(self):
        for tag in self.browser.find_elements_by_tag_name('p'):
            yield tag.text

    def check_heading(self):
        heading = 'Welcome to %s home.' % config['company']
        for ptag in self._get_p_tags():
            if ptag == heading:
                break
        else:
            raise Exception('Heading not found in home page HTML')

    def click_api(self):
        self.browser.find_element_by_class_name('btn-primary').send_keys(Keys.RETURN)
        sleep(randint(5, 10) + random())
        assert self.browser.current_url == config['selenium_test_url'] + 'api/v1/'
        assert self.browser.title == 'API V1'

    def close_browser(self):
        self.browser.quit()


class ArgParser:
    def __init__(self):
        description = 'Usage: python3 selenium_test.py  '
        parser = ArgumentParser(description=description)
        parser.add_argument('-x', '--headless', required=False, action='store_true',
                            help='add -x option to run in terminal only (no GUI)')
        self.args = parser.parse_args()

    def get_args(self):
        return self.args


class MultiBrowserTest(ArgParser):
    def __init__(self, n):
        super().__init__()

        self.browsers = [None for _ in range(n)]
        self.lock = Lock()

    def _browser_thread(self, index):
        new_browser = BrowserTest()
        with self.lock:
            self.browsers[index] = new_browser
        new_browser.open_home()
        new_browser.check_heading()
        new_browser.click_api()

    def open_browsers(self):
        try:
            threads = []
            for index in range(len(self.browsers)):
                current_thread = Thread(target=self._browser_thread, args=[index])
                current_thread.start()
                threads.append(current_thread)
            _ = [fin_thread.join() for fin_thread in threads]
        finally:
            sleep(randint(60, 70) + random())
            _ = [obj.close_browser() for obj in self.browsers if obj is not None]


if __name__ == '__main__':
    sel_test = MultiBrowserTest(10)
    if not sel_test.get_args().headless:
        sel_test.open_browsers()
    else:
        with Display():
            sel_test.open_browsers()
