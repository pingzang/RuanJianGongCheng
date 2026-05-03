# code:utf-8
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import *
import sys
import sqlite3
import cv2
import time

class record_window(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)

        self.setupUi()

        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.set_bg_frame)
        self.video_thread.start()

        self.drag = False

    def set_bg_frame(self, qimg):
        self.bg_label.setPixmap(QtGui.QPixmap.fromImage(qimg))

    def setupUi(self):
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, 1000, 600)
        self.bg_label.lower()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # 顶部栏
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 80, 170, 10)

        title = QLabel("祈愿记录")
        title.setStyleSheet("""
            QLabel {
                color: #ff9292;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
            }
        """)
        top_bar.addStretch(1)
        top_bar.addWidget(title)
        top_bar.addStretch(1)

        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(38, 38)
        close_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 20px;
                background-color: #ff9292;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #ff7272;
            }
        """)
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)

        main_layout.addLayout(top_bar)

        # 文本框
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(160, 13, 100, 40)

        self.textEdit = QTextEdit()
        self.textEdit.setFixedSize(680, 420)
        self.textEdit.setStyleSheet("""
            QTextEdit {
                color: #ff9292;
                font-size: 15px;
                border: none;
                background: transparent;
                padding: 10px;
            }
        """)
        content_layout.addWidget(self.textEdit, alignment=Qt.AlignLeft)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def print_record(self, username):
        self.textEdit.clear()
        if not username:
            self.textEdit.append("                               请先登录！")
            return

        try:
            conn = sqlite3.connect("game_data.db")
            cursor = conn.cursor()
            cursor.execute('''
                SELECT draw_time, card_name, card_star 
                FROM gacha_history 
                WHERE username = ? 
                ORDER BY draw_time DESC
            ''', (username,))
            records = cursor.fetchall()
            conn.close()

            if not records:
                self.textEdit.append("                               暂无抽卡记录")
                return

            self.textEdit.append("                       ━━━━━━━━  祈愿记录  ━━━━━━━━\n")
            for time_str, card_name, star in records:
                self.textEdit.append(f"                       {time_str}")
                self.textEdit.append(f"                       ★{star}   {card_name}")
                self.textEdit.append("                       --------------------------------\n")

        except Exception as e:
            self.textEdit.append(f"                       读取失败：{str(e)}")

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag = True
            self.drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self.drag:
            self.move(e.globalPos() - self.drag_pos)

    def mouseReleaseEvent(self, e):
        self.drag = False

    def closeEvent(self, event):
        self.video_thread.stop()
        event.accept()

class VideoThread(QThread):
    frame_signal = pyqtSignal(QtGui.QImage)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        cap = cv2.VideoCapture("03.mp4")
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = 1.0 / fps

        while self.running:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            q_img = QtGui.QImage(frame.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
            q_img = q_img.scaled(1000, 600, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.frame_signal.emit(q_img)
            time.sleep(delay)

    def stop(self):
        self.running = False
        self.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = record_window()
    win.show()
    sys.exit(app.exec_())