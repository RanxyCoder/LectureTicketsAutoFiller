import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QRadioButton,
    QButtonGroup, QCheckBox, QMessageBox, QDateTimeEdit
)
from PySide6.QtCore import QDateTime, QObject, Signal, QTimer
from TencentDocs import web_launcher, web_grabber, InternalElementError
import datetime
import time


class Signals(QObject):
    update_status = Signal(str)
    set_button_text = Signal(str)
    set_button_enabled = Signal(bool)


class TencentDocsGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.signals = Signals()

        self.setWindowTitle("腾讯文档抢填器")
        self.resize(600, 500)

        layout = QVBoxLayout()

        # 第一行：网址
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("网址："))
        self.url_edit = QLineEdit("https://docs.qq.com/form/page/你的表单ID")
        row1.addWidget(self.url_edit)
        layout.addLayout(row1)

        # 第二行：浏览器 + 启动
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

        # 第三行：定时器
        row3 = QHBoxLayout()
        self.checkbox_timer = QCheckBox("定时器")
        self.checkbox_timer.setChecked(True)
        row3.addWidget(self.checkbox_timer)
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(60))  # 默认 +60秒
        row3.addWidget(self.datetime_edit)
        layout.addLayout(row3)

        # 第四行：表单内容 + 运行
        row4 = QHBoxLayout()
        self.text_inputs = QTextEdit()
        self.text_inputs.setPlaceholderText("每行一个字段，按顺序填写\n例如：\n张三\n2021001\n计算机学院")
        row4.addWidget(self.text_inputs)
        self.btn_run = QPushButton("运行")
        row4.addWidget(self.btn_run)
        layout.addLayout(row4)

        # 状态栏
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # 信号连接
        self.signals.update_status.connect(self.status_label.setText)
        self.signals.set_button_text.connect(self.btn_run.setText)
        self.signals.set_button_enabled.connect(self.btn_run.setEnabled)

        # 事件绑定
        self.btn_web_launch.clicked.connect(self.launch_browser)
        self.btn_run.clicked.connect(self.run_grabber)
        self.checkbox_timer.stateChanged.connect(self.toggle_datetime_edit)

        # 关键：延迟初始化，确保状态同步
        QTimer.singleShot(0, self._init_timer_state)

    def _init_timer_state(self):
        self.datetime_edit.setEnabled(self.checkbox_timer.isChecked())

    def toggle_datetime_edit(self, state):
        self.datetime_edit.setEnabled(self.checkbox_timer.isChecked())

    def launch_browser(self):
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "请输入腾讯文档网址")
            return

        browser = self.browser_group.checkedId()
        self.btn_web_launch.setDisabled(True)
        self.signals.update_status.emit("正在启动浏览器...")

        def _launch():
            try:
                self.driver = web_launcher(url, browser)
                self.signals.update_status.emit("浏览器已启动，请扫码登录腾讯文档")
                # 禁用启动相关控件
                self.url_edit.setDisabled(True)
                self.radio_chrome.setDisabled(True)
                self.radio_edge.setDisabled(True)
            except Exception as e:
                self.signals.update_status.emit(f"启动失败：{e}")
                QMessageBox.critical(self, "错误", str(e))
            finally:
                self.btn_web_launch.setDisabled(False)

        threading.Thread(target=_launch, daemon=True).start()

    def run_grabber(self):
        if not self.driver:
            QMessageBox.warning(self, "提示", "请先启动浏览器并登录")
            return

        input_text = self.text_inputs.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, "提示", "请输入表单内容")
            return

        input_list = [line.strip() for line in input_text.splitlines() if line.strip()]
        if not input_list:
            QMessageBox.warning(self, "提示", "表单内容不能为空")
            return

        target_time = None
        if self.checkbox_timer.isChecked():
            dt = self.datetime_edit.dateTime().toPython()
            if dt <= datetime.datetime.now():
                QMessageBox.warning(self, "提示", "定时时间不能早于当前时间")
                return
            target_time = dt

        # 禁用控件
        self._lock_ui(True)
        self.signals.update_status.emit("准备就绪，等待执行...")

        thread = threading.Thread(
            target=self._grab_thread,
            args=(input_list, target_time),
            daemon=True
        )
        thread.start()

    def _lock_ui(self, lock=True):
        self.checkbox_timer.setDisabled(lock)
        self.datetime_edit.setDisabled(lock)
        self.text_inputs.setDisabled(lock)
        self.btn_run.setDisabled(lock)
        self.btn_run.setText("计时中..." if lock else "运行")

    def _grab_thread(self, input_list, target_time):
        try:
            if target_time:
                wait_secs = (target_time - datetime.datetime.now()).total_seconds()
                if wait_secs > 0:
                    for remaining in range(int(wait_secs), 0, -1):
                        self.signals.update_status.emit(f"倒计时：{remaining} 秒")
                        time.sleep(1)
                    self.signals.update_status.emit("开始抢填！")

            web_grabber(self.driver, input_list)
            self.signals.update_status.emit("抢填成功！")
        except InternalElementError as e:
            self.signals.update_status.emit(f"表单错误：{e}")
        except Exception as e:
            self.signals.update_status.emit(f"执行失败：{e}")
        finally:
            self._lock_ui(False)

    def closeEvent(self, event):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TencentDocsGUI()
    window.show()
    sys.exit(app.exec())
