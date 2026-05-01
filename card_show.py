from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2

class card_show(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(900, 600)

        # 拖拽功能
        self.dragging = False
        self.offset = QPoint()

        # ---------------------- 视频层（全屏，播放时独占窗口） ----------------------
        self.video_label = QLabel(self)
        self.video_label.setScaledContents(True)
        self.video_label.setGeometry(0, 0, 900, 600)

        # ---------------------- 结果界面（默认隐藏，视频播完才显示） ----------------------
        self.result_widget = QWidget(self)
        self.result_widget.setGeometry(0, 0, 900, 600)
        self.result_widget.setVisible(False)
        self.result_widget.setStyleSheet("background-color: #1a1a2e;")

        # 结果布局
        layout = QVBoxLayout(self.result_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        # 调整边距，给顶部和底部留出更多空间
        layout.setContentsMargins(0, 40, 0, 40)

        # 标题：抽卡结果
        self.title_label = QLabel("抽卡结果")
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # 卡片图片显示（调整大小和位置，避免被按钮挡住）
        self.card_label = QLabel()
        self.card_label.setAlignment(Qt.AlignCenter)
        # 减小卡片高度，确保不会超出按钮上方的区域
        self.card_label.setFixedSize(350, 380)
        layout.addWidget(self.card_label, alignment=Qt.AlignCenter)

        # 关闭按钮（位置靠下，和卡片保持距离）
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

        # 视频定时器（正常速度）
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_frame)
        self.timer.setInterval(33)

    # ---------------------- 启动：只播放视频 ----------------------
    def show_card(self, pic_path):
        self.card_path = pic_path
        self.cap = cv2.VideoCapture("02.mp4")
        self.video_label.setVisible(True)
        self.result_widget.setVisible(False)
        self.timer.start()
        self.show()

    # ---------------------- 逐帧播放视频（全屏） ----------------------
    def play_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.show_result()
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    # ---------------------- 视频结束 → 显示结果界面 ----------------------
    def show_result(self):
        self.timer.stop()
        self.cap.release()

        # 切换界面：隐藏视频，显示结果页
        self.video_label.setVisible(False)
        self.result_widget.setVisible(True)

        # 加载并缩放卡片，匹配新的显示区域大小
        pix = QPixmap(self.card_path).scaled(
            350, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.card_label.setPixmap(pix)

    # ---------------------- 关闭 ----------------------
    def close_all(self):
        self.timer.stop()
        if hasattr(self, 'cap'):
            self.cap.release()
        self.closed.emit()
        self.close()

    # ---------------------- 拖拽 ----------------------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = e.globalPos() - self.pos()

    def mouseMoveEvent(self, e):
        if self.dragging:
            self.move(e.globalPos() - self.offset)

    def mouseReleaseEvent(self, e):
        self.dragging = False