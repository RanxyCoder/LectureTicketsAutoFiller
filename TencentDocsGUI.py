import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QRadioButton,
    QButtonGroup, QCheckBox, QMessageBox, QDateTimeEdit
)
from PySide6.QtCore import QDateTime
from TencentDocs import web_launcher, web_grabber
import datetime
import time


class TencentDocsGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.setWindowTitle("腾讯文档抢填器")

        layout = QVBoxLayout()

        # -------- 第一行：网址 --------
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("网址："))
        self.url_edit = QLineEdit()
        row1.addWidget(self.url_edit)
        layout.addLayout(row1)

        # -------- 第二行：浏览器选择 + 启动按钮 --------
        row2 = QHBoxLayout()
        self.radio_chrome = QRadioButton("Chrome")
        self.radio_chrome.setChecked(True)
        self.radio_edge = QRadioButton("Edge")
        self.browser_group = QButtonGroup()
        self.browser_group.addButton(self.radio_chrome, 0)
        self.browser_group.addButton(self.radio_edge, 1)
        row2.addWidget(self.radio_chrome)
        row2.addWidget(self.radio_edge)
        self.btn_web_launch = QPushButton("Web启动")
        row2.addWidget(self.btn_web_launch)
        layout.addLayout(row2)

        # -------- 第三行：定时器 --------
        row3 = QHBoxLayout()
        self.checkbox_timer = QCheckBox("定时器")
        self.checkbox_timer.setChecked(True)
        row3.addWidget(self.checkbox_timer)
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        row3.addWidget(self.datetime_edit)
        layout.addLayout(row3)

        # -------- 第四行：表单内容 + 运行按钮 --------
        row4 = QHBoxLayout()
        self.text_inputs = QTextEdit()
        row4.addWidget(self.text_inputs)
        self.btn_run = QPushButton("运行")
        row4.addWidget(self.btn_run)
        layout.addLayout(row4)

        # 状态显示
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # 绑定事件
        self.btn_web_launch.clicked.connect(self.launch_browser)
        self.btn_run.clicked.connect(self.run_grabber)
        self.checkbox_timer.stateChanged.connect(self.toggle_datetime_edit)

        # 初始化时间控件状态
        self.toggle_datetime_edit(self.checkbox_timer.checkState())

    # -------- 槽函数 --------
    def toggle_datetime_edit(self, state):
        """勾选定时器才启用时间控件"""
        self.datetime_edit.setEnabled(state == 2)  # 2 = Qt.Checked

    def launch_browser(self):
        url = self.url_edit.text().strip()
        browser = self.browser_group.checkedId()
        try:
            self.driver = web_launcher(url, browser)
            self.status_label.setText("✅ 浏览器已启动，请扫码登录")
            # 禁用第一、二行控件
            self.url_edit.setDisabled(True)
            self.radio_chrome.setDisabled(True)
            self.radio_edge.setDisabled(True)
            self.btn_web_launch.setDisabled(True)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def run_grabber(self):
        if not self.driver:
            QMessageBox.warning(self, "提示", "请先启动浏览器并登录")
            return

        # 获取表单内容
        input_list = [line.strip() for line in self.text_inputs.toPlainText().splitlines() if line.strip()]
        if not input_list:
            QMessageBox.warning(self, "提示", "请输入表单内容")
            return

        # 获取定时时间
        if self.checkbox_timer.isChecked():
            dt = self.datetime_edit.dateTime().toPython()
            target_time = dt
        else:
            target_time = None

        # 禁用输入控件
        self.datetime_edit.setDisabled(True)
        self.checkbox_timer.setDisabled(True)
        self.text_inputs.setDisabled(True)
        self.btn_run.setText("计时中...")
        self.btn_run.setDisabled(True)

        # 用线程执行
        thread = threading.Thread(target=self._grab_thread, args=(input_list, target_time), daemon=True)
        thread.start()

    def _grab_thread(self, input_list, target_time):
        # 等待定时
        if target_time:
            now = datetime.datetime.now()
            wait_seconds = (target_time - now).total_seconds()
            if wait_seconds > 0:
                self.status_label.setText(f"⏳ 等待开始... 还有 {wait_seconds:.1f} 秒")
                time.sleep(wait_seconds)

        try:
            print(input_list)
            web_grabber(self.driver, input_list)
            self.status_label.setText("✅ 抢填完成！")
            self.btn_run.setText("运行")
            self.btn_run.setDisabled(False)
        except Exception as e:
            self.status_label.setText(f"❌ 出错：{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TencentDocsGUI()
    window.show()
    sys.exit(app.exec())
