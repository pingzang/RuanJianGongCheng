from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
import os
import re

class CollectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("卡牌图鉴")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #f9e5f9;")

        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QGridLayout(central)
        self.layout.setSpacing(15)

        self.ALL_CARDS = [
            "star3_1.jpg",
            "star3_2.jpg",
            "star4_1.jpg",
            "star4_2.jpg",
            "star4_3.jpg",
            "star5_1.jpg"
        ]
        self.IMAGE_DIR = "pic"
        self.PLACEHOLDER = "lock.png"

        if not os.path.exists(self.PLACEHOLDER):
            grey = QPixmap(150, 200)
            grey.fill(QColor("#cccccc"))
            painter = QPainter(grey)
            painter.setPen(QColor("#666666"))
            painter.setFont(QFont("微软雅黑", 18, QFont.Bold))
            painter.drawText(grey.rect(), Qt.AlignCenter, "未获得")
            painter.end()
            grey.save(self.PLACEHOLDER)

        self.refresh_collection()

    def refresh_collection(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        # 读取并清理脏数据
        try:
            data = np.load("receive_card.npy", allow_pickle=True)
            received = [str(item) for item in data]
        except:
            received = []

        # 从文字里自动提取 xxx.jpg
        owned = set()
        for text in received:
            match = re.findall(r'star\d+_\d+\.jpg', text)
            owned.update(match)

        print("=" * 50)
        print("实际拥有的卡牌：", list(owned))
        print("=" * 50)

        row = 0
        col = 0
        for card in self.ALL_CARDS:
            box = QGroupBox()
            box.setStyleSheet("background:#ffffff;border-radius:10px;")
            vbox = QVBoxLayout(box)

            img_label = QLabel()
            img_label.setFixedSize(150, 200)
            img_label.setScaledContents(True)

            if card in owned:
                img_path = os.path.join(self.IMAGE_DIR, card)
            else:
                img_path = self.PLACEHOLDER

            if os.path.exists(img_path):
                img_label.setPixmap(QPixmap(img_path))
            else:
                img_label.setPixmap(QPixmap(self.PLACEHOLDER))

            name_label = QLabel(card.replace(".jpg", ""))
            name_label.setAlignment(Qt.AlignCenter)

            vbox.addWidget(img_label)
            vbox.addWidget(name_label)
            self.layout.addWidget(box, row, col)

            col += 1
            if col >= 4:
                col = 0
                row += 1

    def showEvent(self, event):
        self.refresh_collection()
        super().showEvent(event)