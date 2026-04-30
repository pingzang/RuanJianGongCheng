from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import card_analysis

class StatsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("抽卡统计 & 欧非鉴定")
        self.setGeometry(100, 100, 750, 600)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20,20,20,20)

        # 标题
        title = QLabel("📊 抽卡统计分析")
        title.setStyleSheet("font-size:22px; font-weight:bold;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # 欧皇等级
        self.grade_label = QLabel("等级：未检测")
        self.grade_label.setStyleSheet("font-size:20px; color:#e74c3c; font-weight:bold;")
        self.grade_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.grade_label)

        # 刷新
        refresh_btn = QPushButton("🔄 刷新数据")
        refresh_btn.clicked.connect(self.refresh)
        main_layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)

        # 信息展示
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("font-size:14px;")
        main_layout.addWidget(self.info_text)

        self.refresh()

    def refresh(self):
        # 获取解析后的数据
        iv5, iv4, cnt5, cnt4, total = card_analysis.parse_card_records()
        grade, stats = card_analysis.judge_eu_non(iv5, iv4, cnt5, cnt4, total)

        # 显示等级
        self.grade_label.setText(f"🎭 你的欧非等级：【{grade}】")

        # 拼接显示内容
        msg = f"""
【基础统计】
总抽数：{stats['总抽数']}
五星数量：{stats['五星数量']}
四星数量：{stats['四星数量']}

【真实概率】
五星概率：{stats['五星真实概率(%)']}%（理论：10%）
四星概率：{stats['四星真实概率(%)']}%（理论：30%）

【间隔抽数（两个相同星级之间的抽数）】
五星间隔：{stats['五星间隔列表']}
四星间隔：{stats['四星间隔列表']}

【平均间隔】
五星平均间隔：{stats['五星平均间隔']} 抽
四星平均间隔：{stats['四星平均间隔']} 抽
        """
        self.info_text.setText(msg)