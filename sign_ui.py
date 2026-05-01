# code:utf-8
import json
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QGridLayout,
                             QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt

SAVE_FILE = "sign_data.json"

def load_sign_data():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"last_sign_date": "", "week_sign": [False] * 7}

def save_sign_data(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

class SignDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("每日签到")
        self.setFixedSize(400, 320)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.sign_data = load_sign_data()
        self.today = datetime.now()
        self.today_weekday = self.today.weekday()
        self.init_ui()

    def init_ui(self):
        self.widget = QWidget(self)
        self.widget.setStyleSheet("""
    QWidget {
        background-color: rgba(30, 30, 50, 240);
        border-radius: 6px;
        border: 2px solid #ff9292;
    }
    QLabel {
        color: #ff9292;
        font-size: 18px;
        font-weight: bold;
    }
    QPushButton {
        padding: 5px 5px;
        color:#ffffff;
        border: 2px solid #ff9292;
        border-radius: 2px;
        background-color: #ff9292;
        font-size:14px;
    }
    QPushButton:hover {
        background-color: #ff7272;
    }
    QPushButton:checked {
        background-color: #ff7272;
        color:white;
    }
        """)
        self.widget.setFixedSize(400, 320)

        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("📅 连续7日签到")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)
        self.buttons = []
        week_days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        for i in range(7):
            btn = QPushButton(week_days[i])
            btn.setFixedSize(80, 80)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.sign_click(idx))

            if self.sign_data["week_sign"][i]:
                btn.setChecked(True)
            if i == self.today_weekday:
                btn.setStyleSheet(btn.styleSheet() + "border:2px solid #ff9292;")

            grid.addWidget(btn, i // 4, i % 4)
            self.buttons.append(btn)

        layout.addLayout(grid)

        close_btn = QPushButton("关闭")
        close_btn.setFixedHeight(35)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
    QPushButton {
        padding: 5px 5px;
        color:#ffffff;
        border: 2px solid #ff9292;
        border-radius: 2px;
        background-color: #ff9292;
        font-size:14px;
    }
    QPushButton:hover {
        background-color: #ff7272;
    }
        """)
        layout.addWidget(close_btn)

    def sign_click(self, idx):
        if idx != self.today_weekday:
            QMessageBox.warning(self, "提示", "只能签到今天哦!")
            return
        if self.sign_data["week_sign"][idx]:
            QMessageBox.information(self, "提示", "你今天已经签到过啦!")
            return

        self.sign_data["week_sign"][idx] = True
        self.sign_data["last_sign_date"] = self.today.strftime("%Y-%m-%d")
        save_sign_data(self.sign_data)

        self.buttons[idx].setChecked(True)
        self.buttons[idx].setStyleSheet("""
            QPushButton {background-color:#4CAF50;color:white;border-radius:8px;border:none;}
        """)
        QMessageBox.information(self, "签到成功", "🎉 恭喜你，签到成功！")