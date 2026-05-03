from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from database import init_db, register_user, login_user

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("抽卡模拟器 - 登录/注册")
        self.setFixedSize(450, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        init_db()
        self.current_user = None
        self.init_ui()
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fbd3e9, stop:1 #bbbbff);
            }
        """)

    def init_ui(self):
        self.stack = QStackedWidget()
        self.login_page = self.create_login_page()
        self.register_page = self.create_register_page()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)
        self.stack.setCurrentIndex(0)
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    # ========== LOGO水平居中 ==========
    def create_logo_label(self):
        logo_label = QLabel()
        pixmap = QPixmap("logo.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(
                200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        logo_label.setAlignment(Qt.AlignCenter)
        return logo_label

    # ========== 标题样式 ==========
    def label_style(self, text, size=18, bold=True):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        font = QFont("Microsoft YaHei", size)
        font.setBold(bold)
        label.setFont(font)
        label.setStyleSheet("color: #333333; margin-top:0px;")
        return label

    def common_input_style(self):
        return """
            QLineEdit {
                border: 2px solid #c8c8e0;
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 14px;
                background: rgba(255,255,255,180);
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #7b68ee;
                background: rgba(255,255,255,220);
            }
        """

    def common_btn_style(self, color="#7b68ee"):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
        """

    def lighten_color(self, hex_color):
        light_map = {"#7b68ee": "#9a8cf0", "#ff7272": "#ff9292", "#ff9292": "#ffb2b2"}
        return light_map.get(hex_color, hex_color)

    def darken_color(self, hex_color):
        dark_map = {"#7b68ee": "#6a5acd", "#ff7272": "#e65c5c", "#ff9292": "#e67a7a"}
        return dark_map.get(hex_color, hex_color)

    # ========== 登录页 ==========
    def create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 20, 40, 30)
        layout.setSpacing(5)

        layout.addWidget(self.create_logo_label())
        layout.addWidget(self.label_style("🐱 用户登录", 18))

        layout.addWidget(QLabel("用户名"))
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("请输入用户名")
        self.login_username.setStyleSheet(self.common_input_style())
        layout.addWidget(self.login_username)

        layout.addWidget(QLabel("密码"))
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("请输入密码")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setStyleSheet(self.common_input_style())
        layout.addWidget(self.login_password)

        btn_layout = QHBoxLayout()
        login_btn = QPushButton("登录")
        login_btn.setStyleSheet(self.common_btn_style())
        login_btn.clicked.connect(self.handle_login)
        btn_layout.addWidget(login_btn)

        goto_register_btn = QPushButton("去注册")
        goto_register_btn.setStyleSheet(self.common_btn_style("#ff9292"))
        goto_register_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_layout.addWidget(goto_register_btn)

        layout.addLayout(btn_layout)
        page.setLayout(layout)
        return page

    # ========== 注册页 ==========
    def create_register_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 20, 40, 30)
        layout.setSpacing(5)

        layout.addWidget(self.create_logo_label())
        layout.addWidget(self.label_style("🐱 用户注册", 18))

        layout.addWidget(QLabel("用户名"))
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("至少3个字符")
        self.reg_username.setStyleSheet(self.common_input_style())
        layout.addWidget(self.reg_username)

        layout.addWidget(QLabel("密码"))
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("至少6个字符")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setStyleSheet(self.common_input_style())
        layout.addWidget(self.reg_password)

        layout.addWidget(QLabel("确认密码"))
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("再次输入密码")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        self.reg_confirm.setStyleSheet(self.common_input_style())
        layout.addWidget(self.reg_confirm)

        btn_layout = QHBoxLayout()
        register_btn = QPushButton("注册")
        register_btn.setStyleSheet(self.common_btn_style())
        register_btn.clicked.connect(self.handle_register)
        btn_layout.addWidget(register_btn)

        goto_login_btn = QPushButton("去登录")
        goto_login_btn.setStyleSheet(self.common_btn_style("#ff9292"))
        goto_login_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_layout.addWidget(goto_login_btn)

        layout.addLayout(btn_layout)
        page.setLayout(layout)
        return page

    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "提示", "用户名和密码不能为空！")
            return
        success, msg = login_user(username, password)
        if success:
            self.current_user = username
            QMessageBox.information(self, "成功", f"欢迎回来，{username}！")
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)

    def handle_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()
        confirm = self.reg_confirm.text().strip()
        if len(username) < 3:
            QMessageBox.warning(self, "提示", "用户名至少需要3个字符！")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "提示", "密码至少需要6个字符！")
            return
        if password != confirm:
            QMessageBox.warning(self, "提示", "两次输入的密码不一致！")
            return
        success, msg = register_user(username, password)
        if success:
            QMessageBox.information(self, "成功", "注册成功！请登录。")
            self.stack.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "失败", msg)