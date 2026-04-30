# collection_utils.py
import numpy as np
import os
from PIL import Image

def load_received_cards(npy_path="receive_card.npy"):
    """读取已获得的卡牌列表（兼容npy文件不存在的情况）"""
    if os.path.exists(npy_path):
        received_cards = np.load(npy_path, allow_pickle=True).tolist()
    else:
        received_cards = []
        np.save(npy_path, received_cards)  # 初始化空文件
    return received_cards

def get_card_image_path(card_id, received_cards, card_img_dir="card_images/", placeholder_img="unlocked_placeholder.png"):
    """根据卡牌状态返回对应图片路径"""
    if card_id in received_cards:
        img_path = os.path.join(card_img_dir, f"{card_id}.png")
        # 兜底：若卡牌原图缺失，仍显示占位图
        if not os.path.exists(img_path):
            img_path = placeholder_img
    else:
        img_path = placeholder_img
    return img_path

def load_card_image(img_path, error_img="default_error.png"):
    """加载图片（兼容图片缺失）"""
    if os.path.exists(img_path):
        return Image.open(img_path)
    elif os.path.exists(error_img):
        return Image.open(error_img)
    else:
        # 无兜底图时返回空
        return None