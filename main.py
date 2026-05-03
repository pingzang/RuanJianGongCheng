# code:utf-8
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import QCursor
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QProgressBar, QLabel
from datetime import datetime
import sys
import numpy as np
import cv2
import time
import sqlite3
import random
import os
from card_pool import CARD_POOL, GACHA_PROB, PITY_GUARANTEE
from main_ui import MainUI
import card_show
from showrecord import record_window
from sign_ui import SignDialog
from stats_window import StatsWindow
from login_window import LoginWindow
from collection_window import CollectionWindow

DB_NAME = "game_data.db"

# ======================封面动画========================
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(1000, 600)
        self.setStyleSheet("background-color: black;")

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 1000, 600)
        self.label.setScaledContents(True)
        self.cap = cv2.VideoCapture("game.mp4")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)

        self.music_player = QMediaPlayer()
        self.music_player.setMedia(QMediaContent(QUrl.fromLocalFile("gamebgm.mp3")))
        self.music_player.setVolume(60)
        self.music_player.play()
        self.music_player.mediaStatusChanged.connect(
            lambda s: self.music_player.play() if s == QMediaPlayer.EndOfMedia else None
        )
        self.show()

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qimg))

    def mousePressEvent(self, event):
        self.close_all()

    def keyPressEvent(self, event):
        self.close_all()

    def close_all(self):
        self.timer.stop()
        self.cap.release()
        self.music_player.stop()
        self.close()

# ======================主界面========================
class card_func(QMainWindow):
    def __init__(self, username=None):
        super().__init__()
        self.username = username
        self.ui = MainUI()
        self.setCentralWidget(self.ui)

        # 按钮音效
        self.sound_player = QMediaPlayer()
        self.button_sound_path = "button.mp3"
        if not os.path.exists(self.button_sound_path):
            QMessageBox.warning(self, "提示", "未找到button.mp3音效文件，按钮点击无音效！")

        #初始化
        self.init_ui()
        self.gacha_coin = self.get_user_coin()
        self.pity = self.get_pity_count()
        self.music_on = True
        self.init_video()

        self.Dialogue = card_show.card_show()
        self.Dialogue.closed.connect(self.post_gacha)
        self.Dialogue.showEvent = lambda e: self.pause_bgm() # 抽卡窗口打开时暂停背景音乐
        self.Dialogue.resume_bgm.connect(self.resume_bgm) # 抽卡窗口关闭时恢复背景音乐

        self.bgm_player = QMediaPlayer()
        self.bgm_player.setVolume(40)
        bgm_url = QUrl.fromLocalFile("bgm.mp3")
        if not bgm_url.isValid() or not QFile.exists("bgm.mp3"):
            QMessageBox.warning(self, "提示", "未找到bgm.mp3文件，背景音乐无法播放！")
        else:
            self.bgm_player.setMedia(QMediaContent(bgm_url))
            self.bgm_player.play()
        self.bgm_player.mediaStatusChanged.connect(self._loop_bgm)

        self.stats_window = None
        self.ui.coin_label.setText(f"✨祈愿币：{self.gacha_coin}")
        self.setWindowTitle("Cat Wisher")

        # 按钮功能绑定
        self.ui.btn_1.clicked.connect(self.gachicard)
        self.ui.btn_record.clicked.connect(self.recordit)
        self.ui.btn_collection.clicked.connect(self.open_collection)
        self.ui.btn_stats.clicked.connect(self.open_stats)
        self.ui.btn_sign.clicked.connect(self.open_sign_dialog)
        self.ui.music_btn.toggled.connect(self.switch_music)
        self.ui.btn_free_coin.clicked.connect(self.open_free_coin_dialog)

        # 按钮音效绑定
        self.ui.btn_1.clicked.connect(self.play_button_sound)
        self.ui.btn_record.clicked.connect(self.play_button_sound)
        self.ui.btn_collection.clicked.connect(self.play_button_sound)
        self.ui.btn_stats.clicked.connect(self.play_button_sound)
        self.ui.btn_sign.clicked.connect(self.play_button_sound)
        self.ui.btn_free_coin.clicked.connect(self.play_button_sound)

        # 顶部用户名+保底文字
        self.user_label = QLabel(self)
        self.user_label.setStyleSheet("color: #ffffff; font-size:15px; font-weight: bold;")
        self.user_label.setText(f"当前用户：{self.username if self.username else '游客'}")
        self.user_label.adjustSize()

        self.pity_label = QLabel(self)
        self.pity_label.setStyleSheet("color: gold; font-size:15px;")
        self.pity_label.adjustSize()
        
        self.refresh_pity_ui() # 顶部居中
    
    def pause_bgm(self): #暂停背景音乐
        if self.music_on and self.bgm_player.state() == QMediaPlayer.PlayingState:
            self.bgm_player.pause()

    def resume_bgm(self): #恢复背景音乐
        if self.music_on and self.bgm_player.state() == QMediaPlayer.PausedState:
            self.bgm_player.play()

    def open_free_coin_dialog(self):
        ok = QMessageBox.question(self, "免费领币", "观看15秒广告获得1枚祈愿币",
                                QMessageBox.Ok | QMessageBox.Cancel)
        if ok != QMessageBox.Ok:
            return

        # 暂停音乐
        self.old_volume = self.bgm_player.volume()
        self.bgm_player.setVolume(0)

        self.ad = AdWindow(self)
        self.ad.ad_finished.connect(self.on_ad_finished)
        self.ad.show()

    def on_ad_finished(self, success):
        # 恢复音乐
        self.bgm_player.setVolume(self.old_volume)

        if success:
            self.gacha_coin += 1
            self.update_user_coin(self.gacha_coin)
            self.ui.coin_label.setText(f"✨祈愿币：{self.gacha_coin}")
            QMessageBox.information(self, "成功", "恭喜获得1枚祈愿币！")
        else:
            QMessageBox.warning(self, "提示", "未完成广告，无法领取奖励")

    # 播放按钮音效方法
    def play_button_sound(self):
        """播放按钮点击音效"""
        if not os.path.exists(self.button_sound_path):
            return
        # 每次播放前重置播放器状态，避免音效重叠
        self.sound_player.stop()
        sound_url = QUrl.fromLocalFile(self.button_sound_path)
        self.sound_player.setMedia(QMediaContent(sound_url))
        self.sound_player.setVolume(50)  #音量
        self.sound_player.play()

    def refresh_pity_ui(self):
        from card_pool import PITY_GUARANTEE
        current = self.pity
        total = PITY_GUARANTEE

        self.pity_label.setText(f"保底：{current}/{total}")
        self.user_label.adjustSize()
        self.pity_label.adjustSize()

        # 顶部水平居中
        total_width = self.user_label.width() + 18 + self.pity_label.width()
        start_x = (self.width() - total_width) // 2

        self.user_label.move(start_x, 12)
        self.pity_label.move(start_x + self.user_label.width() + 18, 12)

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(1000, 600)
        self.ui.close_btn.clicked.connect(self.close)
        self.ui.min_btn.clicked.connect(self.showMinimized)
        self.ui.music_btn.setChecked(True)
        self.ui.music_btn.setText("🔊 音乐开启")

    def get_user_coin(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT coin FROM users WHERE username=?", (self.username,))
        res = cur.fetchone()
        conn.close()
        return res[0] if res else 100

    def get_pity_count(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT count FROM pity_count WHERE username=?", (self.username,))
        res = cur.fetchone()
        if not res:
            cur.execute("INSERT INTO pity_count (username, count) VALUES (?, 0)", (self.username,))
            conn.commit()
            res = (0,)
        conn.close()
        return res[0] if res else 0

    def update_pity_count(self, new_count):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("REPLACE INTO pity_count (username, count) VALUES (?, ?)", (self.username, new_count))
        conn.commit()
        conn.close()

    def update_user_coin(self, new_coin):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("UPDATE users SET coin = ? WHERE username = ?", (new_coin, self.username))
        conn.commit()
        conn.close()

    def save_gacha_record(self, card_info):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO gacha_history (username, draw_time, draw_type, card_name, card_star, card_color)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.username,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "单抽",
            card_info["name"],
            card_info["star"],
            card_info["color"]
        ))
        cur.execute("""
            INSERT OR IGNORE INTO collection (username, card_name, card_star, card_color)
            VALUES (?, ?, ?, ?)
        """, (self.username, card_info["name"], card_info["star"], card_info["color"]))
        cur.execute("SELECT total_draw, ssr_count FROM gacha_stat WHERE username=?", (self.username,))
        stat = cur.fetchone()
        if stat:
            total = stat[0] + 1
            ssr = stat[1] + (1 if card_info["star"] == 5 else 0)
            cur.execute("""
                UPDATE gacha_stat SET total_draw = ?, ssr_count = ? WHERE username = ?
            """, (total, ssr, self.username))
        else:
            cur.execute("""
                INSERT INTO gacha_stat (username, total_draw, ssr_count)
                VALUES (?, 1, ?)
            """, (self.username, 1 if card_info["star"] == 5 else 0))
        conn.commit()
        conn.close()

    def switch_music(self):
        if self.music_on:
            self.bgm_player.setVolume(0)
            self.music_on = False
            self.ui.music_btn.setText("🔇 音乐关闭")
        else:
            self.bgm_player.setVolume(40)
            self.music_on = True
            self.ui.music_btn.setText("🔊 音乐开启")

    def init_video(self):
        self.video_thread = VideoThread()
        self.video_thread.video_signal.connect(self.show_video_frame)
        self.video_thread.start()

    def show_video_frame(self, img):
        self.ui.center_label.setPixmap(QtGui.QPixmap.fromImage(img))

    def _loop_bgm(self, status):
        from PyQt5.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.EndOfMedia:
            self.bgm_player.setPosition(0)
            self.bgm_player.play()

    def gachicard(self):
        if self.gacha_coin < 1:
            QMessageBox.warning(self, "提示", "祈愿币不足，无法抽卡！")
            return

        current_pity = self.pity + 1
        card_star = None

        if current_pity >= PITY_GUARANTEE:
            card_star = 5
            current_pity = 0
        else:
            rand = random.random()
            prob_sum = 0
            for star, prob in GACHA_PROB.items():
                prob_sum += prob
                if rand <= prob_sum:
                    card_star = star
                    break
        if card_star == 5:
            current_pity = 0

        card_list = CARD_POOL[card_star]
        selected_card = random.choice(card_list)
        self.picdir = selected_card["pic_path"]

        self.gacha_coin -= 1
        self.update_user_coin(self.gacha_coin)
        self.update_pity_count(current_pity)
        self.pity = current_pity

        self.save_gacha_record(selected_card)
        # 暂停BGM
        self.pause_bgm()
        self.Dialogue.show_card(self.picdir)
        self.refresh_pity_ui()

    def post_gacha(self):
        self.ui.coin_label.setText(f"✨祈愿币：{self.gacha_coin}")

    def recordit(self):
        self.record_win = record_window()
        self.record_win.show()
        self.record_win.print_record(self.username)

    def open_stats(self):
        self.stats_win = StatsWindow(self.username)
        self.stats_win.show()

    def open_sign_dialog(self):
        dialog = SignDialog(self.username, self)
        dialog.exec_()
        self.gacha_coin = self.get_user_coin()
        self.ui.coin_label.setText(f"✨祈愿币：{self.gacha_coin}")

    def open_collection(self):
        self.collect = CollectionWindow(self.username)
        self.collect.show()

    # ===================== 窗口拖拽 =====================
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.__drag = True
            self.__drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self.__drag:
            self.move(e.globalPos() - self.__drag_pos)
            self.refresh_pity_ui()

    def mouseReleaseEvent(self, e):
        self.__drag = False

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
                qt_image = qt_image.scaled(1000, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.video_signal.emit(qt_image)
                time.sleep(0.033)
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# ===================== 广告窗口 =====================
class AdWindow(QWidget):
    ad_finished = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(1000, 600)
        self.is_ad_completed = False
        self.countdown = 15

        # 视频显示
        self.video_label = QLabel(self)
        self.video_label.setGeometry(0, 0, 1000, 600)
        self.video_label.setScaledContents(True)

        # 倒计时标签
        self.count_label = QLabel(self)
        self.count_label.setStyleSheet("""
            QLabel {
                color:white; 
                font-size:26px; 
                font-weight:bold;
                background:rgba(0,0,0,0.8); 
                padding:10px 22px; 
                border-radius:10px;
            }
        """)
        self.count_label.setMinimumWidth(300)
        self.count_label.move(20, 20)

        # 关闭按钮
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background:#ff4444; 
                color:white; 
                font-size:22px;
                padding:8px 16px; 
                border-radius:10px;
            }
            QPushButton:hover {
                background:#ff0000;
            }
        """)
        self.close_btn.clicked.connect(self.try_close)
        self.close_btn.move(880, 20)

        # 视频播放（OpenCV）
        self.cap = cv2.VideoCapture("nibeipianle.mp4")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.delay = int(1000 / self.fps)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(self.delay)

        # 音频
        self.ad_sound = QMediaPlayer()
        self.ad_sound.setMedia(QMediaContent(QUrl.fromLocalFile("ad_audio.mp3")))
        self.ad_sound.setVolume(80)
        self.ad_sound.play()

        # 倒计时
        self.count_timer = QTimer()
        self.count_timer.timeout.connect(self.update_countdown)
        self.count_timer.start(1000)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        q_img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def update_countdown(self):
        if self.countdown > 0:
            self.count_label.setText(f"广告剩余时间：{self.countdown}s")
            self.countdown -= 1
        else:
            self.is_ad_completed = True
            self.count_label.setText(" 广告已完成 ")
            self.count_timer.stop()

    def try_close(self):
        self.timer.stop()
        self.count_timer.stop()
        self.cap.release()
        self.ad_sound.stop()

        if self.is_ad_completed:
            self.ad_finished.emit(True)
        else:
            res = QMessageBox.question(self, "提示", "未看完广告将无法获得奖励，确认关闭吗？")
            if res == QMessageBox.Yes:
                self.ad_finished.emit(False)
            else:
                self.cap.open("nibeipianle.mp4")
                self.timer.start(self.delay)
                self.count_timer.start(1000)
                self.ad_sound.play()
                return

        self.close()

    def closeEvent(self, e):
        self.timer.stop()
        self.count_timer.stop()
        self.cap.release()
        self.ad_sound.stop()
        e.accept()

# ===================== 程序入口 =====================
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 启动动画
    splash = SplashScreen()
    app.exec_()

    # 登录
    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:
        global main_window
        main_window = card_func(username=login.current_user)
        main_window.show()

        sys.exit(app.exec_())