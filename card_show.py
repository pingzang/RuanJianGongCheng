from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import cv2
import os

class card_show(QWidget):
    closed = pyqtSignal()
    resume_bgm = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(900, 600)

        self.dragging = False
        self.offset = QPoint()

        self.video_label = QLabel(self)
        self.video_label.setScaledContents(True)
        self.video_label.setGeometry(0, 0, 900, 600)

        self.result_widget = QWidget(self)
        self.result_widget.setGeometry(0, 0, 900, 600)
        self.result_widget.setVisible(False)

        self.bg_pixmap = QPixmap("background.jpg")
        self.result_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        layout = QVBoxLayout(self.result_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 40, 0, 40)

        self.title_label = QLabel("抽卡结果")
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.card_label = QLabel()
        self.card_label.setAlignment(Qt.AlignCenter)
        self.card_label.setFixedSize(350, 380)
        self.card_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.card_label, alignment=Qt.AlignCenter)

        self.close_btn = QPushButton("关闭")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff477e;
                color: white;
                font-size: 18px;
                padding: 10px 40px;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #ff2e63;
            }
        """)
        self.close_btn.clicked.connect(self.close_all)
        layout.addWidget(self.close_btn, alignment=Qt.AlignCenter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.play_frame)
        self.timer.setInterval(33)

        # 抽卡音效
        self.gacha_sound = QMediaPlayer()
        self.sound_file = "gacha.mp3"

    def paintEvent(self, event):
        if self.result_widget.isVisible():
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.bg_pixmap)

    def show_card(self, pic_path):
        self.card_path = pic_path
        self.cap = cv2.VideoCapture("02.mp4")
        self.video_label.setVisible(True)
        self.result_widget.setVisible(False)

        # 播放抽卡音效
        if os.path.exists(self.sound_file):
            self.gacha_sound.stop()
            self.gacha_sound.setMedia(QMediaContent(QUrl.fromLocalFile(self.sound_file)))
            self.gacha_sound.setVolume(70)
            self.gacha_sound.play()

        self.timer.start()
        self.show()

    def play_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.show_result()
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def show_result(self):
        self.timer.stop()
        self.cap.release()
        self.video_label.setVisible(False)
        self.result_widget.setVisible(True)

        pix = QPixmap(self.card_path).scaled(350, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.card_label.setPixmap(pix)

    def close_all(self):
        self.timer.stop()
        if hasattr(self, 'cap'):
            self.cap.release()

        self.gacha_sound.stop()
        self.resume_bgm.emit()
        self.closed.emit()
        self.close()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = e.globalPos() - self.pos()

    def mouseMoveEvent(self, e):
        if self.dragging:
            self.move(e.globalPos() - self.offset)

    def mouseReleaseEvent(self, e):
        self.dragging = False