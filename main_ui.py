from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MainUI(QWidget):
    def __init__(self):
        super().__init__()

        # 核心：用 QGridLayout 让所有控件叠加在同一块区域
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0,0,0,0)

        # ---------------------- 视频背景（第一层） ----------------------
        self.center_label = QLabel()
        self.center_label.setScaledContents(True)
        self.layout().addWidget(self.center_label, 0, 0)

        # ---------------------- 悬浮控件层（第二层，透明） ----------------------
        self.overlay = QWidget()
        self.overlay.setStyleSheet("background:transparent;")
        self.layout().addWidget(self.overlay, 0, 0)

        # 给悬浮层设置布局
        vbox = QVBoxLayout(self.overlay)
        vbox.setContentsMargins(20, 20, 20, 30)

        # ========== 顶部：左音乐 + 右祈愿币/最小化/关闭 ==========
        top_bar = QHBoxLayout()

        # 左：音乐
        self.music_btn = QCheckBox(" 🎵 BGM")
        self.music_btn.setChecked(True)
        self.music_btn.setStyleSheet("""
            QCheckBox {
                color:white; font-size:16px; 
                background:rgba(255,80,140,0.8); 
                padding:6px 12px; border-radius:8px;
            }
        """)
        top_bar.addWidget(self.music_btn)
        top_bar.addStretch()

        # 右：祈愿币
        self.mana_label = QLabel("祈愿币：0")
        self.mana_label.setStyleSheet("""
            QLabel {
                color:white; font-size:16px; font-weight:bold;
                background:rgba(255,60,60,0.8);
                padding:6px 12px; border-radius:8px;
            }
        """)

        # 窗口按钮
        self.min_btn = QPushButton("—")
        self.close_btn = QPushButton("✕")
        btn_style = """
            QPushButton {
                background:rgba(255,80,140,0.9); color:white;
                font-size:16px; padding:6px 10px; border-radius:8px;
                min-width:40px;
            }
            QPushButton:hover {
                background:rgba(255,20,100,1);
            }
        """
        self.min_btn.setStyleSheet(btn_style)
        self.close_btn.setStyleSheet(btn_style)

        top_bar.addWidget(self.mana_label)
        top_bar.addWidget(self.min_btn)
        top_bar.addWidget(self.close_btn)

        # ========== 底部：功能按钮横向排列 ==========
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(14)
        bottom_bar.setAlignment(Qt.AlignCenter)

        self.btn_1 = QPushButton("✨单抽")
        self.btn_record = QPushButton("🎴抽卡记录")
        self.btn_collection = QPushButton("🔮图鉴")
        self.btn_stats = QPushButton("🍀欧非鉴定")
        self.btn_reset = QPushButton("🔄 重置祈愿币")

        btn_style2 = """
            QPushButton {
                background:rgba(255,80,140,0.9); color:white;
                font-size:16px; padding:12px 24px; border-radius:10px;
            }
            QPushButton:hover {
                background:rgba(255,20,100,1);
            }
        """
        for btn in [self.btn_1, self.btn_record, self.btn_collection, self.btn_stats, self.btn_reset]:
            btn.setStyleSheet(btn_style2)
            bottom_bar.addWidget(btn)

        # ========== 组装布局 ==========
        vbox.addLayout(top_bar)
        vbox.addStretch()  # 把按钮推到最底部
        vbox.addLayout(bottom_bar)