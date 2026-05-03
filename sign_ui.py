# code:utf-8
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QGridLayout,
                             QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
import database

class SignDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__()
        self.username = username
        self.today = datetime.now()
        self.today_date = self.today.strftime("%Y-%m-%d")
        self.today_weekday = self.today.weekday()

        self.setWindowTitle("每日签到")
        self.setFixedSize(400, 320)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.init_ui()
        self.move_to_center()
        self.refresh_sign_status()

        self.__dragWin = False
        self.__dragPos = None

    def move_to_center(self):
        win_w = self.width()
        win_h = self.height()
        screen_w = self.screen().availableSize().width()
        screen_h = self.screen().availableSize().height()
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.move(x, y)

    # 拖拽功能
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__dragWin = True
            self.__dragPos = event.globalPos() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):
        if self.__dragWin and event.buttons() == Qt.LeftButton and self.__dragPos:
            self.move(event.globalPos() - self.__dragPos)

    def mouseReleaseEvent(self, event):
        self.__dragWin = False
        self.setCursor(QCursor(Qt.ArrowCursor))

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
            self.buttons.append(btn)
            grid.addWidget(btn, i // 4, i % 4)

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

    def refresh_sign_status(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT last_sign_date FROM sign_in WHERE username=?", (self.username,))
            row = cursor.fetchone()
            conn.close()

            for btn in self.buttons:
                btn.setChecked(False)

            if row and row["last_sign_date"] == self.today_date:
                self.buttons[self.today_weekday].setChecked(True)
        except:
            pass

    def sign_click(self, idx):
        if idx != self.today_weekday:
            QMessageBox.warning(self, "提示", "只能签到今天哦!")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT last_sign_date FROM sign_in WHERE username=?", (self.username,))
            row = cursor.fetchone()

            if row and row["last_sign_date"] == self.today_date:
                QMessageBox.information(self, "提示", "你今天已经签到过啦!")
                conn.close()
                return

            # 祈愿币 +10
            cursor.execute("UPDATE users SET coin = coin + 10 WHERE username=?", (self.username,))

            cursor.execute('''
                INSERT OR REPLACE INTO sign_in (username, last_sign_date)
                VALUES (?, ?)
            ''', (self.username, self.today_date))

            conn.commit()
            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "错误", f"签到失败：{str(e)}")
            return

        self.buttons[idx].setChecked(True)
        QMessageBox.information(self, "签到成功", "🎉 签到成功！获得 10 祈愿币！")