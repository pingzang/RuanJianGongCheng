from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import card_analysis

class StatsWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username  # 保存用户名
        
        # 初始化界面
        self._init_ui()
        # 首次加载数据
        self.refresh()

    def _init_ui(self):
        """初始化界面布局"""
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

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新数据")
        refresh_btn.clicked.connect(self.refresh)
        main_layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)

        # 信息展示文本框
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("font-size:14px;")
        main_layout.addWidget(self.info_text)

        # 窗口基础设置
        self.setWindowTitle(f"{self.username}的抽卡统计")
        self.resize(600, 800)

    def refresh(self):
        """刷新数据（从数据库读取真实数据）"""
        try:
            # 调用card_analysis从数据库解析数据
            iv5, iv4, cnt5, cnt4, total = card_analysis.parse_card_records(self.username)
            grade, stats = card_analysis.judge_eu_non(iv5, iv4, cnt5, cnt4, total)

            # 更新欧皇等级显示
            self.grade_label.setText(f"🎭 你的欧非等级：【{grade}】")

            # 拼接显示内容
            msg = f"""
【基础统计】
总抽数：{stats['总抽数']}
五星数量：{stats['五星数量']}
四星数量：{stats['四星数量']}

【真实概率】
五星概率：{stats['五星真实概率(%)']:.2f}%（理论：10%）
四星概率：{stats['四星真实概率(%)']:.2f}%（理论：30%）

【间隔抽数（两个相同星级之间的抽数）】
五星间隔：{stats['五星间隔列表']}
四星间隔：{stats['四星间隔列表']}

【平均间隔】
五星平均间隔：{stats['五星平均间隔']:.2f} 抽
四星平均间隔：{stats['四星平均间隔']:.2f} 抽
            """
            self.info_text.setText(msg)
        except Exception as e:
            self.grade_label.setText("🎭 你的欧非等级：【数据加载失败】")
            self.info_text.setText(f"数据刷新失败：{str(e)}\n请检查：\n1. 数据库是否初始化\n2. 是否有抽卡记录\n3. 用户名是否正确")

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = StatsWindow("测试用户")
    window.show()
    sys.exit(app.exec_())