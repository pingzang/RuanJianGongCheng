from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from card_pool import CARD_POOL  

class CollectionWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("卡牌图鉴")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #f9e5f9;")

        # ========== 滚动区域 ==========
        #创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 自适应子控件大小
        scroll_area.setStyleSheet("border: none;")  # 隐藏滚动区域边框
        self.setCentralWidget(scroll_area)

        #滚动区域的内容容器
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        self.layout = QGridLayout(scroll_content)  # 布局移到滚动内容容器
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)  # 增加内边距，避免贴边

        #从卡池配置中获取所有卡片的完整信息
        self.all_cards = []
        for star in CARD_POOL:
            self.all_cards.extend(CARD_POOL[star])
        
        self.placeholder_path = "lock.png"
        self._init_placeholder()  #初始化占位图
        self.refresh_collection()

    def _init_placeholder(self):
        """初始化未获得卡片的占位图"""
        if not os.path.exists(self.placeholder_path):
            grey = QPixmap(150, 200)
            grey.fill(QColor("#cccccc"))
            painter = QPainter(grey)
            painter.setPen(QColor("#666666"))
            painter.setFont(QFont("微软雅黑", 18, QFont.Bold))
            painter.drawText(grey.rect(), Qt.AlignCenter, "未获得")
            painter.end()  # 释放画笔
            grey.save(self.placeholder_path)

    def _load_owned_cards(self):
        """加载用户已获得的卡片名称（精准异常捕获）"""
        try:
            conn = sqlite3.connect("game_data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT card_name FROM collection WHERE username=?", (self.username,))
            rows = cursor.fetchall()
            conn.close()
            return set([row[0] for row in rows])  # 转集合，提升匹配效率
        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"加载图鉴失败：{str(e)}")
            return set()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载图鉴失败：{str(e)}")
            return set()

    def refresh_collection(self):
        """刷新图鉴显示（核心逻辑）"""
        # 清空原有布局
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        owned_cards = self._load_owned_cards()
        row = col = 0

        # 遍历所有卡片，逐个显示
        for card in self.all_cards:
            card_name = card["name"]
            card_star = card["star"]
            card_img_path = card["pic_path"]

            # 创建卡片容器
            box = QGroupBox(f"{card_star}星 - {card_name}")
            box.setStyleSheet("background:#ffffff;border-radius:10px;padding:10px;")
            box.setFixedSize(180, 250)  # 固定卡片大小，避免错位
            vbox = QVBoxLayout(box)
            vbox.setContentsMargins(5, 5, 5, 5)  # 卡片内边距

            # 加载卡片图片
            img_label = QLabel()
            img_label.setFixedSize(150, 200)
            img_label.setScaledContents(True)  # 自适应大小

            if card_name in owned_cards:
                # 已获得：加载实际图片
                if os.path.exists(card_img_path):
                    img_label.setPixmap(QPixmap(card_img_path))
                else:
                    # 图片不存在：显示占位图+提示
                    img_label.setPixmap(QPixmap(self.placeholder_path))
                    QMessageBox.warning(self, "提示", f"卡片{card_name}的图片{card_img_path}不存在！")
            else:
                # 未获得：显示占位图
                img_label.setPixmap(QPixmap(self.placeholder_path))

            # 添加状态标签
            status_label = QLabel("已获得" if card_name in owned_cards else "未获得")
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet(f"color: {'green' if card_name in owned_cards else 'red'}; font-weight: bold;")

            # 添加到布局
            vbox.addWidget(img_label)
            vbox.addWidget(status_label)
            self.layout.addWidget(box, row, col)

            # 控制每行显示4个卡片
            col += 1
            if col >= 4:
                col = 0
                row += 1

    def showEvent(self, event):
        """窗口显示时刷新"""
        self.refresh_collection()
        super().showEvent(event)