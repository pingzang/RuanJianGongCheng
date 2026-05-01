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
<<<<<<< HEAD
import operator_tip_use
from sign_ui import SignDialog

class card_func(QMainWindow, Ui_getcard):
=======
from stats_window import StatsWindow
>>>>>>> dca73ab852199a700a3a4ce677164ee5f5bcf7c9

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
        
        # ===================== 按钮绑定 =====================
        self.ui.btn_1.clicked.connect(self.gachicard)        #单抽
        self.ui.btn_record.clicked.connect(self.recordit)    #抽卡记录
        self.ui.btn_collection.clicked.connect(self.open_collection) #图鉴
        self.ui.btn_stats.clicked.connect(self.open_stats)   #抽卡统计
        self.ui.btn_reset.clicked.connect(self.update_card)  #重置祈愿币/卡池
        self.ui.music_btn.toggled.connect(self.toggle_music) #音乐开关

<<<<<<< HEAD
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
=======
    # ===================== 窗口初始化 =====================
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)         #隐藏窗口栏
        self.setFixedSize(1000, 600)
        self.ui.close_btn.clicked.connect(self.close)
        self.ui.min_btn.clicked.connect(self.showMinimized)
        self.ui.music_btn.setChecked(True)  # 默认开启音乐
>>>>>>> dca73ab852199a700a3a4ce677164ee5f5bcf7c9

    # ===================== 单个音频循环播放 =====================
    def init_audio(self):
        self.bgm = QMediaPlayer()
        self.bgm.setMedia(QMediaContent(QUrl.fromLocalFile("bgm.mp3")))
        self.bgm.setVolume(60)
        self.bgm.play()  # 启动就播放

<<<<<<< HEAD
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
=======
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
>>>>>>> dca73ab852199a700a3a4ce677164ee5f5bcf7c9
        self.pic, self.count_pic = npor.read_num()
        print(f"卡池加载完成：共{len(self.pic)}张卡，当前祈愿币：{self.count_pic}")
        self.ui.mana_label.setText(f"✨祈愿币：{self.count_pic}")
        self.Dialogue.closed.connect(self.save_num)

<<<<<<< HEAD
    # 抽卡记录
=======
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
>>>>>>> dca73ab852199a700a3a4ce677164ee5f5bcf7c9
    def recordit(self):
        self.record_win = record_window()
        self.record_win.show()
        self.record_win.print_record()

    def open_stats(self):
        self.stats_win = StatsWindow()
        self.stats_win.show()

<<<<<<< HEAD
    # ✅【修复】签到函数 —— 已经放进类里面了！
    def open_sign_dialog(self):
        dialog = SignDialog(self)
        dialog.exec_()
=======
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
>>>>>>> dca73ab852199a700a3a4ce677164ee5f5bcf7c9

    # 拖拽功能
    def mousePressEvent(self, e):
<<<<<<< HEAD
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
=======
        self.drag = True
        self.x = e.x()
        self.y = e.y()

    def mouseMoveEvent(self, e):
        if self.drag:
            self.move(e.globalPos().x() - self.x, e.globalPos().y() - self.y)
>>>>>>> dca73ab852199a700a3a4ce677164ee5f5bcf7c9

    def mouseReleaseEvent(self, e):
        self.drag = False

<<<<<<< HEAD
# 多线程
class Update(QThread):
    date1 = pyqtSignal()
    def __init__(self):
        super(Update, self).__init__()
=======
# ===================== 视频线程 =====================
class VideoThread(QThread):
    video_signal = pyqtSignal(QtGui.QImage)

>>>>>>> dca73ab852199a700a3a4ce677164ee5f5bcf7c9
    def run(self):
        cap = cv2.VideoCapture("01.mp4")
        while True:
<<<<<<< HEAD
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
=======
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
>>>>>>> dca73ab852199a700a3a4ce677164ee5f5bcf7c9
    sys.exit(app.exec_())