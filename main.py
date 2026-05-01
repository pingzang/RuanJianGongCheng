# code:utf-8
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
import sys
from main_ui import MainUI
import numpy_operator as npor
import numpy as np
import card_show
from showrecord import record_window
import cv2
from sign_ui import SignDialog
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import QCursor
from stats_window import StatsWindow

# class card_func(QMainWindow, Ui_getcard):
# from stats_window import StatsWindow

class card_func(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = MainUI()
        self.setCentralWidget(self.ui)

        # ===================== 初始化 =====================
        self.init_ui()
        self.init_audio()       # 单个音频，循环
        self.init_video()       # 单个视频，循环
        self.init_card_data()   # 抽卡数据
        # self.pushButton_3.clicked.connect(self.recordit)
        # ========== 在这里加这一行 ==========
        self.stats_window = None  # 加在这里！
        
        # ===================== 按钮绑定 =====================
        self.ui.btn_1.clicked.connect(self.gachicard)        #单抽
        self.ui.btn_record.clicked.connect(self.recordit)    #抽卡记录
        self.ui.btn_collection.clicked.connect(self.open_collection) #图鉴
        self.ui.btn_stats.clicked.connect(self.open_stats)   #抽卡统计
        self.ui.btn_reset.clicked.connect(self.update_card)  #重置祈愿币/卡池
        self.ui.music_btn.toggled.connect(self.toggle_music) #音乐开关

        # ✅ 每日签到按钮（正确位置 + 正确样式）
        self.sign_btn = QPushButton("每日签到", self)
        self.sign_btn.setFixedSize(120, 40)
        self.sign_btn.move(30, self.height() - 70)  # 左下角位置
        self.sign_btn.setStyleSheet("""
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
        self.sign_btn.clicked.connect(self.open_sign_dialog)

    # 设置默认大小
    def default_size(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        if (size.width() < screen.width()) & (size.height() < screen.height()) & \
                (size.width() <= 1920) & (size.height() <= 1080):
            self.setGeometry(0, 0, screen.width(), screen.height())
        elif (size.width() < screen.width()) & (size.height() < screen.height()) & \
                (size.width() > 1920) & (size.height() > 1080):
            self.setGeometry(0, 0, 1920, 1080)

    # ===================== 窗口初始化 =====================
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)         #隐藏窗口栏
        self.setFixedSize(1000, 600)
        self.ui.close_btn.clicked.connect(self.close)
        self.ui.min_btn.clicked.connect(self.showMinimized)
        self.ui.music_btn.setChecked(True)  # 默认开启音乐

    # ===================== 单个音频循环播放 =====================
    def init_audio(self):
        self.bgm = QMediaPlayer()
        self.bgm.setMedia(QMediaContent(QUrl.fromLocalFile("bgm.mp3")))
        self.bgm.setVolume(60)
        self.bgm.play()  # 启动就播放

    def toggle_music(self):
        # 勾选播放，取消停止
        if self.ui.music_btn.isChecked():
            self.bgm.play()
        else:
            self.bgm.stop()

    # ===================== 单个视频循环 =====================
    def init_video(self):
        self.video_thread = VideoThread()
        self.video_thread.video_signal.connect(self.show_video_frame)
        self.video_thread.start()

    def show_video_frame(self, img):
        self.ui.center_label.setPixmap(QtGui.QPixmap.fromImage(img))

    # ===================== 抽卡逻辑 =====================
    def init_card_data(self):
        self.Dialogue = card_show.card_show()
        self.pic, self.count_pic = npor.read_num()
        print(f"卡池加载完成：共{len(self.pic)}张卡，当前祈愿币：{self.count_pic}")
        self.ui.mana_label.setText(f"✨祈愿币：{self.count_pic}")
        self.Dialogue.closed.connect(self.save_num)

    def lack_mana(self):
        QMessageBox.warning(self, "提示", "祈愿币不足！")

    def gachicard(self):
        if self.count_pic <= 0:
            self.lack_mana()
            return
        self.picdir, self.initpic = npor.gachi_card_out()
        if not self.picdir or self.initpic == -1:
            self.lack_mana()
            return

        # 3. 更新本地祈愿币变量（同步文件）
        _, self.count_pic = npor.read_num()
        self.Dialogue.show()
        self.Dialogue.show_card(self.picdir)

    def save_num(self):
        # 同步读取最新祈愿币
        _, self.count_pic = npor.read_num()
        # 更新UI显示
        self.ui.mana_label.setText(f"✨祈愿币：{self.count_pic}")
    def update_card(self):
        new_mana = npor.reset_mana()
        # 同步更新UI
        self.count_pic = new_mana
        self.ui.mana_label.setText(f"✨祈愿币：{self.count_pic}")

    # ===================== 功能窗口 =====================
    def recordit(self):
        self.record_win = record_window()
        self.record_win.show()
        self.record_win.print_record()

    def open_stats(self):
        self.stats_win = StatsWindow()
        self.stats_win.show()

    # ✅【修复】签到函数 —— 已经放进类里面了！
    def open_sign_dialog(self):
        dialog = SignDialog(self)
        dialog.exec_()
    # ===================== 窗口拖拽 =====================
    
    # 新增：打开图鉴功能
    def open_collection(self):
        from collection_window import CollectionWindow
    # 如果窗口已经存在，直接刷新再显示，不用重复创建
        if hasattr(self, 'collect') and self.collect.isVisible():
                self.collect.refresh_collection()
                self.collect.raise_()
        else:
            self.collect = CollectionWindow()
            self.collect.show()
#   以下都是重写功能 主要实现两大功能

    # 拖拽功能
    def mousePressEvent(self, e):
        self.__dragWin = True
        self.__dragWin_x = e.x()
        self.__dragWin_y = e.y()
        self.drag = True
        self.x = e.x()
        self.y = e.y()
        self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, e):
        if hasattr(self, '__dragWin') and self.__dragWin:
            pos = e.globalPos()
            self.move(pos.x() - self.__dragWin_x, pos.y() - self.__dragWin_y)
        elif hasattr(self, 'drag') and self.drag:
            self.move(e.globalPos().x() - self.x, e.globalPos().y() - self.y)

# 多线程
class Update(QThread):
    date1 = pyqtSignal()
    def __init__(self):
        super(Update, self).__init__()
# ===================== 视频线程 =====================
class VideoThread(QThread):
    video_signal = pyqtSignal(QtGui.QImage)

    def run(self):
        cap = cv2.VideoCapture("01.mp4")
        while True:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                # 缩放以适应 label 大小（可选）
                qt_image = qt_image.scaled(1000, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.video_signal.emit(qt_image)
                time.sleep(0.033)
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

class Update1(QThread):
    date2 = pyqtSignal()
    def __init__(self):
        super(Update1, self).__init__()
    def run(self):
        while True:
            time.sleep(0.1)
            self.date2.emit()

class Update_v(QThread):
    video2label = pyqtSignal(QtGui.QImage)
    def __init__(self):
        super(Update_v, self).__init__()
    def run(self):
        cap = cv2.VideoCapture('02.mp4')
        while True:
            ret = cap.grab()
            if video_status == 1:
                if ret:
                    ret, frame = cap.retrieve()
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                    if w1 & h1:
                        convertToQtFormat = convertToQtFormat.scaled(w1, h1)
                    cv2.waitKey(20)
                    self.video2label.emit(convertToQtFormat)
                else:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
            elif video_status == 2:
                continue
            else:
                cap.release()
                return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mk1 = card_func()
    mk1.show()
    sys.exit(app.exec_())