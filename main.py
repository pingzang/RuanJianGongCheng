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
from stats_window import StatsWindow

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
        # self.musicon = self.radioButton.isChecked()
        # self.Update1 = Update()
        # self.Update1.start()
        # self.Update_s = Update1()
        # self.Update_s.start()
        # self.Update1.date1.connect(self.musicplay)
        # self.videoinit()
        # self.player.mediaStatusChanged.connect(self.alternativemusic)
        # self.player1.mediaStatusChanged.connect(self.alternativemusic)
        # self.pushButton_2.clicked.connect(self.gachicard)
        # self.pushButton_4.clicked.connect(self.tipit)
        # self.pushButton_5.clicked.connect(self.update_card)
        # self.Update_s.date2.connect(self.video_size)
        # self.pushButton_3.clicked.connect(self.recordit)
        # ========== 在这里加这一行 ==========
        self.stats_window = None  # 加在这里！
        # 👇 新增图鉴按钮 👇
        self.pushButton_6.clicked.connect(self.open_collection)

        # ===================== 按钮绑定 =====================
        self.ui.btn_1.clicked.connect(self.gachicard)        #单抽
        self.ui.btn_record.clicked.connect(self.recordit)    #抽卡记录
        self.ui.btn_stats.clicked.connect(self.open_stats)   #抽卡统计
        self.ui.btn_reset.clicked.connect(self.update_card)  #重置祈愿币/卡池
        self.ui.music_btn.toggled.connect(self.toggle_music) #音乐开关

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

#   拖拽功能
    def mousePressEvent(self, e):
        self.drag = True
        self.x = e.x()
        self.y = e.y()

    def mouseMoveEvent(self, e):
        if self.drag:
            self.move(e.globalPos().x() - self.x, e.globalPos().y() - self.y)

    def mouseReleaseEvent(self, e):
        self.drag = False

# ===================== 视频线程 =====================
class VideoThread(QThread):
    video_signal = pyqtSignal(QtGui.QImage)

    def run(self):
        cap = cv2.VideoCapture("01.mp4")
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
            qimg = qimg.scaled(900, 500, Qt.KeepAspectRatio)
            self.video_signal.emit(qimg)
            cv2.waitKey(30)

# ===================== 启动 =====================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = card_func()
    win.show()
    sys.exit(app.exec_())