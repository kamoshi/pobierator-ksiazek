import re
import requests
import os
from urllib.parse import urlparse

from PyQt5.QtWidgets import QFileDialog
from selenium import webdriver
from PyQt5 import QtWidgets, QtCore
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from window import Ui_MainWindow


url_checker = re.compile(r"https://epublikacje.mac.pl/*")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, driver: WebDriver):
        super().__init__()
        self._driver = driver
        self.setupUi(self)

    def setupUi(self, main_window):
        super().setupUi(main_window)

    @QtCore.pyqtSlot()
    def on_buttonSave_clicked(self):
        url, start, end = self.inputPageURL.toPlainText(), self.inputPageStart.value(), self.inputPageEnd.value() + 1
        if not (url_checker.match(url) and start < end):
            return
        if '#' in url:
            url = url[:url.find('#')]

        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not directory:
            return

        to_download = list(range(start, end))
        img_urls = []
        while len(to_download):
            current_page = to_download.pop()
            self._driver.get(url + f"#p={current_page}")
            self._driver.refresh()
            img_urls.append(WebDriverWait(self._driver, 3)
                            .until(ec.visibility_of_element_located((
                                By.XPATH,
                                f'//div[@id="pageMask{current_page}"]//div[@class="side-content"]/div[2]')))
                            .value_of_css_property("background-image").split('"')[1])

        for img in img_urls:
            res = requests.get(img, stream=True)
            if res.ok:
                filename = os.path.basename(urlparse(img).path)
                with open(os.path.join(directory, filename), 'wb') as f:
                    for block in res.iter_content(1024):
                        if not block:
                            break
                        f.write(block)

    @QtCore.pyqtSlot()
    def on_buttonCancel_clicked(self):
        self.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    test = webdriver.Firefox(executable_path="./geckodriver")
    w = MainWindow(test)
    w.show()
    sys.exit(app.exec_())
