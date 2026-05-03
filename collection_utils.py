import os
import sqlite3
from PIL import Image

CONFIG = {
    "DEFAULT_CARD_IMG_DIR": "card_images/",
    "DEFAULT_PLACEHOLDER": "unlocked_placeholder.png",
    "DEFAULT_ERROR_IMG": "default_error.png"
}

def get_user_collection(username):
    try:
        conn = sqlite3.connect("game_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT card_name FROM collection WHERE username=?", (username,))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except:
        return []

def get_card_image_path(card_id, owned_cards, card_img_dir=None, placeholder_img=None):
    card_img_dir = card_img_dir or CONFIG["DEFAULT_CARD_IMG_DIR"]
    placeholder_img = placeholder_img or CONFIG["DEFAULT_PLACEHOLDER"]
    
    if card_id in owned_cards:
        img_path = os.path.join(card_img_dir, f"{card_id}.png")
        if not os.path.exists(img_path):
            img_path = placeholder_img
    else:
        img_path = placeholder_img
    return img_path

def load_card_image(img_path, error_img=None):
    error_img = error_img or CONFIG["DEFAULT_ERROR_IMG"]
    try:
        if os.path.exists(img_path):
            return Image.open(img_path).convert("RGBA")
        elif os.path.exists(error_img):
            return Image.open(error_img).convert("RGBA")
        else:
            return None
    except:
        return None