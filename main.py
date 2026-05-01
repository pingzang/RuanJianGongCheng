# code:utf-8
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
import sys
from getcard import Ui_getcard
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
import time
import numpy_operator as npor
import numpy as np
import card_show
from showrecord import record_window
from PyQt5.QtGui import QCursor
import cv2
import operator_tip_use
from sign_ui import SignDialog

class card_func(QMainWindow, Ui_getcard):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()
        self.musicon = self.radioButton.isChecked()
        self.Update1 = Update()
        self.Update1.start()
        self.Update_s = Update1()
        self.Update_s.start()
        self.Update1.date1.connect(self.musicplay)
        self.videoinit()
        self.player.mediaStatusChanged.connect(self.alternativemusic)
        self.player1.mediaStatusChanged.connect(self.alternativemusic)
        self.pushButton_2.clicked.connect(self.gachicard)
        self.pushButton_4.clicked.connect(self.tipit)
        self.pushButton_5.clicked.connect(self.update_card)
        self.Update_s.date2.connect(self.video_size)
        self.pushButton_3.clicked.connect(self.recordit)

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

    # 初始化开始界面
    def videoinit(self):
        global video_status, w1, h1
        video_status = 1
        w1 = 719
        h1 = 400
        self.Update_v = Update_v()
        self.Update_v.start()
        self.Update_v.video2label.connect(self.videoplay)

    # 实时变换视频大小
    def video_size(self):
        self.screenfull_w = self.screenfull.geometry().width()
        self.screenfull_h = self.screenfull.geometry().height()
        global w1, h1
        w1 = self.screenfull_w
        h1 = self.screenfull_h

    # 配置界面
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.default_size()
        self.pushButton.clicked.connect(self.close)
        self.pushButton_back.clicked.connect(self.showMinimized)
        self.musicinit()
        self.musicinit_re()
        self.readtime = 0
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_card()

    # 初始化BGM
    def musicinit(self):
        self.play1 = False
        self.firstplay = True
        wavefile = QUrl.fromLocalFile('Grand.wav')
        content = QMediaContent(wavefile)
        self.player = QMediaPlayer()
        self.player.setMedia(content)
        self.player.setVolume(60)

    # 初始化第二段BGM
    def musicinit_re(self):
        rewave = QUrl.fromLocalFile('Grand_01.wav')
        recontent = QMediaContent(rewave)
        self.player1 = QMediaPlayer()
        self.player1.setMedia(recontent)
        self.player1.setVolume(60)

    # 播放BGM
    def musicplay(self):
        self.musicon = self.radioButton.isChecked()
        if self.firstplay:
            if self.musicon & (not self.play1):
                self.player.play()
                self.play1 = True
            elif (not self.musicon) & self.play1:
                self.player.stop()
                self.player1.stop()
                self.play1 = False
                self.firstplay = False
        elif not self.firstplay:
            if self.musicon & (not self.play1):
                self.player1.play()
                self.play1 = True
            elif (not self.musicon) & self.play1:
                self.player.stop()
                self.player1.stop()
                self.play1 = False

    # 音频切换
    def alternativemusic(self):
        self.readtime += 1
        if self.play1 & (self.readtime > 3):
            self.play1 = not self.play1
            self.firstplay = False

    # 视频帧显示
    def videoplay(self, image):
        self.screenfull.setPixmap(QtGui.QPixmap(image))

    # 提示玛娜不足
    def lack_mana(self):
        self.reply = QMessageBox(QMessageBox.Information, "提示", "\t    -玛娜不足-\n请重置抽卡次数或者更换卡池文件内容")
        self.reply.addButton('知道了', QMessageBox.YesRole)
        self.reply.addButton('也不是不可以啦', QMessageBox.NoRole)
        self.reply.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.reply.setStyleSheet("""
            QPushButton {
                padding: 5px 5px;
                color:#ffffff;
                border: 2px solid #ff9292;
                border-radius: 2px;
                background-color: #ff9292;
            }
            QLabel{
                font-size: 18px;
                padding: 5px 5px;
                color:#ff9292;
            }
        """)
        font = QtGui.QFont()
        font.setFamily("字魂蜜桃猫体")
        font.setBold(True)
        self.reply.setFont(font)
        self.reply.setIcon(0)
        self.reply.show()

    # 抽卡功能
    def gachicard(self):
        if self.label_2.text() == '0':
            self.lack_mana()
        else:
            global video_status
            video_status = 0
            self.radioButton.setChecked(False)
            self.picdir, self.initpic = npor.gachi_card_out(self.pic, self.count_pic)
            self.Dialogue.show()
            self.Dialogue.show_card(self.picdir)

    # 保存数值
    def save_num(self):
        self.pic = np.delete(self.pic, self.initpic)
        self.count_pic -= 1
        self.label_2.setText(str(self.count_pic))
        np.save('picnum1', self.pic)
        self.radioButton.setChecked(True)
        global video_status
        video_status = 1
        self.Update_v.start()

    # 更新卡池
    def update_card(self):
        self.Dialogue = card_show.card_show()
        self.pic, self.count_pic = npor.renew_num()
        self.label_2.setText(str(self.count_pic))
        self.Dialogue.closed.connect(self.save_num)

    # 初始化卡池
    def init_card(self):
        self.Dialogue = card_show.card_show()
        self.pic, self.count_pic = npor.read_num()
        self.label_2.setText(str(self.count_pic))
        self.Dialogue.closed.connect(self.save_num)

    # 抽卡记录
    def recordit(self):
        self.record_Widget = record_window()
        self.record_Widget.show()
        self.record_Widget.print_record()

    def tipit(self):
        self.tip_widget = operator_tip_use.tip_window()
        self.tip_widget.show()

    # ✅【修复】签到函数 —— 已经放进类里面了！
    def open_sign_dialog(self):
        dialog = SignDialog(self)
        dialog.exec_()

    # 拖拽功能
    def mousePressEvent(self, e):
        global video_status
        video_status = 2
        self.__dragWin = True
        self.__dragWin_x = e.x()
        self.__dragWin_y = e.y()
        self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, e):
        if self.__dragWin == True:
            pos = e.globalPos()
            self.move(pos.x() - self.__dragWin_x, pos.y() - self.__dragWin_y)

    def mouseReleaseEvent(self, e):
        global video_status
        video_status = 1
        self.__dragWin = False
        self.setCursor(QCursor(Qt.ArrowCursor))

# 多线程
class Update(QThread):
    date1 = pyqtSignal()
    def __init__(self):
        super(Update, self).__init__()
    def run(self):
        while True:
            time.sleep(0.1)
            self.date1.emit()

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